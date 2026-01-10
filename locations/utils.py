import json
import xml.etree.ElementTree as ET
from datetime import datetime
from django.utils import timezone
from .models import LocationBatch, Place
import zipfile
import io
import pytz
    
def parse_e7(value):
    """Converts Google's E7 integer format to float degrees."""
    if value is None:
        return 0.0
    return float(value) / 1e7

def parse_timeline_json(batch, file_content):
    """
    Parses Google Semantic Location History JSON.
    Expected structure: { "timelineObjects": [ { "placeVisit": { ... } }, ... ] }
    """
    if not file_content:
        raise ValueError("The uploaded file is empty or invalid.")

    try:
        # Try decoding with UTF-8 first
        content_str = file_content.decode('utf-8')
    except UnicodeDecodeError:
        # If UTF-8 fails, try latin-1
        content_str = file_content.decode('latin-1')
        
    if not content_str.strip():
        raise ValueError("The uploaded file contains only whitespace.")

    if content_str.strip().startswith('<'):
        raise ValueError("The file appears to be an XML/KML file, but 'timeline' (JSON) was selected. Please select the correct file type.")

    if not content_str.strip().startswith('{'):
        raise ValueError("The file does not appear to be a valid timeline JSON file. It should start with '{'.")
        
    data = json.loads(content_str)
    
    places_to_create = []
    
    if 'timelineObjects' in data:
        # Handle Semantic Location History format
        objects = data.get('timelineObjects', [])
        for obj in objects:
            if 'placeVisit' in obj:
                visit = obj['placeVisit']
                location = visit.get('location', {})
                duration = visit.get('duration', {})
                start_ts, end_ts = None, None
                if 'startTimestamp' in duration:
                    start_ts = datetime.fromisoformat(duration['startTimestamp'].replace('Z', '+00:00'))
                if 'endTimestamp' in duration:
                    end_ts = datetime.fromisoformat(duration['endTimestamp'].replace('Z', '+00:00'))

                places_to_create.append(Place(
                    batch=batch,
                    name=location.get('name', 'Unknown Place'),
                    latitude=parse_e7(location.get('latitudeE7')),
                    longitude=parse_e7(location.get('longitudeE7')),
                    place_id=location.get('placeId'),
                    address=location.get('address'),
                    confidence=visit.get('visitConfidence'),
                    timestamp=start_ts,
                    duration_start=start_ts,
                    duration_end=end_ts
                ))
    elif 'locations' in data:
        # Handle raw Location History format
        for loc in data['locations']:
            ts_ms = int(loc.get('timestampMs', 0))
            timestamp = datetime.fromtimestamp(ts_ms / 1000, tz=pytz.utc) if ts_ms else timezone.now()
            
            places_to_create.append(Place(
                batch=batch,
                name=f"Location at {timestamp.strftime('%Y-%m-%d %H:%M')}",
                latitude=parse_e7(loc.get('latitudeE7')),
                longitude=parse_e7(loc.get('longitudeE7')),
                timestamp=timestamp
            ))
    else:
        raise ValueError("JSON file is not a recognized Google Timeline format (missing 'timelineObjects' or 'locations' key).")
        
    if not places_to_create:
        # This can happen if the file is valid but contains no relevant data (e.g., only activitySegments)
        raise ValueError("No place data found in the uploaded file.")

    Place.objects.bulk_create(places_to_create)

def parse_kml(batch, file_content):
    """
    Parses generic KML/KMZ files (like those from Google My Maps).
    """
    if not file_content:
        raise ValueError("The uploaded file is empty or invalid.")

    kml_content = None
    try:
        # Attempt to open as a KMZ (zip) file
        with zipfile.ZipFile(io.BytesIO(file_content), 'r') as kmz:
            # Look for the main KML file, typically doc.kml or the first .kml file
            kml_filenames = [name for name in kmz.namelist() if name.lower().endswith('.kml')]
            if kml_filenames:
                # Prefer 'doc.kml' if it exists, otherwise take the first one
                main_kml_file = 'doc.kml' if 'doc.kml' in kml_filenames else kml_filenames[0]
                kml_content = kmz.read(main_kml_file)
            else:
                raise ValueError("No KML file found inside the KMZ archive.")
    except zipfile.BadZipFile:
        # Not a zip file, so treat as a direct KML file
        kml_content = file_content
    except Exception as e:
        raise ValueError(f"Error processing KMZ file: {e}")


    try:
        # Try decoding with UTF-8 first
        xml_string = kml_content.decode('utf-8')
    except UnicodeDecodeError:
        # If UTF-8 fails, try latin-1
        xml_string = kml_content.decode('latin-1')
    if not xml_string.strip():
        raise ValueError("The uploaded file contains only whitespace.")

    if xml_string.strip().startswith('{'):
        raise ValueError("The file appears to be a JSON file, but 'mymaps' (KML) was selected. Please select the correct file type.")

    stripped_content = xml_string.strip()
    if not (stripped_content.startswith('<?xml') or stripped_content.startswith('<kml')):
        raise ValueError("The file does not appear to be a valid KML file. It should start with '<?xml' or '<kml>'.")
        
    # Basic namespace stripping
    xml_string = xml_string.replace('xmlns="http://www.opengis.net/kml/2.2"', '')
    
    root = ET.fromstring(xml_string)
    places_to_create = []

    # Find all Placemarks
    for placemark in root.findall('.//Placemark'):
        name = placemark.find('name').text if placemark.find('name') is not None else "Unnamed"
        
        # Extract coordinates
        point = placemark.find('.//Point/coordinates')
        if point is not None:
            coords = point.text.strip().split(',')
            lon = float(coords[0])
            lat = float(coords[1])
            
            places_to_create.append(Place(
                batch=batch,
                name=name,
                latitude=lat,
                longitude=lon,
                timestamp=timezone.now() # KML often doesn't have timestamps for static maps
            ))

    Place.objects.bulk_create(places_to_create)

def parse_saved_places_json(batch, file_content):
    """
    Parses Google Takeout 'Saved Places.json' (GeoJSON format).
    """
    if not file_content:
        raise ValueError("The uploaded file is empty or invalid.")

    try:
        content_str = file_content.decode('utf-8')
    except UnicodeDecodeError:
        content_str = file_content.decode('latin-1')

    if not content_str.strip():
        raise ValueError("The uploaded file contains only whitespace.")

    if not content_str.strip().startswith('{'):
        raise ValueError("The file does not appear to be a valid JSON file.")

    data = json.loads(content_str)
    features = data.get('features', [])
    
    if data.get('type') != 'FeatureCollection' or not features:
        raise ValueError("The file does not appear to be a valid 'Saved Places' GeoJSON file.")

    places_to_create = []

    for feature in features:
        if feature.get('type') == 'Feature' and feature.get('geometry', {}).get('type') == 'Point':
            properties = feature.get('properties', {})
            geometry = feature.get('geometry', {})
            
            name = properties.get('location', {}).get('name', 'Unknown Place')
            address = properties.get('location', {}).get('address')
            # GeoJSON coordinates are [longitude, latitude]
            lon, lat = geometry.get('coordinates', [0, 0])

            # Timestamp is not usually available in Saved Places, so we use current time
            timestamp = properties.get('date', timezone.now()) 

            places_to_create.append(Place(
                batch=batch,
                name=name,
                latitude=lat,
                longitude=lon,
                address=address,
                timestamp=timestamp
            ))
            
    Place.objects.bulk_create(places_to_create)

def parse_labeled_places_json(batch, file_content):
    """
    Parses Google Takeout 'Labeled places.json' (GeoJSON format).
    """
    if not file_content:
        raise ValueError("The uploaded file is empty or invalid.")

    try:
        content_str = file_content.decode('utf-8')
    except UnicodeDecodeError:
        content_str = file_content.decode('latin-1')

    if not content_str.strip():
        raise ValueError("The uploaded file contains only whitespace.")

    if not content_str.strip().startswith('{'):
        raise ValueError("The file does not appear to be a valid JSON file.")

    data = json.loads(content_str)
    features = data.get('features', [])
    
    if data.get('type') != 'FeatureCollection' or not features:
        raise ValueError("The file does not appear to be a valid 'Labeled Places' GeoJSON file.")

    places_to_create = []

    for feature in features:
        if feature.get('type') == 'Feature' and feature.get('geometry', {}).get('type') == 'Point':
            properties = feature.get('properties', {})
            geometry = feature.get('geometry', {})
            
            name = properties.get('name', 'Unknown Place')
            address = properties.get('address')
            # GeoJSON coordinates are [longitude, latitude]
            lon, lat = geometry.get('coordinates', [0, 0])

            # Timestamp is not usually available in Labeled Places, so we use current time
            timestamp = timezone.now()

            places_to_create.append(Place(
                batch=batch,
                name=name,
                latitude=lat,
                longitude=lon,
                address=address,
                timestamp=timestamp
            ))
            
    Place.objects.bulk_create(places_to_create)

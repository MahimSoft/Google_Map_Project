import json
import os
from django.shortcuts import render, redirect
from .models import MediaItem
from .forms import MediaItemForm
from .utils import get_exif_data
from django.core.files.uploadedfile import InMemoryUploadedFile, UploadedFile
from django.contrib import messages
from datetime import datetime
from django.core.serializers.json import DjangoJSONEncoder # For serializing datetime objects

from .models import Photo


def map_view(request):
    media_items = MediaItem.objects.all()

    places_data = []
    for item in media_items:
        if item.latitude and item.longitude: # Only include items with location data
            places_data.append({
                'latitude': item.latitude,
                'longitude': item.longitude,
                'timestamp': item.timestamp.isoformat() if item.timestamp else None, # ISO format for JS Date parsing
                'name': item.title if item.title else os.path.basename(item.image.name), # Use title or filename
                'icon': 'camera', # Default icon, can be customized
                'color': 'red',   # Default color, can be customized
                'address': '',    # MediaItem does not have an address field
                'comments': '',   # MediaItem does not have an comments field
                'image_url': item.image.url, # URL to display image in popup
            })
    
    # For now, places_by_type will be empty as MediaItem doesn't have a type field
    # If type categorization is needed later, this needs to be extended.
    places_by_type = {}

    places_json = json.dumps(places_data, cls=DjangoJSONEncoder)
    places_by_type_json = json.dumps(places_by_type, cls=DjangoJSONEncoder)

    context = {
        'places_json': places_json,
        'places_by_type_json': places_by_type_json,
        'total_place': len(places_data)
    }
    return render(request, 'gallery/map.html', context) # Render map.html instead of takeout.html


def upload_view(request):
    if request.method == 'POST':
        uploaded_files = request.FILES.getlist('image') # This will contain both images and JSONs if selected together

        images_to_process = {} # Store actual image files
        json_data_map = {}     # Store parsed JSON data, keyed by base image name

        # First pass: Separate images and parse JSON files
        for uploaded_file in uploaded_files:
            name, ext = os.path.splitext(uploaded_file.name)
            if ext.lower() in ('.jpg', '.jpeg', '.png', '.gif'):
                images_to_process[name] = uploaded_file
            elif ext.lower() == '.json':
                try:
                    json_content = json.loads(uploaded_file.read().decode('utf-8'))
                    json_data_map[name] = json_content
                except json.JSONDecodeError as json_e:
                    messages.error(request, f"Error decoding JSON for {uploaded_file.name}: {json_e}")
                except Exception as e:
                    messages.error(request, f"Error processing JSON file {uploaded_file.name}: {e}")

        # Second pass: Process images
        for base_name, image_file in images_to_process.items():
            # Basic validation for image file types (already done implicitly above, but good for safety)
            if not isinstance(image_file, UploadedFile) or not image_file.content_type.startswith('image'):
                messages.error(request, f"Skipping non-image file {image_file.name}. Detected content type: {image_file.content_type}")
                continue

            image_file.seek(0)
            lat, lon, dt = None, None, None # Initialize to None
            
            # 1. Try to get EXIF data
            try:
                lat, lon, dt = get_exif_data(image_file)
            except Exception as e:
                messages.error(request, f"Error processing EXIF data for {image_file.name}: {e}")
                # Continue to JSON check even if EXIF processing fails

            # 2. If no EXIF location data, try companion JSON
            if not (lat and lon):
                json_content = json_data_map.get(image_file.name)
                if json_content:
                    try:
                        geo_data = json_content.get('geoDataExif')
                        if geo_data:
                            lat = geo_data.get('latitude')
                            lon = geo_data.get('longitude')
                        
                        # Try to get timestamp from JSON if dt is still None
                        if not dt:
                            creation_time = json_content.get('creationTime')
                            if creation_time:
                                timestamp_str = creation_time.get('timestamp')
                                if timestamp_str:
                                    # Convert Unix timestamp string to datetime object
                                    dt = datetime.fromtimestamp(int(timestamp_str))
                    except Exception as json_e:
                        messages.error(request, f"Error extracting data from JSON for {image_file.name}: {json_e}")
            
            if lat and lon:
                media_item = MediaItem(latitude=lat, longitude=lon)
                if dt:
                    media_item.timestamp = dt
                media_item.image.save(image_file.name, image_file)
                messages.success(request, f"Successfully uploaded {image_file.name}")
            else:
                messages.warning(request, f"Could not find location data for {image_file.name} from EXIF or companion JSON. Skipping.")

        return redirect('gallery:gallery_map')
    else:
        form = MediaItemForm()
    return render(request, 'gallery/upload.html', {'form': form})

def photo_map(request):
    photos = Photo.objects.exclude(latitude__isnull=True)
    return render(request, 'gallery/map.html', {'photos': photos})
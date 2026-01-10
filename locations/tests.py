from django.test import TestCase
from django.utils import timezone
from .models import LocationBatch, Place
from .utils import parse_kml, parse_timeline_json, parse_saved_places_json, parse_labeled_places_json
import io
import zipfile
import os
import pytz
from datetime import datetime

class LocationUtilsTest(TestCase):
    def setUp(self):
        self.batch = LocationBatch.objects.create(name="Test Batch")

    def test_parse_kml_valid_kml(self):
        kml_content = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>Test KML</name>
    <Placemark>
      <name>Test Place KML</name>
      <Point>
        <coordinates>-74.0060,40.7128,0</coordinates>
      </Point>
    </Placemark>
  </Document>
</kml>"""
        
        parse_kml(self.batch, kml_content.encode('utf-8'))
        
        self.assertEqual(Place.objects.count(), 1)
        place = Place.objects.first()
        self.assertEqual(place.name, "Test Place KML")
        self.assertAlmostEqual(place.latitude, 40.7128)
        self.assertAlmostEqual(place.longitude, -74.0060)
        self.assertEqual(place.batch, self.batch)

    def test_parse_kml_valid_kmz(self):
        kml_string = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>Test KMZ</name>
    <Placemark>
      <name>Test Place KMZ</name>
      <Point>
        <coordinates>10.1234,20.5678,0</coordinates>
      </Point>
    </Placemark>
  </Document>
</kml>"""
        
        # Create an in-memory KMZ file
        kmz_buffer = io.BytesIO()
        with zipfile.ZipFile(kmz_buffer, 'w', zipfile.ZIP_DEFLATED) as kmz_file:
            kmz_file.writestr("doc.kml", kml_string.encode('utf-8'))
        kmz_buffer.seek(0) # Reset buffer position to the beginning
        
        parse_kml(self.batch, kmz_buffer.read())
        
        self.assertEqual(Place.objects.count(), 1)
        place = Place.objects.first()
        self.assertEqual(place.name, "Test Place KMZ")
        self.assertAlmostEqual(place.latitude, 20.5678)
        self.assertAlmostEqual(place.longitude, 10.1234)
        self.assertEqual(place.batch, self.batch)

    def test_parse_kml_empty_file(self):
        with self.assertRaisesMessage(ValueError, "The uploaded file is empty or invalid."):
            parse_kml(self.batch, b"")

    def test_parse_kml_invalid_content(self):
        with self.assertRaisesMessage(ValueError, "The file does not appear to be a valid KML file. It should start with '<?xml' or '<kml>'."):
            parse_kml(self.batch, b"this is not kml content")

    def test_parse_kml_kmz_no_kml_file_inside(self):
        # Create an in-memory KMZ file without any .kml file inside
        kmz_buffer = io.BytesIO()
        with zipfile.ZipFile(kmz_buffer, 'w', zipfile.ZIP_DEFLATED) as kmz_file:
            kmz_file.writestr("not_a_kml.txt", b"some text")
        kmz_buffer.seek(0) # Reset buffer position to the beginning

        with self.assertRaisesMessage(ValueError, "No KML file found inside the KMZ archive."):
            parse_kml(self.batch, kmz_buffer.read())

    # --- Tests for parse_timeline_json (existing functionality, good to have tests) ---
    def test_parse_timeline_json_semantic_location_history(self):
        json_content = """{
            "timelineObjects": [
                {
                    "placeVisit": {
                        "location": {
                            "latitudeE7": 340000000,
                            "longitudeE7": -1180000000,
                            "name": "Semantic Place",
                            "placeId": "ChIJEXAMPLE",
                            "address": "123 Semantic St"
                        },
                        "duration": {
                            "startTimestamp": "2023-01-01T10:00:00.000Z",
                            "endTimestamp": "2023-01-01T11:00:00.000Z"
                        },
                        "visitConfidence": 100
                    }
                }
            ]
        }"""
        parse_timeline_json(self.batch, json_content.encode('utf-8'))
        
        self.assertEqual(Place.objects.count(), 1)
        place = Place.objects.first()
        self.assertEqual(place.name, "Semantic Place")
        self.assertAlmostEqual(place.latitude, 34.0)
        self.assertAlmostEqual(place.longitude, -118.0)
        self.assertEqual(place.place_id, "ChIJEXAMPLE")
        self.assertEqual(place.address, "123 Semantic St")
        self.assertEqual(place.confidence, 100)
        self.assertEqual(place.timestamp, datetime(2023, 1, 1, 10, 0, 0, tzinfo=pytz.utc))
        self.assertEqual(place.duration_start, datetime(2023, 1, 1, 10, 0, 0, tzinfo=pytz.utc))
        self.assertEqual(place.duration_end, datetime(2023, 1, 1, 11, 0, 0, tzinfo=pytz.utc))

    def test_parse_timeline_json_raw_location_history(self):
        json_content = """{
            "locations": [
                {
                    "timestampMs": "1672531200000",
                    "latitudeE7": 350000000,
                    "longitudeE7": -1190000000
                }
            ]
        }"""
        parse_timeline_json(self.batch, json_content.encode('utf-8'))

        self.assertEqual(Place.objects.count(), 1)
        place = Place.objects.first()
        self.assertTrue(place.name.startswith("Location at "))
        self.assertAlmostEqual(place.latitude, 35.0)
        self.assertAlmostEqual(place.longitude, -119.0)
        self.assertEqual(place.timestamp, datetime(2023, 1, 1, 0, 0, 0, tzinfo=pytz.utc))

    def test_parse_timeline_json_empty_file(self):
        with self.assertRaisesMessage(ValueError, "The uploaded file is empty or invalid."):
            parse_timeline_json(self.batch, b"")

    def test_parse_timeline_json_not_json(self):
        with self.assertRaisesMessage(ValueError, "The file appears to be an XML/KML file, but 'timeline' (JSON) was selected. Please select the correct file type."):
            parse_timeline_json(self.batch, b"<kml></kml>")

    def test_parse_timeline_json_unrecognized_format(self):
        with self.assertRaisesMessage(ValueError, "JSON file is not a recognized Google Timeline format (missing 'timelineObjects' or 'locations' key)."):
            parse_timeline_json(self.batch, b'{"some_other_key": []}')

    def test_parse_timeline_json_no_place_data(self):
        with self.assertRaisesMessage(ValueError, "No place data found in the uploaded file."):
            parse_timeline_json(self.batch, b'{"timelineObjects": [{"activitySegment": {}}]}')

    # --- Tests for parse_saved_places_json (existing functionality, good to have tests) ---
    def test_parse_saved_places_json_valid_geojson(self):
        json_content = """{
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [-73.9876, 40.7654]
                    },
                    "properties": {
                        "location": {
                            "name": "Saved Place",
                            "address": "456 Saved St"
                        }
                    }
                }
            ]
        }"""
        parse_saved_places_json(self.batch, json_content.encode('utf-8'))

        self.assertEqual(Place.objects.count(), 1)
        place = Place.objects.first()
        self.assertEqual(place.name, "Saved Place")
        self.assertAlmostEqual(place.latitude, 40.7654)
        self.assertAlmostEqual(place.longitude, -73.9876)
        self.assertEqual(place.address, "456 Saved St")
    
    def test_parse_saved_places_json_empty_file(self):
        with self.assertRaisesMessage(ValueError, "The uploaded file is empty or invalid."):
            parse_saved_places_json(self.batch, b"")

    def test_parse_saved_places_json_not_json(self):
        with self.assertRaisesMessage(ValueError, "The file does not appear to be a valid JSON file."):
            parse_saved_places_json(self.batch, b"not json")
    
    def test_parse_saved_places_json_invalid_geojson_structure(self):
        with self.assertRaisesMessage(ValueError, "The file does not appear to be a valid 'Saved Places' GeoJSON file."):
            parse_saved_places_json(self.batch, b'{"type": "InvalidCollection", "features": []}')

    def test_parse_labeled_places_json_valid_geojson(self):
        json_content = """{
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [-73.1234, 40.5678]
                    },
                    "properties": {
                        "name": "Labeled Place",
                        "address": "123 Labeled St"
                    }
                }
            ]
        }"""
        parse_labeled_places_json(self.batch, json_content.encode('utf-8'))

        self.assertEqual(Place.objects.count(), 1)
        place = Place.objects.first()
        self.assertEqual(place.name, "Labeled Place")
        self.assertAlmostEqual(place.latitude, 40.5678)
        self.assertAlmostEqual(place.longitude, -73.1234)
        self.assertEqual(place.address, "123 Labeled St")
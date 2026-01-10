from exif import Image as ExifImage
from datetime import datetime

# utils.py
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS


def get_exif_data(image_file):
    img = ExifImage(image_file)
    if hasattr(img, "has_exif") and img.has_exif and hasattr(img, 'gps_latitude') and hasattr(img, 'gps_longitude'):
        # Convert DMS to Decimal degrees
        lat = img.gps_latitude
        lon = img.gps_longitude
        
        # Get timestamp
        dt_str = img.get('datetime_original')
        dt_obj = None
        if dt_str:
            try:
                dt_obj = datetime.strptime(dt_str, '%Y:%m:%d %H:%M:%S')
            except ValueError:
                pass

        # Basic conversion logic (Decimal = Degrees + Minutes/60 + Seconds/3600)
        return lat[0] + lat[1]/60 + lat[2]/3600, lon[0] + lon[1]/60 + lon[2]/3600, dt_obj
    return None, None, None


#! Google Photoes  ===============
def get_decimal_from_dms(dms, ref):
    degrees = dms[0]
    minutes = dms[1] / 60.0
    seconds = dms[2] / 3600.0
    if ref in ['S', 'W']:
        return -float(degrees + minutes + seconds)
    return float(degrees + minutes + seconds)

def extract_photo_metadata(image_path):
    with Image.open(image_path) as img:
        exif_data = img._getexif()
        if not exif_data:
            return None, None, None

        decoded_exif = {TAGS.get(tag, tag): value for tag, value in exif_data.items()}
        print(decoded_exif)
        
        # 1. Extract DateTime
        captured_at = None
        date_str = decoded_exif.get("DateTimeOriginal") or decoded_exif.get("DateTime")
        if date_str:
            try:
                # Converts "2023:10:15 14:30:05" to a datetime object
                captured_at = datetime.strptime(date_str, "%Y:%m:%d %H:%M:%S")
            except ValueError:
                pass

        # 2. Extract GPS
        lat, lon = None, None
        gps_info_raw = decoded_exif.get("GPSInfo")
        if gps_info_raw:
            # Map numerical keys to string labels (e.g., 2 -> 'GPSLatitude')
            gps_data = {GPSTAGS.get(t, t): gps_info_raw[t] for t in gps_info_raw}
            
            if "GPSLatitude" in gps_data and "GPSLongitude" in gps_data:
                lat = get_decimal_from_dms(gps_data["GPSLatitude"], gps_data["GPSLatitudeRef"])
                lon = get_decimal_from_dms(gps_data["GPSLongitude"], gps_data["GPSLongitudeRef"])

        return lat, lon, captured_at
    
# print(extract_photo_metadata("D:/takeout 20251226/Takeout/Google Photos/Photos from 2025/20250105_111449.jpg"))
if __name__ == "__main__":
    print(extract_photo_metadata("D:/Google Backup/J7Primo/20180825_143837.jpg"))
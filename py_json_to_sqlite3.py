import json
from datetime import datetime
import sqlite3
import os
from tqdm import tqdm



def setup_database(table_columns, table_name, DB_NAME):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({table_columns})")
    conn.commit()
    return conn

def process_files(source_folder, table_columns, table_name, DB_NAME):
    date_format = "%b %d, %Y, %I:%M:%S %p utc"
    conn = setup_database(table_columns, table_name, DB_NAME)
    cursor = conn.cursor()
    
    # 1. First, collect all JSON file paths to set the progress bar length
    all_json_files = []
    for root, _, files in os.walk(source_folder):
        for file in files:
            if file.endswith('.json'):
                all_json_files.append(os.path.join(root, file))

    print(f"Found {len(all_json_files)} JSON files. Starting extraction...")

    # 2. Process files with a progress bar
    for file_path in tqdm(all_json_files, desc="Processing Photos", unit="file"):
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                
                # FIX: Handle if the file is a list [] or a single object {}
                records = data if isinstance(data, list) else [data]
                
                for item in records:
                    # print("ROOT: ", file_path.split("\\")[-1], "File: ",file_path)
                    # Use .get() on 'item' to avoid AttributeError
                    title = item.get('title')
                    desc = item.get('description')
                    views = int(item.get('imageViews', 0))
                    
                    # Nested extraction
                    c_time = datetime.strptime(item.get('creationTime', {}).get('formatted'), date_format) 
                    p_time =  datetime.strptime(item.get('photoTakenTime', {}).get('formatted'), date_format)
                    
                    geo = item.get('geoData', {})
                    lat = geo.get('latitude')
                    lon = geo.get('longitude')
                    alt = geo.get('altitude')
                    
                    people_list = item.get('people', [])
                    # Safely extract names if they exist
                    people_names = ", ".join([p.get('name', 'Unknown') for p in people_list if isinstance(p, dict)])
                    image = f"{REMARKS}/Google Photos/{file_path.split('/')[-1].split("\\")[0]}/{item.get('title')}"
                    url = item.get('url')
                    origin = item.get('googlePhotosOrigin', {}).get('mobileUpload', {})
                    folder = origin.get('deviceFolder', {}).get('localFolderName')
                    device = origin.get('deviceType')
                    remarks = REMARKS
                    
                    # Insert into Database
                    table_columns_names = table_columns.replace("\n","").split(",")
                    table_columns_names = [col.strip().split(" ")[0] for col in table_columns_names]
                    qry =f"""
                        INSERT INTO {table_name} {tuple(table_columns_names[1:])}
                        VALUES ({'?, ' * (len(table_columns_names)-2)}?)
                    """
                    # print(qry)
                    cursor.execute(qry, (title, desc, views, c_time, p_time, lat, lon, alt, people_names, image, url, folder, device, remarks))
                
            except (json.JSONDecodeError, AttributeError, TypeError) as e:
                # Silently skip or log errors for corrupt/mismatched files
                print(f"Skipping {file_path}: {e}")
                continue

    conn.commit()
    conn.close()
    print("\nExtraction complete! Database saved as " + DB_NAME)
    
# Configuration
SOURCE_FOLDER = 'D:/takeout 20251226/Mahimsoft/Google Photos/'
DB_NAME = 'Mahimsoft.sqlite3'
REMARKS = 'Mahimsoft'
table_columns = """id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    title TEXT,
                    description TEXT,
                    image_views INTEGER,
                    creation_time TEXT, 
                    photo_taken_time TEXT, 
                    latitude REAL, 
                    longitude REAL, 
                    altitude REAL, 
                    people TEXT, 
                    image TEXT, 
                    url TEXT, 
                    local_folder TEXT, 
                    device_type TEXT, 
                    remarks TEXT"""
                    
table_name="locations_googlephotos"

#! To Run: python py_json_to_sqlite3.py

if __name__ == "__main__":
    process_files(source_folder = SOURCE_FOLDER, table_columns = table_columns, table_name=table_name, DB_NAME=DB_NAME)
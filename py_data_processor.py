import json
from datetime import datetime
import sqlite3
import os
from tqdm import tqdm
from locations.decorators import time_of_execution
from py_copy_delete_file import copy_file, delete_file
from py_delete_data_from_table import delete_data_from_table
from py_data_base_update_query import update_data, query_list
from py_person_data import populate_data_in_person_table
from py_display import display
from py_heic_relevant_mp4_data import data_insertion_for_converted_mp4
from py_create_video_thumbnail import process_all_thumbnails
from py_convert_videos import convert_to_mp4
from dotenv import dotenv_values, load_dotenv

config = {**dotenv_values(".env")} 

def setup_database(table_columns, table_name, DB_NAME):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({table_columns})")
    conn.commit()
    return conn

@time_of_execution
def process_files(source_folder, table_columns, table_name, DB_NAME, REMARKS):
    date_format = "%b %d, %Y, %I:%M:%S %p utc"
    conn = setup_database(table_columns, table_name, DB_NAME)
    cursor = conn.cursor()
    
    # 1. First, collect all JSON file paths to set the progress bar length
    all_json_files = []
    for root, _, files in os.walk(source_folder):
        for file in files:
            if file.endswith('.json'):
                all_json_files.append(os.path.join(root, file))
    display(text="Starting extraction...", query=False, mysql=False, leading_text=f"Found {len(all_json_files)} JSON files", border=False)
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
    display(text=f"Extraction complete! Database saved as {DB_NAME}", query=False, mysql=False, leading_text="", border=False)
    
# Configuration
DB_NAME_main = 'map_db.sqlite3'
root_folder =config["MEDIA_ROOT"]
folder_1 ="MasudJGTDSL"
folder_2 ="33a33a33a"
folder_3 ="Mahimsoft"
copy_bd_source = r"F:\Takeout\Google_Map_Project\map_db.sqlite3"
copy_bd_destination = rf"F:\Takeout\Google_Map_Project\map_db_backup_{str(datetime.now().strftime('%Y%m%d%H%M%S'))}.sqlite3"


SOURCE_FOLDER_1 = f'{root_folder}/{folder_1}/Google Photos/'
SOURCE_FOLDER_2 = f'{root_folder}/{folder_2}/Google Photos/'
SOURCE_FOLDER_3 = f'{root_folder}/{folder_3}/Google Photos/'

DEST_VIDEO_FOLDER_1 = f'{root_folder}/{folder_1}/Google Photos/MP4'
DEST_VIDEO_FOLDER_2 = f'{root_folder}/{folder_2}/Google Photos/MP4'
DEST_VIDEO_FOLDER_3 = f'{root_folder}/{folder_3}/Google Photos/MP4'

REMARKS_1 = folder_1
REMARKS_2 = folder_2
REMARKS_3 = folder_3

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
                    
table_name_googlephotos="locations_googlephotos"

table_peoplenames="locations_peoplenames"
table_peoplenamesvideos="locations_peoplenamesvideos"
columns_person_image_video = " name TEXT, num_of_images INTEGER "
columns_person_videos = " name TEXT, num_of_videos INTEGER "

query_image_video = """SELECT people FROM locations_googlephotos WHERE length(people) > 0"""

query_video="""SELECT people FROM locations_googlephotos WHERE length(people) > 0 
and (
title like '%.mp4' 
or title like '%.MOV' 
or title like '%.MTS' 
or title like '%.3gp' 
or title like '%.3GP' 
or title like '%.MPO' 
or title like '%.wmv' 
or title like '%.AVI' 
or title like '%.MP4' 
)"""

#! To Run: python py_data_processor.py
if __name__ == "__main__":
    copy_file(copy_bd_source,copy_bd_destination,entire_folder=False)
    delete_data_from_table(table_name=table_name_googlephotos, DB_NAME=DB_NAME_main)
    
    process_files(source_folder = SOURCE_FOLDER_1, 
                  table_columns = table_columns, 
                  table_name=table_name_googlephotos, DB_NAME=DB_NAME_main, REMARKS=REMARKS_1)
    process_files(source_folder = SOURCE_FOLDER_2, 
                  table_columns = table_columns, 
                  table_name=table_name_googlephotos, DB_NAME=DB_NAME_main, REMARKS=REMARKS_2)
    process_files(source_folder = SOURCE_FOLDER_3, 
                  table_columns = table_columns, 
                  table_name=table_name_googlephotos, DB_NAME=DB_NAME_main, REMARKS=REMARKS_3)
    
    convert_to_mp4(input_root=SOURCE_FOLDER_1, output_root=DEST_VIDEO_FOLDER_1)
    convert_to_mp4(input_root=SOURCE_FOLDER_2, output_root=DEST_VIDEO_FOLDER_2)
    convert_to_mp4(input_root=SOURCE_FOLDER_3, output_root=DEST_VIDEO_FOLDER_3)
    
    data_insertion_for_converted_mp4(input_root=SOURCE_FOLDER_1, db_name=DB_NAME_main)
    data_insertion_for_converted_mp4(input_root=SOURCE_FOLDER_2, db_name=DB_NAME_main)
    data_insertion_for_converted_mp4(input_root=SOURCE_FOLDER_3, db_name=DB_NAME_main)
    
    # update Tables ======
    update_data(db_name=DB_NAME_main, query_list=query_list)
    
    # Person Tables ======
    delete_data_from_table(table_name=table_peoplenames, DB_NAME=DB_NAME_main)
    delete_data_from_table(table_name=table_peoplenamesvideos, DB_NAME=DB_NAME_main)
    populate_data_in_person_table(table_columns = columns_person_image_video, 
                                    table_name = table_peoplenames, 
                                    DB_NAME = DB_NAME_main,
                                    query = query_image_video)
    populate_data_in_person_table(table_columns = columns_person_videos, 
                                    table_name = table_peoplenamesvideos, 
                                    DB_NAME = DB_NAME_main,
                                    query = query_video)
    
    process_all_thumbnails(db_name=DB_NAME_main, output_folder=f"{root_folder}/thumbnails")
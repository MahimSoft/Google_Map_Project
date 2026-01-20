import os
import subprocess
import time
import sqlite3
from locations.decorators import time_of_execution
from py_display import display

# def time_of_execution(func):
#     def wrapper(*args, **kwargs):


# start_time = time.time()
# result = func(*args, **kwargs)
# end_time = time.time()
# execution_time = end_time - start_time

def update_data(db_name="map_db.sqlite3"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    qry_1 ="""UPDATE locations_googlephotos
            SET image = REPLACE(
                REPLACE(image, '/Google Photos/', '/Google Photos/JPG/'),
                substr(image, -5),
                '.jpg'
            )
            WHERE (image LIKE '%.HEIC'
            OR image LIKE '%.heic');
            """
    cursor.execute(qry_1)


    qry_2 ="""UPDATE locations_googlephotos
        SET image = REPLACE(
            REPLACE(image, '/Google Photos/', '/Google Photos/MP4/'),
            substr(image, -4),
            '.mp4'
        )
        WHERE (
        lower(image) like "%.mts" 
        or lower(image) like "%.mov" 
        or lower(image) like "%.3gp"  
        or lower(image) like "%.mpo"  
        or lower(image) like "%.wmv"  
        or lower(image) like "%.avi"
        );"""
        
    cursor.execute(qry_2)
    conn.commit()
    conn.close()


@time_of_execution        
def data_insertion_for_converted_mp4(input_root, db_name="map_db.sqlite3"):
    update_data(db_name)
    # Connect to the database
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    # conn2 = sqlite3.connect("heic_mp4.sqlite3")
    # cursor2 = conn2.cursor()
    create_table_query = """CREATE TABLE IF NOT EXISTS locations_googlephotos ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "title" varchar(255) NULL, "description" text NULL, "image_views" integer NOT NULL, "creation_time" datetime NULL, "photo_taken_time" datetime NULL, "latitude" real NULL, "longitude" real NULL, "altitude" real NULL, "people" varchar(255) NULL, "image" varchar(255) NULL, "url" varchar(500) NULL, "local_folder" varchar(255) NULL, "device_type" varchar(255) NULL, "remarks" varchar(255) NULL, "video_thumbnail" varchar(255) NULL);"""
    cursor.execute(create_table_query)
    # cursor2.execute(create_table_query)
    
    # List to store file paths
    file_list = []
    # root_list = []
    renamed_list = []

    for root, dirs, files in os.walk(input_root):
        for file in files:
            if file.lower().endswith(".heic"):
                # 1. Construct full input path
                input_path = '/'.join(os.path.join(root, file).split("/")[2:])
                # print(input_path)
                renamed_file = os.path.join(root, file.replace(".HEIC", ".MP4"))
                renamed_list.append(renamed_file)
                # root_list.append(root)
                file_list.append(input_path)
    
    zip_list = list(zip(file_list, renamed_list))
    
    
    for file,renamed_file in zip_list:
        # print(renamed_file)
        if os.path.isfile(renamed_file):
            qry = f"""SELECT 
            replace(title, '.HEIC','.MP4') as title,
            description,
            image_views,
            creation_time,
            photo_taken_time,
            latitude,
            longitude,
            altitude,
            people,
            replace(
            replace(image, '/Google Photos/JPG/', '/Google Photos/'), '.jpg', '.MP4'
            ) as image,
            video_thumbnail,
            url,
            local_folder,
            device_type,
            remarks
            FROM locations_googlephotos WHERE device_type = 'IOS_PHONE' and
            image = replace("{file.replace('/Google Photos/', '/Google Photos/JPG/').replace('.HEIC', '.jpg').replace('  ', ' ').replace('   ', ' ')}","\\","/");"""
            # device_type = 'IOS_PHONE' and 
            print(qry)
            cursor.execute(qry)
            rows = cursor.fetchall()
            # print(file.replace('/Google Photos/', '/Google Photos/JPG/').replace('.HEIC', '.jpg'))
            # print(rows)
            # print(rows)
            print("✅")
            insert_query = f"""INSERT INTO locations_googlephotos (
                                title,
                                description,
                                image_views,
                                creation_time,
                                photo_taken_time,
                                latitude,
                                longitude,
                                altitude,
                                people,
                                image,
                                video_thumbnail,
                                url,
                                local_folder,
                                device_type,
                                remarks) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"""
            if len(rows) > 0:
                cursor.execute(insert_query, rows[0])
        else:
            print("🙁")
            
    conn.commit()
    # conn2.close()
    conn.close()
    total_files = len(file_list)
    
    display(text=f"{total_files}", query=False, mysql=False, leading_text="Total Rows Inserted: ", border=False)
    # print(zip_list[0:10])
    # print("Total Files Found: ", total_files)
    
    

#! To Run: python py_heic_relevant_mp4_data.py

if __name__ == "__main__":
    SOURCE_FOLDER_1 = r'D:/takeout 20251226/MasudJGTDSL/Google Photos/'
    SOURCE_FOLDER_2 = r'D:/takeout 20251226/33a33a33a/Google Photos/'
    SOURCE_FOLDER_3 = r'D:/takeout 20251226/Mahimsoft/Google Photos/'

    data_insertion_for_converted_mp4(input_root=SOURCE_FOLDER_1)
    data_insertion_for_converted_mp4(input_root=SOURCE_FOLDER_2)
    data_insertion_for_converted_mp4(input_root=SOURCE_FOLDER_3)
from pathlib import Path
import os
import sqlite3
from locations.decorators import time_of_execution
from py_display import display, CLR

def get_file_paths(query="SELECT image FROM locations_googlephotos", db_name="map_db.sqlite3"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    file_paths = [row[0] for row in rows]
    conn.close()
    return file_paths

def format_bytes(size_bytes):
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB")
    import math
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_name[i]}"

def write_paths_to_file(file_paths, output_filename="file_paths_list.txt"):
    try:
        with open(output_filename, 'w', encoding='utf-8') as f:
            for path in file_paths:
                f.write(f"{path}\n")
        print(f"File paths successfully written to {output_filename}")
    except IOError as e:
        print(f"Error writing file paths to {output_filename}: {e}")

def calculate_total_size(root_dir, paths):
    total_bytes = 0
    total_not_found = 0
    total_file = len(paths)
    not_found_list = []
    for p in paths:
        file_obj = Path(f"{root_dir}/{p}")
        if file_obj.is_file():
            total_bytes += file_obj.stat().st_size
        else:
            total_not_found += 1
            not_found_list.append(file_obj)
            # print(f"Warning: {p} is not a valid file.")
    return {"total_bytes":total_bytes,"total_file":f"{total_file:,} Nos.", 
            "total_not_found":f"{total_not_found:,} Nos.", "not_found_list":not_found_list }

# total = calculate_total_size(file_paths)
# print(f"Total size: {total} bytes")


qry = """
SELECT *
FROM (
        SELECT `locations_googlephotos`.`id` AS `col1`,
            `locations_googlephotos`.`title` AS `col2`,
            `locations_googlephotos`.`description` AS `col3`,
            `locations_googlephotos`.`image_views` AS `col4`,
            `locations_googlephotos`.`creation_time` AS `col5`,
            `locations_googlephotos`.`photo_taken_time` AS `col6`,
            `locations_googlephotos`.`latitude` AS `col7`,
            `locations_googlephotos`.`longitude` AS `col8`,
            `locations_googlephotos`.`altitude` AS `col9`,
            `locations_googlephotos`.`people` AS `col10`,
            `locations_googlephotos`.`image` AS `col11`,
            `locations_googlephotos`.`video_thumbnail` AS `col12`,
            `locations_googlephotos`.`url` AS `col13`,
            `locations_googlephotos`.`local_folder` AS `col14`,
            `locations_googlephotos`.`device_type` AS `col15`,
            `locations_googlephotos`.`remarks` AS `col16`,
            LENGTH(`locations_googlephotos`.`people`) AS `people_len`,
            ROW_NUMBER() OVER (
                PARTITION BY `locations_googlephotos`.`title`
                ORDER BY `locations_googlephotos`.`title` ASC,
                    (`locations_googlephotos`.`people` * -1)
            ) AS `row_number`,
            
            CASE
                WHEN `locations_googlephotos`.`longitude` > 0.0 THEN True
                ELSE False
            END AS `is_location`,
            CASE
                WHEN (
                    `locations_googlephotos`.`title` LIKE '%.MTS'  
					OR `locations_googlephotos`.`title` LIKE "%.mp4"  
					OR `locations_googlephotos`.`title` LIKE "%.3gp"  
					OR `locations_googlephotos`.`title` LIKE "%.MOV"  
					OR `locations_googlephotos`.`title` LIKE "%.MP4"  
					OR `locations_googlephotos`.`title` LIKE "%.3GP"  
					OR `locations_googlephotos`.`title` LIKE "%.MPO"  
					OR `locations_googlephotos`.`title` LIKE '%.wmv'  
					OR `locations_googlephotos`.`title` LIKE '%.AVI' ) 
					THEN True ELSE False END AS `is_video`
					FROM `locations_googlephotos` 
					-- WHERE LENGTH(`locations_googlephotos`.`people`) > 0 
					ORDER BY `locations_googlephotos`.`photo_taken_time` DESC ) `qualify` 
WHERE `row_number` = 1 ORDER BY `col6` DESC;
"""

qry_all = """
SELECT image
FROM (
        SELECT 
            `locations_googlephotos`.`image` AS image,
            ROW_NUMBER() OVER (
                PARTITION BY `locations_googlephotos`.`title`
                ORDER BY `locations_googlephotos`.`title` ASC,
                    (`locations_googlephotos`.`people` * -1)
            ) AS `row_number`
            
            
					FROM `locations_googlephotos` 
					-- WHERE LENGTH(`locations_googlephotos`.`people`) > 0 
					ORDER BY `locations_googlephotos`.`photo_taken_time` DESC ) `qualify` 
WHERE `row_number` = 1 ;
"""

where_clause_not_video = """
(
lower(image)    not like "%.mts" 
AND lower(image) not like "%.mp4" 
AND lower(image) not like "%.mov" 
AND lower(image) not like "%.3gp"  
AND lower(image) not like "%.mpo"  
AND lower(image) not like "%.wmv"  
AND lower(image) not like "%.avi"
)"""

where_clause_videos_only = """
(
lower(image)    like "%.mts" 
or lower(image) like "%.mp4" 
or lower(image) like "%.mov" 
or lower(image) like "%.3gp"  
or lower(image) like "%.mpo"  
or lower(image) like "%.wmv"  
or lower(image) like "%.avi"
)"""

qry_except_video = f"""
SELECT image
FROM (
        SELECT 
            `locations_googlephotos`.`image` AS image,
            ROW_NUMBER() OVER (
                PARTITION BY `locations_googlephotos`.`title`
                ORDER BY `locations_googlephotos`.`title` ASC,
                    (`locations_googlephotos`.`people` * -1)
            ) AS `row_number`
            
					FROM `locations_googlephotos` 
					WHERE {where_clause_videos_only}
					-- WHERE LENGTH(`locations_googlephotos`.`people`) > 0 
					ORDER BY `locations_googlephotos`.`photo_taken_time` DESC ) `qualify` 
WHERE `row_number` = 1 ;
"""

def _get_files_and_size_recursive(path, extensions, collect_paths):
    total_size = 0
    file_paths = []
    with os.scandir(path) as it:
        for entry in it:
            if entry.is_file():
                for ext in extensions:
                    if entry.name.lower().endswith(ext.lower()):
                        if collect_paths:
                            file_paths.append(entry.path)
                        else:
                            total_size += entry.stat().st_size
            elif entry.is_dir():
                try:
                    result = _get_files_and_size_recursive(entry.path, extensions, collect_paths)
                    if collect_paths:
                        file_paths.extend(result)
                    else:
                        total_size += result
                except Exception as e:
                    print("☹️ ", e)
                    continue  # skip this file and move on
    return file_paths if collect_paths else total_size


def get_directory_size_fast(path, extensions=['.json', '.jpg', '.mp4', '.mts', '.3gp', '.mov', '.mpo', '.wmv', '.avi'], create_path_list=False):
    if create_path_list:
        return _get_files_and_size_recursive(path, extensions, collect_paths=True)
    else:
        return _get_files_and_size_recursive(path, extensions, collect_paths=False)

root_dir = r'D:\takeout 20251226\MasudJGTDSL'
root_dir_1 = r'E:/Takeout_20260205/Takeout/Google Photos/'
root_dir_2 = r'D:\takeout 20251226\MasudJGTDSL\Google Photos\MP4'
root_dir_2 = r'C:/'

#! To Run: python py_file_size_calculation.py
if __name__ == "__main__":
    # paths = get_file_paths(qry_except_video, db_name="map_db.sqlite3")
    # file_size =calculate_total_size(root_dir, paths)
    # formatted_size = format_bytes(file_size["total_bytes"])
    # total_file = file_size["total_file"]
    # total_not_found = file_size["total_not_found"]
    # not_found_list = file_size["not_found_list"]

    #! display(text, query=False, mysql=False, leading_text="Returned Data 📋", text_clr=CLR.Fg.red, border=True):
    # display(total_file, query=False, mysql=False, leading_text="Total Files", text_clr=CLR.Fg.red, border=False)
    # display(formatted_size, query=False, mysql=False, leading_text="Total Filesize", text_clr=CLR.Fg.red, border=False)
    # display(total_not_found, query=False, mysql=False, leading_text="Files Not Found", text_clr=CLR.Fg.red, border=False)
    # display(not_found_list, query=False, mysql=False, leading_text="List of Files Not Found", text_clr=CLR.Fg.red, border=False)
    extensions=['.jpg', '.mp4', '.mts', '.3gp', '.mov', '.mpo', '.wmv', '.avi']
    extensions_1=['.mp4','.mts', '.3gp', '.mov', '.mpo', '.wmv', '.avi']
    extensions_2=['.jpg','jpeg']
    extensions_3=['.json']
    display(format_bytes(get_directory_size_fast(root_dir_2, extensions=extensions_1)))

    # Example of creating a path list file
    output_path_filename = "video_paths_list.txt"
    video_paths = get_directory_size_fast(root_dir_2, extensions=extensions_1, create_path_list=True)
    write_paths_to_file(video_paths, output_path_filename)
    display(f"Video paths written to {output_path_filename}", text_clr=CLR.Fg.green, border=False)

    output_path_filename_jpg = "image_paths_list.txt"
    image_paths = get_directory_size_fast(root_dir_2, extensions=extensions_2, create_path_list=True)
    write_paths_to_file(image_paths, output_path_filename_jpg)
    display(f"Image paths written to {output_path_filename_jpg}", text_clr=CLR.Fg.green, border=False)
from datetime import datetime
import sqlite3
from py_delete_data_from_table import delete_data_from_table


def setup_database(table_columns, table_name, DB_NAME):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} (id INTEGER PRIMARY KEY AUTOINCREMENT, {table_columns})")
    conn.commit()
    return conn

def populate_data_in_person_table(table_columns, table_name, DB_NAME, query):
    conn = setup_database(table_columns, table_name, DB_NAME)
    cursor = conn.cursor()
    cursor.execute(query)
    print(query)
    people_list = cursor.fetchall()
    name_list = []
    for item in people_list:
        # print(item[0].split(", "))
        name_list += item[0].split(", ")

    people_list = list(set(name_list))
    people_list.sort()

    if table_name == "locations_peoplenames":
        qry =f"INSERT INTO {table_name} (id, name, num_of_images, archive) VALUES (?,?,'',0)"
    else:
        qry =f"INSERT INTO {table_name} (id, name) VALUES (?,?)"
        
    tpl = tuple(enumerate(people_list, start=1))
    # print(tpl)
    cursor.executemany(qry, tpl)
    conn.commit()  
    cursor.execute(f"SELECT * FROM {table_name};")
    people_list_from_db = cursor.fetchall()
    print(people_list_from_db)
    print(len(people_list_from_db))
    
    qry_image_nums = """
    select count(people) as num_of_images
    from locations_googlephotos
    where length(people) > 0 and people like '%{}%'
    """
    
    qry_video_nums = """
    select count(people) as num_of_images
    from locations_googlephotos
    where length(people) > 0 and people like '%{}%' and (
                    title like '%.mp4' 
                    or title like '%.MOV' 
                    or title like '%.MTS' 
                    or title like '%.3gp' 
                    or title like '%.3GP' 
                    or title like '%.MPO' 
                    or title like '%.wmv' 
                    or title like '%.AVI' 
                    or title like '%.MP4' 
                    );
    """
    if table_name == "locations_peoplenames":
        qry_for_nums = qry_image_nums
    else:
        qry_for_nums = qry_video_nums
    
    for item in people_list_from_db:
        cursor.execute(qry_for_nums.format(item[1]))
        num_of_images = cursor.fetchone()[0]
        print(f"{item[1]}: {num_of_images}")
        if table_name == "locations_peoplenames":
            cursor.execute(f"UPDATE {table_name} SET num_of_images = {num_of_images} WHERE id = '{item[0]}';")
        else:
            cursor.execute(f"UPDATE {table_name} SET num_of_videos = {num_of_images} WHERE id = '{item[0]}';")
            
    conn.commit()
    # conn.commit()          
    # print(tuple(enumerate(people_list)), len(people_list))

    conn.close()


#! To Run: python py_person_data.py

if __name__ == "__main__":
    columns_person_image_video = " name TEXT, num_of_images INTEGER, thumbnail varchar(255) NULL, archive bool "
    columns_person_videos = " name TEXT, num_of_videos INTEGER "
    query_image_video = """SELECT lower(people) as people, Null as thumbnail, 0 as archive FROM locations_googlephotos WHERE length(people) > 0"""
    query_video="""SELECT lower(people) as people FROM locations_googlephotos WHERE length(people) > 0 
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
    # copy_table('source_db.sqlite3', 'target_db.sqlite3', 'source_table', 'target_table')
    # copy_table('db.sqlite3', 'map_db.sqlite3', 'locations_locationbatch', 'locations_locationbatch')
    # copy_table('db.sqlite3', 'map_db.sqlite3', 'locations_place', 'locations_place')
    DB_NAME = 'map_db.sqlite3'
    table_name_image_video = 'locations_peoplenames'
    table_name_videos = 'locations_peoplenamesvideos'
    delete_data_from_table(table_name_image_video, DB_NAME)
    populate_data_in_person_table(table_columns = columns_person_image_video, 
               table_name = table_name_image_video, 
               DB_NAME = DB_NAME,
               query = query_image_video)
    
    delete_data_from_table(table_name_videos, DB_NAME)
    populate_data_in_person_table(table_columns = columns_person_videos, 
               table_name = table_name_videos, 
               DB_NAME = DB_NAME,
               query = query_video)

# locations_people_names


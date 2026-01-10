import sqlite3

def copy_table(source_db, target_db, source_table, target_table, columns=" * "):
    # Connect to the target database (Database B)
    conn = sqlite3.connect(target_db)
    cursor = conn.cursor()

    try:
        # 1. Attach Database A to the current connection
        # We give it an alias 'source_db' so we can reference its tables
        cursor.execute(f"ATTACH DATABASE '{source_db}' AS source_db")

        # 2. Create the table in Database B if it doesn't exist 
        # (This copies the schema exactly)
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {target_table} AS 
            SELECT id, {columns} FROM source_db.{source_table} WHERE 1=0
        ''')

        # 3. Copy the data
        cursor.execute(f"INSERT INTO {target_table} ({columns}) SELECT {columns} FROM source_db.{source_table}")
        
        conn.commit()
        print(f"Successfully copied data from {source_db} to {target_db}")

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    
    finally:
        # 4. Detach and close
        cursor.execute("DETACH DATABASE source_db")
        conn.close()

#! To Run: python py_copy_data.py

columns = " title, description, image_views, creation_time, photo_taken_time, latitude, longitude, altitude, people, image, url, local_folder, device_type, remarks "
columns_2 = " name "
if __name__ == "__main__":
    # copy_table('source_db.sqlite3', 'target_db.sqlite3', 'source_table', 'target_table')
    # copy_table('db.sqlite3', 'map_db.sqlite3', 'locations_locationbatch', 'locations_locationbatch')
    # copy_table('db.sqlite3', 'map_db.sqlite3', 'locations_place', 'locations_place')
    # copy_table(source_db = 'MasudJGTDSL.sqlite3', 
    #            target_db = 'map_db.sqlite3', 
    #            source_table='locations_googlephotos', 
    #            target_table = 'locations_googlephotos', 
    #            columns = columns)
    copy_table(source_db = 'people_names.sqlite3', 
               target_db = 'map_db.sqlite3', 
               source_table='locations_people_names', 
               target_table = 'locations_peoplenames', 
               columns = columns_2)
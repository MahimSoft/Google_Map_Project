from datetime import datetime
import sqlite3


def setup_database(table_columns, table_name, DB_NAME):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} (id INTEGER PRIMARY KEY AUTOINCREMENT, {table_columns})")
    conn.commit()
    return conn

def create_person_table(table_columns, table_name, DB_NAME):
    conn = setup_database(table_columns, table_name, DB_NAME)
    conn2 = sqlite3.connect("map_db.sqlite3")
    cursor = conn2.cursor()
    cursor.execute(f'''SELECT people FROM locations_googlephotos WHERE length(people) > 0
         ''')
    people_list = cursor.fetchall()
    name_list = []
    for item in people_list:
        name_list += item[0].split(", ")

    # people_list = [item.split(", ") for item in people_list]
    # people_list = [item for sublist in people_list for item in sublist]
    people_list = list(set(name_list))
    people_list.sort()
    qry =f"INSERT INTO {table_name} (id, name) VALUES (?,?)"
    cursor2 = conn.cursor()
    cursor2.executemany(qry, tuple(enumerate(people_list, start=1)))
    conn.commit()          
    print(tuple(enumerate(people_list)), len(people_list))

    conn.close()
    conn2.close()

#! To Run: python py_others.py

columns = " name TEXT "

if __name__ == "__main__":
    # copy_table('source_db.sqlite3', 'target_db.sqlite3', 'source_table', 'target_table')
    # copy_table('db.sqlite3', 'map_db.sqlite3', 'locations_locationbatch', 'locations_locationbatch')
    # copy_table('db.sqlite3', 'map_db.sqlite3', 'locations_place', 'locations_place')
    create_person_table(table_columns = columns, 
               table_name = 'locations_people_names', 
               DB_NAME = 'people_names.sqlite3')

# locations_people_names


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

table_columns = table_columns.replace("\n","").split(",")
table_columns = [col.strip().split(" ")[0] for col in table_columns]
print(table_columns, "Length = ", len(table_columns))

print(', '.join(table_columns[1:]))


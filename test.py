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


            <button class="btn btn-outline">Default</button>
            <button class="btn btn-outline ">Primary</button>
            <button class="btn btn-outline ">Secondary</button>
            <button class="btn btn-outline ">Accent</button>
            <button class="btn btn-outline ">Info</button>
            <button class="btn btn-outline ">Success</button>
            <button class="btn btn-outline ">Warning</button>
            <button class="btn btn-outline ">Error</button>

'btn-primary',
'btn-secondary',
'btn-accent',
'btn-info',
'btn-success',
'btn-warning',
'btn-error',
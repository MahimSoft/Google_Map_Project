import os
import sqlite3
from tqdm import tqdm

# --- Configuration ---
DB_PATH = "map_db.sqlite3"  # adjust if your database file is elsewhere
TABLE_NAME = "locations_peoplenames"
FIELD_NAME = "thumbnail"
THUMBNAIL_DIR = r"D:\takeout 20251226\people_thumbnails"

def cleanup_thumbnails():
    # Connect to the SQLite database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Fetch all thumbnail paths from the table
    cursor.execute(f"SELECT {FIELD_NAME} FROM {TABLE_NAME} WHERE thumbnail is NOT NULL")
    db_thumbnails = {row[0] for row in cursor.fetchall() if row[0]}

    # List all files in the thumbnail directory
    dir_files = {os.path.join(THUMBNAIL_DIR, f) for f in os.listdir(THUMBNAIL_DIR)}

    # Normalize paths for comparison (important if DB stores relative paths)
    db_thumbnails_normalized = {os.path.normpath(os.path.join(THUMBNAIL_DIR, os.path.basename(path)))
                                for path in db_thumbnails}

    # Find files in directory not referenced in DB
    files_to_delete = dir_files - db_thumbnails_normalized

    # Delete unreferenced files
    for file_path in  tqdm(files_to_delete, desc="Deleting Files", unit="file"):
        try:
            os.remove(file_path)
            # print(f"Deleted: {file_path}")
        except Exception as e:
            print(f"Error deleting {file_path}: {e}")
            
    print(f"Deletion Process Completed!")

    conn.close()

#! To Run: python py_clean_thumbnails.py

if __name__ == "__main__":
    cleanup_thumbnails()

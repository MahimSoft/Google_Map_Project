import json
from datetime import datetime
import sqlite3
import os
from tqdm import tqdm
from locations.decorators import time_of_execution
from py_copy_delete_file import copy_file, delete_file
from py_display import display

def delete_data_from_table(table_name, DB_NAME):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(f"DELETE FROM {table_name}")
    cursor.execute(f"UPDATE sqlite_sequence SET seq = 0 WHERE name = '{table_name}'")
    conn.commit()
    conn.close()
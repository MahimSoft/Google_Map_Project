import os
from datetime import datetime
import shutil
from pathlib import Path
from py_display import display


# source = "path/to/source_file.txt"
# destination = "path/to/destination_folder/target_file.txt"

def copy_file(source, destination, entire_folder=False):

    # Ensure the destination directory exists first (optional but safer)
    os.makedirs(os.path.dirname(destination), exist_ok=True)

    try:
        # This will replace the file if it already exists
        if entire_folder:
            shutil.copytree(source, destination, dirs_exist_ok=True)
            display(text=destination, query=False, mysql=False, leading_text="Directory copied successfully to", border=False)
        else:
            shutil.copy2(source, destination)
            display(text=destination, query=False, mysql=False, leading_text="File copied successfully to", border=False)
            
    except FileNotFoundError:
        print("Source file not found.")
    except PermissionError:
        print("Permission denied.")


def delete_file(file_path,entire_folder=False):
    try:
        # os.remove(file_path)
        if entire_folder:
            shutil.rmtree(file_path)
            print(f"Directory '{file_path}' has been deleted.")
        else:
            Path(file_path).unlink(missing_ok=True)
            #! missing_ok=True prevents an error if the file doesn't exist
            print(f"File '{file_path}' has been deleted.")
            
    except FileNotFoundError:
        print("Source file not found.")
    except PermissionError:
        print("Permission denied.")
        

# if __name__ == "__main__":
#     copy_file(source = "path/to/source_file.txt", destination = "path/to/destination_folder/target_file.txt")
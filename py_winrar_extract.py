import os
import time
import subprocess
from send2trash import send2trash
from locations.decorators import time_of_execution
from py_display import display

@time_of_execution
def extract_and_delete(source_dir, destination_dir, winrar_path, delete_permanently=False):
    # Create destination if it doesn't exist
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)

    # Filter for archive files
    archives = [f for f in os.listdir(source_dir) if f.lower().endswith(('.zip', '.rar', '.7z'))]
    total_files = len(archives)
    sl = 0
    
    if not archives:
        print("No archives found.")
        return

    for filename in archives:
        filepath = os.path.join(source_dir, filename)
        sl += 1
        
        # WinRAR CLI flags:
        # x      : Extract with full paths
        # -ibck  : Run in background (minimized to tray)
        # -y     : Assume "Yes" to all (overwrites existing files)
        command = [winrar_path, "x", "-ibck", "-y", filepath, destination_dir]
        
        try:
            print(f"{sl} of {total_files} Extracting: {filename}...")
            start_time = time.time()
            # Wait for WinRAR to finish
            subprocess.run(command, check=True)
            end_time = time.time()
            execution_time = end_time - start_time
            display(text=f"{execution_time:.2f} seconds.", query=False, mysql=False, leading_text="Extraction completed in", border=False)
            if delete_permanently:
                os.remove(filepath)
                print(f"Permanently deleted: {filename}")
            else:         
                # Move to Recycle Bin
                print(f"Moving to Recycle Bin: {filename}")
                send2trash(filepath)
                
        except subprocess.CalledProcessError as e:
            print(f"Failed to extract {filename}. File was NOT deleted. Error: {e}")
        except Exception as e:
            print(f"An error occurred with {filename}: {e}")
            
#! To Run: python py_winrar_extract.py

if __name__ == "__main__":
    # --- Configuration ---
    winrar_path = r"C:\Program Files\WinRAR\WinRAR.exe"
    source_dir = r"E:\Takeout_20251229"
    # Set destination_dir to source_dir for "Extract Here"
    destination_dir = r"E:\Takeout_20251229" 
    delete_permanently = False  # False moves to Recycle Bin (requires extra lib), True deletes
    # --- End Configuration ---
    
    extract_and_delete(source_dir, destination_dir, winrar_path, delete_permanently)
    print("Process complete.")
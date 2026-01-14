import os
import subprocess
from send2trash import send2trash

# --- Configuration ---
winrar_path = r"C:\Program Files\WinRAR\WinRAR.exe"
source_dir = r"F:\TEST_EXTRACT"
# Set destination_dir to source_dir for "Extract Here"
destination_dir = r"F:\TEST_EXTRACT" 
delete_permanently = False  # False moves to Recycle Bin (requires extra lib), True deletes

def extract_and_delete():
    # Create destination if it doesn't exist
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)

    # Filter for archive files
    archives = [f for f in os.listdir(source_dir) if f.lower().endswith(('.zip', '.rar', '.7z'))]

    if not archives:
        print("No archives found.")
        return

    for filename in archives:
        filepath = os.path.join(source_dir, filename)
        
        # WinRAR CLI flags:
        # x      : Extract with full paths
        # -ibck  : Run in background (minimized to tray)
        # -y     : Assume "Yes" to all (overwrites existing files)
        command = [winrar_path, "x", "-ibck", "-y", filepath, destination_dir]
        
        try:
            print(f"Extracting: {filename}...")
            # Wait for WinRAR to finish
            subprocess.run(command, check=True)
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
    extract_and_delete()
    print("Process complete.")
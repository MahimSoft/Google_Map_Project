# utils.py
import os
import subprocess
import time
from locations.decorators import time_of_execution
from py_display import display

# def time_of_execution(func):
#     def wrapper(*args, **kwargs):


# start_time = time.time()
# result = func(*args, **kwargs)
# end_time = time.time()
# execution_time = end_time - start_time

@time_of_execution        
def convert_to_mp4(input_root, output_root):
    # Extensions to look for (case-insensitive)
    target_extensions = ('.mts', '.3gp', '.mov', '.mpo', '.wmv', '.avi')
    
    # List to store file paths
    file_list = []
    file_count = 0
    
    for root, dirs, files in os.walk(input_root):
        for file in files:
            if file.lower().endswith(target_extensions):
                # 1. Construct full input path
                input_path = os.path.join(root, file)
                file_list.append(input_path)
    
    total_files = len(file_list)
        
    print("Total Files Found: ", total_files)

    for root, dirs, files in os.walk(input_root):
        for file in files:
            if file.lower().endswith(target_extensions):
                # 1. Construct full input path
                input_path = os.path.join(root, file)
                file_count += 1
                # 2. Create corresponding output path
                # Calculate relative path to maintain folder structure
                rel_path = os.path.relpath(root, input_root)
                target_dir = os.path.join(output_root, rel_path)
                
                # Ensure the subfolder exists in the destination
                if not os.path.exists(target_dir):
                    os.makedirs(target_dir)

                # 3. Define output filename (change extension to .mp4)
                filename_no_ext = os.path.splitext(file)[0]
                output_path = os.path.join(target_dir, f"{filename_no_ext}.mp4")
                start_time = time.time()
                if not os.path.isfile(output_path):
                    print(f"Converting: {file_count} of {total_files}: {input_path} -> {output_path}")
                    ffmpeg_path = r'C:/ffmpeg/bin/ffmpeg.exe'
                    # 4. FFmpeg Command
                    command = [
                        ffmpeg_path, '-y', '-i', input_path,
                        '-codec:v', 'libx264', '-crf', '23', '-preset', 'medium',
                        '-codec:a', 'aac', '-b:a', '128k',
                        '-movflags', 'faststart', # Optimizes for web streaming
                        output_path
                    ]

                    try:
                        # check=True will raise an error if the conversion fails
                        subprocess.run(command, check=True, capture_output=True)
                        end_time = time.time()
                        execution_time = end_time - start_time
                        display(text=f"{execution_time:.2f} seconds.", query=False, mysql=False, leading_text="Conversion completed in", border=False)
                        # display(f"Conversion completed in {execution_time:.2f} seconds.")

                    except subprocess.CalledProcessError as e:
                        print(f"Error converting {file}: {e.stderr.decode()}")
                else:
                    print(f"File already exists: {output_path}")



# Example Usage
# convert_to_mp4('media/uploads', 'media/processed')



#! To Run: python py_convert_videos.py

if __name__ == "__main__":
    SOURCE_FOLDER = 'D:/takeout 20251226/33a33a33a/Google Photos/'
    DEST_FOLDER = 'D:/takeout 20251226/33a33a33a/Google Photos/MP4'
    # convert_to_mp4(input_root = SOURCE_FOLDER, output_root=DEST_FOLDER)
    convert_to_mp4(input_root=SOURCE_FOLDER, output_root=DEST_FOLDER)

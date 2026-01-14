import os
from PIL import Image
from pillow_heif import register_heif_opener

# Register the HEIF plugin for Pillow
register_heif_opener()

# SOURCE_FOLDER = "path/to/your/heic_files"
# DEST_FOLDER = "path/to/save/jpg_files"

def batch_convert_recursive(src, dest):
    for root, dirs, files in os.walk(src):
        for file in files:
            if file.lower().endswith(".heic"):
                # 1. Construct full input path
                input_path = os.path.join(root, file)

                # 2. Construct output path (maintaining subfolder structure)
                relative_path = os.path.relpath(root, src)
                output_dir = os.path.join(dest, relative_path)

                # Create the subfolder in destination if it doesn't exist
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)

                output_path = os.path.join(output_dir, os.path.splitext(file)[0] + ".jpg")

                # 3. Perform the conversion
                try:
                    with Image.open(input_path) as img:
                        # Convert to RGB to ensure JPEG compatibility
                        img.convert("RGB").save(output_path, "JPEG", quality=90)
                    print(f"Converted: {input_path} -> {output_path}")
                except Exception as e:
                    print(f"Failed to convert {input_path}: {e}")

# Run the function

SOURCE_FOLDER = 'D:/takeout 20251226/MasudJGTDSL/Google Photos/'
DEST_FOLDER = 'D:/takeout 20251226/MasudJGTDSL/Google Photos/JPG'

#! To Run: python py_heif_to_jpg.py

if __name__ == "__main__":
    batch_convert_recursive(SOURCE_FOLDER, DEST_FOLDER)

import os
from zipfile import ZipFile
from send2trash import send2trash
from tqdm import tqdm

def extract_files(source_dir, destination_dir):
    files_to_extract = [f for f in os.listdir(source_dir) if f.lower().endswith(('.zip', '.rar', '.7z'))]
    total_size = sum(os.path.getsize(f"{source_dir}/{f}") for f in files_to_extract)

    with tqdm(total=total_size, unit='B', unit_scale=True, unit_divisor=1024, desc="Extracting") as t:
        for file in files_to_extract:
            with ZipFile(f"{source_dir}/{file}", 'r') as zip_ref:
                for member in zip_ref.infolist():
                    zip_ref.extract(member, path=destination_dir)
                    t.update(member.file_size)
            send2trash(os.path.join(source_dir, file))

#! To Run: python py_zipfile_extract.py

if __name__ == "__main__":
    SOURCE_DIR = r"F:\ZIP TEST"
    DESTINATION_DIR = r"F:\ZIP TEST"
    extract_files(SOURCE_DIR, DESTINATION_DIR)
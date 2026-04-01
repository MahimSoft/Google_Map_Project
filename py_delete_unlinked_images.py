import os
from bs4 import BeautifulSoup

# Paths
html_file = "Spices.html"
images_folder = "images"

# Step 1: Extract all image src values from HTML
with open(html_file, "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f, "html.parser")

img_srcs = {os.path.basename(img["src"]) for img in soup.find_all("img", src=True)}

# Step 2: List all files in images folder
all_images = set(os.listdir(images_folder))

# Step 3: Find unused files
unused_images = all_images - img_srcs

# Step 4: Delete unused files
for filename in unused_images:
    file_path = os.path.join(images_folder, filename)
    os.remove(file_path)
    print(f"Deleted: {filename}")

print("Cleanup complete.")
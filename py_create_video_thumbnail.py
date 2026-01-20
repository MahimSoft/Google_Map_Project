import sqlite3
import subprocess
import os
from PIL import Image, ImageDraw, ImageFont


def add_logo_to_thumbnail(background_img, logo_path, margin=20):
    """
    background_img: The PIL Image object of the video frame
    logo_path: Path to your PNG logo
    margin: Distance from the edge of the image
    """
    try:
        # 1. Open logo and ensure it has an alpha channel (transparency)
        logo = Image.open(logo_path).convert("RGBA")

        # 2. Resize logo proportionally (e.g., set width to 15% of background)
        bg_w, bg_h = background_img.size
        logo_w_size = int(bg_w * 0.07)
        w_percent = (logo_w_size / float(logo.size[0]))
        h_size = int((float(logo.size[1]) * float(w_percent)))
        logo = logo.resize((logo_w_size, h_size), Image.Resampling.LANCZOS)

        # 3. Calculate position (Top-Right corner)
        # Position = (Total Width - Logo Width - Margin, Margin)
        pos_x = bg_w - logo.size[0] - margin
        pos_y = margin

        # 4. Paste logo using its own alpha channel as a mask
        background_img.paste(logo, (pos_x, pos_y), logo)

        return background_img
    except Exception as e:
        print(f"Could not add logo: {e}")
        return background_img


def process_all_thumbnails(db_name="map_db.sqlite3", output_folder="D:/takeout 20251226/thumbnails"):
    # Connect to the database
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Fetch video paths and titles (adjust field names if they differ)
    # Assuming 'video' is the file path and 'title' (or similar) is the text
    qry = """SELECT id, image, people FROM locations_googlephotos WHERE
            lower(image) like "%.mp4" """
    
    try:
        cursor.execute(qry)
        rows = cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return
    # finally:
    #     conn.close()
    total_files =len(rows)
    rs=0
    
    for id, video_path, text in rows:
        if not os.path.exists(f"D:/takeout 20251226/{video_path}"):
            print(f"File not found, skipping: {video_path}")
            continue
        # Define output path: same folder, change extension to .jpg
        rs+=1
        base_dir = os.path.dirname(video_path)
        file_name = os.path.splitext(os.path.basename(video_path))[0]
        output_path = os.path.join(output_folder, f"{id}_{file_name}_thumb.jpg")
        conn.execute(f"UPDATE locations_googlephotos SET video_thumbnail = 'thumbnails/{id}_{file_name}_thumb.jpg' WHERE id = {id}")
        if not os.path.isfile(output_path):
            print(f"Processing: {rs} of {total_files}: {file_name}...")
            create_thumbnail(f"D:/takeout 20251226/{video_path}", output_path, text)
        
    conn.commit()
    conn.close()
    
def create_thumbnail(video_path, output_path, text):
    temp_frame = "temp_raw_frame.jpg"

    # 1. Extract frame at 2 seconds for the poster
    ffmpeg_path = r'C:/ffmpeg/bin/ffmpeg.exe'
    subprocess.run([
        ffmpeg_path, '-ss', '00:00:02', '-i', video_path,
        '-frames:v', '1', '-q:v', '2', temp_frame, '-y'
    ], capture_output=True)

    if not os.path.exists(temp_frame):
        return

    # 2. Add Text Overlay
    img = Image.open(temp_frame)
    # ! New code ======
    new_size = (680, 380)
    try:
        width, height = img.size
        new_image_width, new_image_height = new_size
        output_size = new_size

        if width > height:
            new_image_height = int(new_image_width*(height/width))
            output_size = (new_image_width,new_image_height)
        else:
            new_image_width = int(new_image_height*(width/height))
            output_size = (new_image_width,new_image_height)
            
        img = img.resize(output_size, Image.Resampling.LANCZOS)     
            
    except FileNotFoundError:
        print(f"Error: Image not found")
        return
    except Exception as e:
        print(f"Error opening image: {e}")
        return
    # ! New code End ======
    
    img = add_logo_to_thumbnail(img, r"F:\Takeout\Google_Map_Project\static\images\096.png")
    draw = ImageDraw.Draw(img)

    # Load font - adjust size based on image width
    try:
        # Standard path for many Linux systems, change for Windows (e.g., "arial.ttf")
        font = ImageFont.truetype("arial.ttf", int(img.width * 0.025))
    except:
        font = ImageFont.load_default()

    # Draw centered text with a small black outline for readability
    w, h = img.size
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x, y = (w - tw) // 2, h - th - 60

    # Draw outline/shadow
    for adj in range(-2, 3):
        draw.text((x+adj, y+adj), text, font=font, fill="black")

    # Draw main text
    draw.text((x, y), text, font=font, fill="white")
    

    # 3. Save to destination and cleanup
    img.save(output_path, quality=90)
    if os.path.exists(temp_frame):
        os.remove(temp_frame)
#! To Run: python py_create_video_thumbnail.py
if __name__ == "__main__":
    process_all_thumbnails()


# draw.text(
#     (img.width / 2, img.height * 0.8), # Coordinates: Center-X, 80% down Y
#     text="YOUR VIDEO TITLE",
#     font=font,
#     fill="white",
#     stroke_width=2,         # Outline thickness
#     stroke_fill="black",    # Outline color
#     anchor="mm"             # Centers text precisely on the coordinate
# )
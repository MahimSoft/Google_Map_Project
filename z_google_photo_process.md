
1. py_json_to_sqlite3.py > py_copy_data.py (for each user google photos folder)

2. py_heif_to_jpg.py > if necessary
    -- Update Field (Mandetory) ===============
    ```sql
    UPDATE locations_googlephotos
    SET image = REPLACE(
        REPLACE(image, '/Google Photos/', '/Google Photos/JPG/'),
        substr(image, -5),
        '.jpg'
    )
    WHERE (image LIKE '%.HEIC'
    OR image LIKE '%.heic');
    ```

3. py_heic_relevent_mp4_data.py


4. py_convert_videos.py
    -- Update Field (Mandetory) ===============
    ```sql
    UPDATE locations_googlephotos
    SET image = REPLACE(
        REPLACE(image, '/Google Photos/', '/Google Photos/MP4/'),
        substr(image, -4),
        '.mp4'
    )
    WHERE (
    lower(image) like "%.mts" 
    or lower(image) like "%.mov" 
    or lower(image) like "%.3gp"  
    or lower(image) like "%.mpo"  
    or lower(image) like "%.wmv"  
    or lower(image) like "%.avi"
    );
    ```

5. py_create_video_thumbnail.py (Before process delete all files from thumbnail folder)
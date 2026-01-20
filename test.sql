SELECT 
replace(image, 'takeout_media/', '') as title,
'' as description,
0 as image_views,
'' as creation_time,
timestamp as photo_taken_time,
latitude,
longitude,
0 as altitude,
image,
'' as url,
'' as local_folder,
'' as device_type,
'gallery_mediaitem' as remarks,
'' as video_thumbnail,
'' as people

from gallery_mediaitem;

-- gallery_mediaitem: id,title,image,latitude,longitude,timestamp,is_video

INSERT INTO locations_googlephotos (
    title,
    description,
    image_views,
    creation_time,
    photo_taken_time,
    latitude,
    longitude,
    altitude,
    image,
    url,
    local_folder,
    device_type,
    remarks,
    video_thumbnail,
    people
)
SELECT 
    REPLACE(image, 'takeout_media/', '') AS title,
    '' AS description,
    0 AS image_views,
    NULL AS creation_time,
    "timestamp" AS photo_taken_time,
    latitude,
    longitude,
    0 AS altitude,
    image,
    '' AS url,
    '' AS local_folder,
    '' AS device_type,
    'gallery_mediaitem' AS remarks,
    '' AS video_thumbnail,
    '' AS people
FROM gallery_mediaitem;


UPDATE locations_googlephotos
SET people = replace(people, "Maliha Mehjabin", "Maliha Mahjabin");

UPDATE locations_googlephotos
SET people = replace(people, "Maliha", "Maliha Mahjabin")
WHERE (
    people like "%maliha%"
    AND people NOT like "%maliha mahjabin%"
  );

UPDATE locations_googlephotos
SET people = replace(people, "Lamiar Ma", "Nasrin Jahan Luna")
WHERE 
    people like "%Lamiar Ma%";

UPDATE locations_googlephotos
SET people = replace(people, "Mim-Er Ma", "Shamima Akter")
WHERE 
    people like "%Mim-Er Ma%";
import sqlite3
from locations.decorators import time_of_execution
from py_display import display

maliha_name_1 = """UPDATE locations_googlephotos
SET people = replace(people, "Maliha Mehjabin", "Maliha Mahjabin");"""

maliha_name_2 = """
UPDATE locations_googlephotos
SET people = replace(people, "Maliha", "Maliha Mahjabin")
WHERE (
    lower(people) like "%maliha%"
    AND (lower(people) NOT like "%maliha mahjabin%" or lower(people) NOT like "%maliha mehjabin%")
);
"""

mim_name = """
UPDATE locations_googlephotos
SET people = replace(people, "Mim", "Sumayah Islam Mim")
WHERE (
    lower(people) like "%mim%"
    AND (lower(people) NOT like "%shamima akter%" or lower(people) NOT like "%farzana (mim)%" or lower(people) NOT like "sumayah islam mim")
);
"""

lamiar_ma_name = """
UPDATE locations_googlephotos
SET people = replace(people, "lamiar ma", "Nasrin Jahan Luna")
WHERE 
    lower(people) like "%lamiar ma%";
"""

poly_paul_name = """
UPDATE locations_googlephotos
SET people = replace(people, "Poly (Wife of Kundu Babu)", "Poly Paul")
WHERE 
    lower(people) like "%poly (wife of kundu babu)%";
"""

mim_er_ma_name_1 = """
UPDATE locations_googlephotos
SET people = replace(people, "Mim-Er ma", "Shamima Akter")
WHERE 
    lower(people) like "%mim-er ma%";
"""
mim_er_ma_name_2 = """
UPDATE locations_googlephotos
SET people = replace(people, "Mim-er Ma", "shamima akter")
WHERE 
    lower(people) like "%mim-er ma%";
"""
farzana_name = """
UPDATE locations_googlephotos
SET people = replace(people, "Farzana", "Farzana Akter Ety")
WHERE 
    lower(people) like "%farzana%"
    AND lower(people) NOT like "%farzana (mim)%";
"""

gallery_mediaitem_to_locations_googlephotos = """INSERT INTO locations_googlephotos (
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
"""

query_list = [maliha_name_1, maliha_name_2, mim_name, lamiar_ma_name, mim_er_ma_name_1, 
              mim_er_ma_name_2,farzana_name,poly_paul_name, gallery_mediaitem_to_locations_googlephotos]
# gallery_mediaitem_to_locations_googlephotos
query_list2 = [mim_er_ma_name_2, farzana_name]
query_list_gallery = [gallery_mediaitem_to_locations_googlephotos]
@time_of_execution
def update_data(db_name="map_db.sqlite3", query_list=query_list):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    for query in query_list:
        cursor.execute(query)
        conn.commit()
    conn.close()
    display(text="Data Updated Successfully!", query=False, mysql=False, leading_text="Message", border=False)


#! To Run: python py_data_base_update_query.py
if __name__ == "__main__":
    update_data(db_name="map_db.sqlite3", query_list=query_list2)
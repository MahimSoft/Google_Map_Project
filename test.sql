CREATE TABLE locations_googlephotos (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255),
    description TEXT,
    image_views INTEGER NOT NULL,
    creation_time TIMESTAMP,
    photo_taken_time TIMESTAMP,
    latitude REAL,
    altitude REAL,
    people VARCHAR(255),
    image VARCHAR(255),
    url VARCHAR(500),
    local_folder VARCHAR(255),
    device_type VARCHAR(255),
    remarks VARCHAR(255),
    video_thumbnail VARCHAR(255),
    longitude REAL
);

SELECT *
FROM (
        SELECT "locations_googlephotos"."id" AS "col1",
            "locations_googlephotos"."title" AS "col2",
            "locations_googlephotos"."description" AS "col3",
            "locations_googlephotos"."image_views" AS "col4",
            "locations_googlephotos"."creation_time" AS "col5",
            "locations_googlephotos"."photo_taken_time" AS "col6",
            "locations_googlephotos"."latitude" AS "col7",
            "locations_googlephotos"."longitude" AS "col8",
            "locations_googlephotos"."altitude" AS "col9",
            "locations_googlephotos"."people" AS "col10",
            "locations_googlephotos"."image" AS "col11",
            "locations_googlephotos"."video_thumbnail" AS "col12",
            "locations_googlephotos"."url" AS "col13",
            "locations_googlephotos"."local_folder" AS "col14",
            "locations_googlephotos"."device_type" AS "col15",
            "locations_googlephotos"."remarks" AS "col16",
            "locations_googlephotos"."location_source" AS "col17",
            "maliha mahjabin" AS "person_name",
            ROW_NUMBER() OVER (
                PARTITION BY "locations_googlephotos"."photo_taken_time"
                ORDER BY "locations_googlephotos"."photo_taken_time" DESC,
                    LENGTH("locations_googlephotos"."people") DESC,
                    "locations_googlephotos"."title" ASC
            ) AS "row_number",
            CASE
                WHEN "locations_googlephotos"."longitude" > 0.0 THEN True
                ELSE False
            END AS "is_location",
            CASE
                WHEN (
                    "locations_googlephotos"."title" LIKE "%.MTS" 
                    OR "locations_googlephotos"."title" LIKE "%.mp4" 
                    OR "locations_googlephotos"."title" LIKE "%.3gp" 
                    OR "locations_googlephotos"."title" LIKE "%.MOV" 
                    OR "locations_googlephotos"."title" LIKE "%.MP4" 
                    OR "locations_googlephotos"."title" LIKE "%.3GP" 
                    OR "locations_googlephotos"."title" LIKE "%.MPO" 
                    OR "locations_googlephotos"."title" LIKE "%.wmv" 
                    OR "locations_googlephotos"."title" LIKE "%.AVI") 
                    THEN True ELSE False END AS "is_video" 
                    FROM "locations_googlephotos" 
                    WHERE "locations_googlephotos"."people" 
                    LIKE "%maliha mahjabin%" ORDER BY "locations_googlephotos"."photo_taken_time" DESC ) "qualify" WHERE "row_number" = 1 ORDER BY "col6" DESC
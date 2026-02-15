-- PGSQL
-- Table: public.locations_googlephotos
-- DROP TABLE IF EXISTS public.locations_googlephotos;
CREATE TABLE IF NOT EXISTS public.locations_googlephotos (
    id integer NOT NULL DEFAULT nextval('locations_googlephotos_id_seq'::regclass),
    title character varying(255) COLLATE pg_catalog."default",
    description text COLLATE pg_catalog."default",
    image_views integer NOT NULL,
    creation_time timestamp without time zone,
    photo_taken_time timestamp without time zone,
    latitude real,
    altitude real,
    image character varying(255) COLLATE pg_catalog."default",
    url character varying(500) COLLATE pg_catalog."default",
    local_folder character varying(255) COLLATE pg_catalog."default",
    device_type character varying(255) COLLATE pg_catalog."default",
    remarks character varying(255) COLLATE pg_catalog."default",
    video_thumbnail character varying(255) COLLATE pg_catalog."default",
    longitude real,
    CONSTRAINT locations_googlephotos_pkey PRIMARY KEY (id)
) TABLESPACE pg_default;
ALTER TABLE IF EXISTS public.locations_googlephotos OWNER to postgres;
-- Index: idx_photos_time
-- DROP INDEX IF EXISTS public.idx_photos_time;
CREATE INDEX IF NOT EXISTS idx_photos_time ON public.locations_googlephotos USING btree (photo_taken_time ASC NULLS LAST) WITH (fillfactor = 100, deduplicate_items = True) TABLESPACE pg_default;
-- Table: public.maps_timeline
-- DROP TABLE IF EXISTS public.maps_timeline;
CREATE TABLE IF NOT EXISTS public.maps_timeline (
    id integer,
    "latitudeE7" integer,
    "longitudeE7" integer,
    accuracy integer,
    source text COLLATE pg_catalog."default",
    "timestamp" text COLLATE pg_catalog."default",
    "deviceDesignation" text COLLATE pg_catalog."default",
    activity text COLLATE pg_catalog."default",
    "deviceTag" text COLLATE pg_catalog."default",
    altitude text COLLATE pg_catalog."default",
    "verticalAccuracy" text COLLATE pg_catalog."default",
    "platformType" text COLLATE pg_catalog."default",
    "serverTimestamp" text COLLATE pg_catalog."default",
    "deviceTimestamp" text COLLATE pg_catalog."default",
    "batteryCharging" text COLLATE pg_catalog."default",
    "formFactor" text COLLATE pg_catalog."default",
    velocity text COLLATE pg_catalog."default",
    heading text COLLATE pg_catalog."default",
    "osLevel" text COLLATE pg_catalog."default",
    "locationMetadata" text COLLATE pg_catalog."default",
    "inferredLocation" text COLLATE pg_catalog."default",
    "placeId" text COLLATE pg_catalog."default",
    "activeWifiScan" text COLLATE pg_catalog."default",
    latitude real,
    longitude real,
    date_time_extracted timestamp without time zone,
    year_month integer
) TABLESPACE pg_default;
ALTER TABLE IF EXISTS public.maps_timeline OWNER to postgres;
-- Index: idx_maps_timeline_time
-- DROP INDEX IF EXISTS public.idx_maps_timeline_time;
CREATE INDEX IF NOT EXISTS idx_maps_timeline_time ON public.maps_timeline USING btree (date_time_extracted ASC NULLS LAST) WITH (fillfactor = 100, deduplicate_items = True) TABLESPACE pg_default;
CREATE TABLE photo_best_match AS
SELECT photo_id,
    latitude,
    longitude
FROM (
        SELECT a.id AS photo_id,
            b.latitude,
            b.longitude,
            ROW_NUMBER() OVER (
                PARTITION BY a.id
                ORDER BY ABS(
                        EXTRACT(
                            EPOCH
                            FROM (a.photo_taken_time - b.date_time_extracted)
                        )
                    )
            ) AS rn
        FROM locations_googlephotos a
            JOIN maps_timeline b ON b.date_time_extracted BETWEEN a.photo_taken_time - INTERVAL '600 seconds'
            AND a.photo_taken_time + INTERVAL '600 seconds'
    ) sub
WHERE rn = 1;
-- SQLite3
SELECT id,
    title,
    description,
    image_views,
    creation_time,
    photo_taken_time,
    latitude,
    altitude,
    image,
    url,
    local_folder,
    device_type,
    remarks,
    video_thumbnail,
    longitude
FROM locations_googlephotos
WHERE latitude < 1
    AND local_folder NOT like "%WhatsApp%";
DELETE FROM location_info_from_timeline;
UPDATE locations_googlephotos
SET longitude = (
        SELECT b.longitude
        FROM location_info_from_timeline b
        WHERE b.photo_id = locations_googlephotos.id
    ),
    latitude = (
        SELECT b.latitude
        FROM location_info_from_timeline b
        WHERE b.photo_id = locations_googlephotos.id
    ),
    remarks = 'Location Manipulated'
WHERE EXISTS (
        SELECT 1
        FROM location_info_from_timeline b
        WHERE b.photo_id = locations_googlephotos.id
    );
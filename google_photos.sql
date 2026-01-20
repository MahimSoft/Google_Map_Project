SELECT *
FROM locations_googlephotos
WHERE (
    title like "%.mp4%"
    OR title like "%.MOV%"
  )
  and latitude > 0;
--! Extension Check ----------
SELECT *
FROM locations_googlephotos
WHERE (
    lower(image) like "%.mts"
    or lower(image) like "%.mov"
    or lower(image) like "%.3gp"
    or lower(image) like "%.mpo"
    or lower(image) like "%.wmv"
    or lower(image) like "%.avi"
  );
SELECT *
FROM locations_googlephotos
WHERE (
    lower(image) like "%.mts"
    or lower(image) like "%.mp4"
    or lower(image) like "%.mov"
    or lower(image) like "%.3gp"
    or lower(image) like "%.mpo"
    or lower(image) like "%.wmv"
    or lower(image) like "%.avi"
  );
SELECT *
FROM locations_googlephotos
WHERE (
    lower(image) not like "%.mts"
    or lower(image) not like "%.mp4"
    or lower(image) not like "%.mov"
    or lower(image) not like "%.3gp"
    or lower(image) not like "%.mpo"
    or lower(image) not like "%.wmv"
    or lower(image) not like "%.avi"
  );
SELECT extension,
  count(extension) as No_of_file
FROM (
    SELECT SUBSTR(
        title,
        INSTR(title, '.') + 1,
        LENGTH(title) - INSTR(title, '.')
      ) AS extension,
      ROW_NUMBER() OVER (
        PARTITION BY title
        ORDER by title
      ) as row_num
    FROM locations_googlephotos
    WHERE latitude > 0
  ) QUERY_set
WHERE row_num = 1
GROUP by extension;
SELECT extension,
  COUNT(*) as No_of_file
FROM (
    SELECT CASE
        WHEN title LIKE '%.%' THEN -- Standard SQLite logic to extract text after the last dot
        REPLACE(title, rtrim(title, replace(title, '.', '')), '')
        ELSE 'no_extension'
      END AS extension,
      ROW_NUMBER() OVER (
        PARTITION BY title
        ORDER BY title
      ) as row_num
    FROM locations_googlephotos
  ) QUERY_set
WHERE row_num = 1
GROUP BY extension
ORDER BY No_of_file DESC;
-- Video Files: MTS, mp4, 3gp, MOV, MP4, 3GP, MPO, wmv, AVI
-- jpg	24859
-- JPG	9752
-- HEIC	1247
-- mp4	1074
-- png	1044
-- jpeg	422
-- MTS	103
-- heic	59
-- PNG	26
-- 3gp	21
-- gif	17
-- MPO	12
-- ico	9
-- bmp	9
-- cur	8
-- MOV	7
-- webp	6
-- no_extension	6
-- MP4	6
-- 3GP	6
-- JPEG	3
-- wmv	2
-- bat	2
-- AVI	2
-- tif	1
-- MPG	1
-- 1633350456943327	1
--! Extension Check End ----------
SELECT *
FROM locations_googlephotos
WHERE photo_taken_time BETWEEN '2017-12-01' AND '2018-01-31';
SELECT *
FROM gallery_mediaitem
WHERE longitude > 100;
SELECT *
FROM gallery_mediaitem
WHERE timestamp BETWEEN '2017-12-01' AND '2018-01-31';
SELECT *
FROM locations_place
WHERE timestamp BETWEEN '2017-12-01' AND '2018-01-31';
SELECT *
FROM (
    SELECT *,
      ROW_NUMBER() OVER (
        PARTITION BY title
        ORDER by title
      ) as row_num
    FROM locations_googlephotos
    WHERE latitude > 0
  ) sorted
WHERE row_num = 1;
SELECT *
FROM locations_googlephotos
WHERE latitude < 1;
-- Delete Data =============
DELETE FROM locations_googlephotos;
UPDATE sqlite_sequence
SET seq = 0
WHERE name = 'locations_googlephotos';
DELETE FROM locations_peoplenames;
UPDATE sqlite_sequence
SET seq = 0
WHERE name = 'locations_peoplenames';
DELETE FROM locations_peoplenamesvideo;
UPDATE sqlite_sequence
SET seq = 0
WHERE name = 'locations_peoplenamesvideo';
-- Update Field ===============
UPDATE locations_googlephotos
SET image = REPLACE(
    REPLACE(image, '/Google Photos/', '/Google Photos/JPG/'),
    substr(image, -5),
    '.jpg'
  )
WHERE (
    image LIKE '%.HEIC'
    OR image LIKE '%.heic'
  );
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

UPDATE locations_googlephotos
SET people = replace(people, "Maliha Mehjabin", "Maliha Mahjabin");

UPDATE locations_googlephotos
SET people = replace(people, "Maliha", "Maliha Mahjabin")
WHERE (
    people like "%maliha%"
    AND people NOT like "%maliha mahjabin%"
  );

  UPDATE locations_googlephotos
SET people = replace(people, "lamiar ma", "Nasrin Jahan Luna")
WHERE (
    people like "%lamiar ma%"
  );

DELETE FROM locations_peoplenames
WHERE name = "Maliha Mehjabin";
DELETE FROM locations_peoplenamesvideos
WHERE name = "Maliha Mehjabin";
DELETE FROM locations_peoplenames
WHERE id in (
    SELECT id
    FROM (
        SELECT *
        FROM (
            SELECT *,
              ROW_NUMBER() OVER (
                PARTITION BY lower(name)
                ORDER by name
              ) as row_num
            FROM locations_peoplenames
          ) sorted
        WHERE row_num = 2
      ) a
  );
DELETE FROM locations_peoplenamesvideos
WHERE id in (
    SELECT id
    FROM (
        SELECT *
        FROM (
            SELECT *,
              ROW_NUMBER() OVER (
                PARTITION BY lower(name)
                ORDER by name
              ) as row_num
            FROM locations_peoplenamesvideos
          ) sorted
        WHERE row_num = 2
      ) a
  );

  SELECT * FROM locations_peoplenames ORDER by locations_peoplenames.num_of_images DESC;


SELECT replace(people, "Lamiar Ma", "Nasrin Jahan Luna") as people FROM locations_googlephotos
WHERE people like "%Nasrin Jahan Luna%";
	
UPDATE locations_googlephotos
SET people = replace(people, "Lamiar Ma", "Nasrin Jahan Luna")
WHERE 
    people like "%Lamiar Ma%";
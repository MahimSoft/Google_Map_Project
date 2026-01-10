SELECT *
FROM locations_googlephotos
WHERE (title like "%.mp4%" OR title like "%.MOV%")
  and latitude > 0;

--! Extension Check ----------
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

SELECT
extension,
COUNT(*) as No_of_file
FROM (
SELECT
CASE
WHEN title LIKE '%.%' THEN
-- Standard SQLite logic to extract text after the last dot
REPLACE(title, rtrim(title, replace(title, '.', '')), '')
ELSE
'no_extension'
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
-- Update Field ===============
UPDATE locations_googlephotos
SET image = REPLACE(
    REPLACE(image, '/Google Photos/', '/Google Photos/JPG/'),
    substr(image, -5),
    '.jpg'
  )
WHERE image LIKE '%.HEIC' ESCAPE '\'
   OR image LIKE ' %.heic ' ESCAPE ' \ ';
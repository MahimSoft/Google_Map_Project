CREATE TABLE locations_googlephotos (
    id              SERIAL PRIMARY KEY,
    title           VARCHAR(255),
    description     TEXT,
    image_views     INTEGER NOT NULL,
    creation_time   TIMESTAMP,
    photo_taken_time TIMESTAMP,
    latitude        REAL,
    altitude        REAL,
    people          VARCHAR(255),
    image           VARCHAR(255),
    url             VARCHAR(500),
    local_folder    VARCHAR(255),
    device_type     VARCHAR(255),
    remarks         VARCHAR(255),
    video_thumbnail VARCHAR(255),
    longitude       REAL
);
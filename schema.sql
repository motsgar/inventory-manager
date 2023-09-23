DROP TABLE IF EXISTS location, item;

CREATE TABLE location (
    id SERIAL PRIMARY KEY,
    parent_id INTEGER
);

CREATE TABLE item (
    id SERIAL PRIMARY KEY,
    location_id INTEGER NOT NULL,
    name TEXT NOT NULL
);
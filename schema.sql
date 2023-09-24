DROP TABLE IF EXISTS location, item;

CREATE TABLE location (
    id SERIAL PRIMARY KEY,
    parent_id INTEGER REFERENCES location,
    name TEXT NOT NULL,

    UNIQUE (parent_id, name),
    CONSTRAINT no_empty_name CHECK (name <> ''),
    CONSTRAINT no_slash_in_name CHECK (name !~ '/')
);

CREATE TABLE item (
    id SERIAL PRIMARY KEY,
    location_id INTEGER NOT NULL,
    name TEXT NOT NULL
);
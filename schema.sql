DROP TABLE IF EXISTS location, category, category_property, item, item_location, item_property;

CREATE TABLE location (
    id SERIAL PRIMARY KEY,
    parent_id INTEGER REFERENCES location,
    name TEXT NOT NULL,

    UNIQUE NULLS NOT DISTINCT (parent_id, name),

    CONSTRAINT no_empty_name CHECK (name <> ''),
    CONSTRAINT no_slash_in_name CHECK (name !~ '/')
);

CREATE TABLE category (
    id SERIAL PRIMARY KEY,
    parent_id INTEGER REFERENCES category,
    name TEXT NOT NULL,

    UNIQUE NULLS NOT DISTINCT (parent_id, name),

    CONSTRAINT no_empty_name CHECK (name <> ''),
    CONSTRAINT no_slash_in_name CHECK (name !~ '/')
);

CREATE TABLE category_property (
    id SERIAL PRIMARY KEY,
    category_id INTEGER NOT NULL REFERENCES category,
    name TEXT NOT NULL,

    UNIQUE (category_id, name),

    CONSTRAINT no_empty_name CHECK (name <> '')
);

CREATE TABLE item (
    id SERIAL PRIMARY KEY,
    category_id INTEGER NOT NULL REFERENCES category,
    name TEXT NOT NULL
);

CREATE TABLE item_location (
    id SERIAL PRIMARY KEY,
    item_id INTEGER NOT NULL REFERENCES item,
    location_id INTEGER NOT NULL REFERENCES location,
    count INTEGER NOT NULL,

    UNIQUE (location_id, item_id),

    CONSTRAINT count_is_positive check (count >= 1)
);

CREATE TABLE item_property (
    id SERIAL PRIMARY KEY,
    item_id INTEGER NOT NULL REFERENCES item,
    category_property_id INTEGER NOT NULL REFERENCES category_property,
    value TEXT NOT NULL,

    UNIQUE (item_id, category_property_id)
);
from sqlalchemy import text

from database import db


# https://learnsql.com/blog/how-to-query-hierarchical-data/
def get_location(path: list[str]):
    return db.session.execute(
        text(
            """
                WITH RECURSIVE location_hierarchy AS (
                    SELECT id, parent_id, name, CAST(name AS text) AS path
                    FROM location
                    WHERE parent_id IS NULL
                    UNION ALL
                    SELECT location.id, location.parent_id, location.name, location_hierarchy.path || '/' || location.name 
                    FROM location, location_hierarchy
                    WHERE location.parent_id = location_hierarchy.id
                )
                SELECT id, name FROM location_hierarchy
                WHERE path = :path;
            """
        ),
        {"path": "/".join(path)},
    ).fetchone()


def get_sublocations(location_id: int | None):
    if location_id is None:
        sql = text(
            """
                SELECT id, name
                FROM location
                WHERE parent_id IS NULL;
            """
        )
    else:
        sql = text(
            """
                SELECT id, name
                FROM location
                WHERE parent_id = :location_id;
            """
        )

    return db.session.execute(
        sql,
        {"location_id": location_id},
    ).fetchall()


def create_location(location_name: str, parent_id: int | None):
    db.session.execute(
        text(
            """
                INSERT INTO location (name, parent_id)
                VALUES (:name, :parent_id);
            """
        ),
        {"name": location_name, "parent_id": parent_id},
    )
    db.session.commit()


def get_all_locations():
    locations = db.session.execute(
        text(
            """
                WITH RECURSIVE location_hierarchy AS (
                    SELECT id, parent_id, name, CAST(name AS text) AS path
                    FROM location
                    WHERE parent_id IS NULL
                    UNION ALL
                    SELECT location.id, location.parent_id, location.name, location_hierarchy.path || '/' || location.name 
                    FROM location, location_hierarchy
                    WHERE location.parent_id = location_hierarchy.id
                )
                SELECT id, name, path, parent_id FROM location_hierarchy;
            """
        )
    ).fetchall()
    return [
        {
            "id": location.id,
            "parent_id": location.parent_id,
            "name": location.name,
            "path": location.path,
        }
        for location in locations
    ]

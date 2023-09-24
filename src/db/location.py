from database import db
from sqlalchemy import text


def get_location(path: list[str]):
    return db.session.execute(
        text(
            """
            WITH RECURSIVE location_hierarchy AS (
                SELECT id, parent_id, CAST(name AS text) AS path
                FROM location
                WHERE parent_id IS NULL
                UNION ALL
                SELECT location.id, location.parent_id, 
                    CASE 
                        WHEN location_hierarchy.path = '' 
                        THEN location.name 
                        ELSE location_hierarchy.path || '/' || location.name 
                    END
                FROM location, location_hierarchy
                WHERE location.parent_id = location_hierarchy.id
            )
            SELECT * FROM location_hierarchy
            WHERE path = :path;
            """
        ),
        {"path": "/".join(path)},
    ).fetchone()


def get_sublocations(path: list[str]):
    path_string = "/" + "/".join(path)
    if path_string != "/":
        path_string += "/"

    return db.session.execute(
        text(
            """
            WITH RECURSIVE location_hierarchy AS (
                SELECT id, parent_id, name, '/' || name AS path
                FROM location
                WHERE parent_id IS NULL
                UNION ALL
                SELECT location.id, location.parent_id, location.name, location_hierarchy.path || '/' || location.name
                FROM location, location_hierarchy
                WHERE location.parent_id = location_hierarchy.id
            )
            SELECT * FROM location_hierarchy
            WHERE path ~ ('^' || :path || '[^/]+$');
            """
        ),
        {"path": path_string},
    ).fetchall()


def get_sublocations_by_id(location_id: int | None):
    if location_id is None:
        sql = text(
            """
            SELECT id, parent_id, name
            FROM location
            WHERE parent_id IS NULL;
            """
        )
    else:
        sql = text(
            """
            SELECT id, parent_id, name
            FROM location
            WHERE parent_id = :location_id;
            """
        )

    return db.session.execute(
        sql,
        {"location_id": location_id},
    ).fetchall()


def get_parent_list(location_id):
    result = db.session.execute(
        text(
            """
            WITH RECURSIVE location_hierarchy AS (
                SELECT id, parent_id      
                FROM location
                WHERE id = :location_id
                UNION ALL
                SELECT l.id, l.parent_id        
                FROM location l
                INNER JOIN location_hierarchy ph ON l.id = ph.parent_id
            )
            SELECT * FROM location_hierarchy;
            """
        ),
        {"location_id": location_id},
    )
    return list(map(lambda x: x, result.fetchall()))

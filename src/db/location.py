from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

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


class LocationExistsError(Exception):
    pass


def create_location(location_name: str, parent_id: int | None):
    try:
        try:
            db.session.execute(
                text(
                    """
                        INSERT INTO location (name, parent_id)
                        VALUES (:name, :parent_id);
                    """
                ),
                {"name": location_name, "parent_id": parent_id},
            )
        except IntegrityError:
            raise LocationExistsError()

        db.session.commit()

    except Exception as e:
        db.session.rollback()
        raise e
        # this is thrown also when a slash exists in the path


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


class LocationDoesNotExistError(Exception):
    pass


def edit_location(location_id: int, new_name: str) -> str:
    try:
        location_parent_path = db.session.execute(
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
                    SELECT path FROM location_hierarchy
                    WHERE id = :location_id;
                """
            ),
            {"location_id": location_id},
        ).scalar()

        if location_parent_path is None:
            raise LocationDoesNotExistError()

        try:
            db.session.execute(
                text(
                    """
                        UPDATE location
                        SET name = :new_name
                        WHERE id = :location_id;
                    """
                ),
                {"location_id": location_id, "new_name": new_name},
            )
        except IntegrityError:
            raise LocationExistsError()

        db.session.commit()
        return "/".join(location_parent_path.split("/")[:-1])

    except Exception as e:
        db.session.rollback()
        raise e


def delete_location(location_id: int):
    try:
        db.session.execute(
            text(
                """
                    DELETE FROM location
                    WHERE id = :location_id;
                """
            ),
            {"location_id": location_id},
        )
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e

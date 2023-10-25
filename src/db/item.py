from sqlalchemy import text
from sqlalchemy.exc import DataError, IntegrityError, NoResultFound

from database import db
from db.category import PropertyDoesNotExistOnCategoryError


def get_item_locations(item_id: int):
    locations = db.session.execute(
        text(
            """
                SELECT id, location_id, count
                FROM item_location
                WHERE item_id = :item_id;
            """
        ),
        {"item_id": item_id},
    ).fetchall()

    if len(locations) == 0:
        return []

    paths = db.session.execute(
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
                SELECT id, path FROM location_hierarchy WHERE id IN :location_ids;
            """
        ),
        {"location_ids": tuple([location.location_id for location in locations])},
    ).fetchall()

    return [
        {
            "path": next(
                path.path for path in paths if path.id == location.location_id
            ),
            "count": location.count,
            "id": location.id,
        }
        for location in locations
    ]


def get_item_properties(item_id: int):
    return db.session.execute(
        text(
            """
                SELECT cp.name AS name, ip.value AS value
                FROM item_property ip
                JOIN category_property cp ON ip.category_property_id = cp.id
                WHERE ip.item_id = :item_id;
            """
        ),
        {"item_id": item_id},
    ).fetchall()


def get_item_info(item_id: int):
    return db.session.execute(
        text(
            """
                SELECT id, category_id, name FROM item WHERE id = :item_id
            """
        ),
        {"item_id": item_id},
    ).fetchone()


def create_item_location(item_id: int, location_id: int, count: int):
    db.session.execute(
        text(
            """
                INSERT INTO item_location (item_id, location_id, count)
                VALUES (:item_id, :location_id, :count);
            """
        ),
        {"item_id": item_id, "location_id": location_id, "count": count},
    )
    db.session.commit()


def edit_item_location_count(item_location_id: int, count: int):
    try:
        if count > 0:
            db.session.execute(
                text(
                    """
                            UPDATE item_location SET count = :count WHERE id = :item_location_id;
                        """
                ),
                {"item_location_id": item_location_id, "count": count},
            )
        else:
            db.session.execute(
                text(
                    """
                            DELETE FROM item_location WHERE id = :item_location_id;
                        """
                ),
                {"item_location_id": item_location_id},
            )
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        raise e


class ItemInstanceDoesNotExistError(Exception):
    pass


class MoreItemsThanSourceError(Exception):
    pass


def move_items(item_location_id: int, new_location_id: int, count: int):
    try:
        item_location_info = db.session.execute(
            text(
                """
                    SELECT count, item_id FROM item_location WHERE id = :item_location_id;
                """
            ),
            {"item_location_id": item_location_id},
        ).fetchone()

        if item_location_info is None:
            raise ItemInstanceDoesNotExistError()

        (items_in_current_location, item_id) = item_location_info

        if count > items_in_current_location:
            raise MoreItemsThanSourceError()

        try:
            db.session.execute(
                text(
                    """
                        INSERT INTO item_location (location_id, item_id, count)
                        VALUES (:new_location_id, :item_id, :count)
                        ON CONFLICT (location_id, item_id)
                        DO UPDATE SET count = item_location.count + :count;
                    """
                ),
                {
                    "new_location_id": new_location_id,
                    "item_id": item_id,
                    "count": count,
                },
            )
        except DataError:
            db.session.rollback()
            raise IntegerTooLargeError()

        if count == items_in_current_location:
            db.session.execute(
                text(
                    """
                        DELETE FROM item_location WHERE id = :item_location_id;
                    """
                ),
                {"item_location_id": item_location_id},
            )
        else:
            db.session.execute(
                text(
                    """
                    UPDATE item_location SET count = count - :count WHERE id = :item_location_id;
                """
                ),
                {"item_location_id": item_location_id, "count": count},
            )
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        raise e


class IntegerTooLargeError(Exception):
    pass


class LocationOrItemDoesNotExistError(Exception):
    pass


def add_items(item_id: int, new_location_id: int, count: int):
    try:
        try:
            db.session.execute(
                text(
                    """
                        INSERT INTO item_location (location_id, item_id, count)
                        VALUES (:new_location_id, :item_id, :count)
                        ON CONFLICT (location_id, item_id)
                        DO UPDATE SET count = item_location.count + :count;
                    """
                ),
                {
                    "new_location_id": new_location_id,
                    "item_id": item_id,
                    "count": count,
                },
            )
        except DataError:
            db.session.rollback()
            raise IntegerTooLargeError()
        except IntegrityError:
            db.session.rollback()
            raise LocationOrItemDoesNotExistError()

        db.session.commit()

    except Exception as e:
        db.session.rollback()
        raise e


class CategoryDoesNotExistError(Exception):
    pass


def create_item_and_location(
    item_name: str,
    item_properties: dict[str, str],
    category_id: int,
    location_id: int,
    count: int,
):
    try:
        try:
            item_id = db.session.execute(
                text(
                    """
                        INSERT INTO item (name, category_id)
                        VALUES (:name, :category_id)
                        RETURNING id;
                    """
                ),
                {
                    "name": item_name,
                    "category_id": category_id,
                },
            ).scalar()
        except NoResultFound:
            raise CategoryDoesNotExistError()

        for property_name, property_value in item_properties.items():
            try:
                db.session.execute(
                    text(
                        """
                            INSERT INTO item_property (item_id, category_property_id, value)
                            VALUES (:item_id, (
                                SELECT id
                                FROM category_property
                                WHERE name = :property_name AND category_id = :category_id
                            ), :property_value);
                        """
                    ),
                    {
                        "item_id": item_id,
                        "property_name": property_name,
                        "category_id": category_id,
                        "property_value": property_value,
                    },
                )
            except IntegrityError:
                raise PropertyDoesNotExistOnCategoryError()

        db.session.execute(
            text(
                """
                    INSERT INTO item_location (item_id, location_id, count)
                    VALUES (:item_id, :location_id, :count);
                """
            ),
            {"item_id": item_id, "location_id": location_id, "count": count},
        )

        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e


def get_items_in_location(location_id: int):
    return db.session.execute(
        text(
            """
                WITH RECURSIVE category_hierarchy AS (
                    SELECT id, parent_id, name, CAST(name AS text) AS path
                    FROM category
                    WHERE parent_id IS NULL
                    UNION ALL
                    SELECT category.id, category.parent_id, category.name, category_hierarchy.path || '/' || category.name
                    FROM category, category_hierarchy
                    WHERE category.parent_id = category_hierarchy.id
                )
                SELECT
                    ii.id AS id,
                    i.id AS item_id,
                    i.category_id AS category_id,
                    c.name AS category_name,
                    i.name AS item_name,
                    ii.location_id AS location_id,
                    ii.count AS count,
                    ch.path AS category_path
                FROM item_location ii
                JOIN item i ON ii.item_id = i.id
                JOIN category c ON i.category_id = c.id
                JOIN category_hierarchy ch ON c.id = ch.id
                WHERE ii.location_id = :location_id;
            """
        ),
        {"location_id": location_id},
    ).fetchall()


def get_items_in_category(category_id: int):
    items_result = db.session.execute(
        text(
            """
                SELECT item.id AS id, item.name AS name, COALESCE(SUM(item_location.count), 0) AS total_count
                FROM item
                LEFT JOIN item_location ON item.id = item_location.item_id
                WHERE item.category_id = :category_id
                GROUP BY item.id, item.name;
            """
        ),
        {"category_id": category_id},
    ).fetchall()

    items_with_properties = []
    for item in items_result:
        properties_result = db.session.execute(
            text(
                """
                    SELECT value
                    FROM item_property
                    WHERE item_id = :item_id;
                """
            ),
            {"item_id": item.id},
        ).fetchall()

        item_properties = [property.value for property in properties_result]
        item = {"id": item.id, "name": item.name, "total_count": item.total_count}
        item["properties"] = item_properties
        items_with_properties.append(item)

    return items_with_properties


def edit_properties(item_id: int, properties: dict):
    try:
        for property_name, property_value in properties.items():
            try:
                db.session.execute(
                    text(
                        """
                            INSERT INTO item_property (item_id, category_property_id, value)
                            VALUES (:item_id, (
                                SELECT id
                                FROM category_property
                                WHERE name = :property_name AND category_id = (
                                    SELECT category_id
                                    FROM item
                                    WHERE id = :item_id
                                )
                            ), :property_value)
                            ON CONFLICT (item_id, category_property_id)
                            DO UPDATE SET value = :property_value;
                        """
                    ),
                    {
                        "item_id": item_id,
                        "property_name": property_name,
                        "property_value": property_value,
                    },
                )
            except IntegrityError:
                raise PropertyDoesNotExistOnCategoryError()

        db.session.commit()

    except Exception as e:
        db.session.rollback()
        raise e

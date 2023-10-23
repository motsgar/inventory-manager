from sqlalchemy import text

from database import db


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


def move_items(item_location_id: int, new_location_id: int, count: int):
    item_location_info = db.session.execute(
        text(
            """
                SELECT count, item_id FROM item_location WHERE id = :item_location_id;
            """
        ),
        {"item_location_id": item_location_id},
    ).fetchone()

    if item_location_info is None:
        raise Exception("No item location with id found")

    (items_in_current_location, item_id) = item_location_info

    if count > items_in_current_location:
        raise Exception("Tried to move more items than source has")

    db.session.execute(
        text(
            """
                INSERT INTO item_location (location_id, item_id, count)
                VALUES (:new_location_id, :item_id, :count)
                ON CONFLICT (location_id, item_id)
                DO UPDATE SET count = item_location.count + :count;
            """
        ),
        {"new_location_id": new_location_id, "item_id": item_id, "count": count},
    )

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


def add_items(item_id: int, new_location_id: int, count: int):
    db.session.execute(
        text(
            """
                INSERT INTO item_location (location_id, item_id, count)
                VALUES (:new_location_id, :item_id, :count)
                ON CONFLICT (location_id, item_id)
                DO UPDATE SET count = item_location.count + :count;
            """
        ),
        {"new_location_id": new_location_id, "item_id": item_id, "count": count},
    )
    db.session.commit()


def create_item_and_location(
    item_name: str,
    item_properties: dict[str, str],
    category_id: int,
    location_id: int,
    count: int,
):
    item_insert_result = db.session.execute(
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
    )
    item_id = item_insert_result.scalar()

    for property_name, property_value in item_properties.items():
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


def get_items_in_location(location_id: int):
    return db.session.execute(
        text(
            """
                SELECT ii.id AS id, i.id AS item_id, i.category_id as category_id, i.name AS name,
                    ii.location_id AS location_id, ii.count AS count
                FROM item_location ii
                JOIN item i ON ii.item_id = i.id
                WHERE ii.location_id = :location_id;
            """
        ),
        {"location_id": location_id},
    ).fetchall()


def get_items_in_category(category_id: int):
    return db.session.execute(
        text(
            """
                SELECT item.id, item.name, COALESCE(SUM(item_location.count), 0) AS total_count
                FROM item
                LEFT JOIN item_location ON item.id = item_location.item_id
                WHERE item.category_id = :category_id
                GROUP BY item.id, item.name;
            """
        ),
        {"category_id": category_id},
    ).fetchall()

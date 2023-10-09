from sqlalchemy import text

from database import db


def get_items(item_id: int):
    return db.session.execute(
        text(
            """
                SELECT id, location_id, count
                FROM item_location
                WHERE item_id = :item_id;
            """
        ),
        {"item_id": item_id},
    ).fetchall()


def create_item_location(item_id: int, location_id: int, count: int):
    return db.session.execute(
        text(
            """
                INSERT INTO item_location (item_id, location_id, count)
                VALUES (:item_id, :location_id, :count);
            """
        ),
        {"item_id": item_id, "location_id": location_id, "count": count},
    )


def create_item_and_location(
    item_name: str,
    item_properties: dict[str, str],
    category_name: int,
    location_path: str,
    count: int,
):
    with db.session.begin():
        category_id = db.session.execute(
            text(
                """
                    SELECT id
                    FROM category
                    WHERE name = :category_name;
                """
            ),
            {"category_name": category_name},
        ).scalar()

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
            print(property_name, property_value)
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

        location_id = db.session.execute(
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
                    SELECT id FROM location_hierarchy
                    WHERE path = :path;
                """
            ),
            {"path": location_path},
        ).scalar()

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
                SELECT i.id AS id, i.category_id as category_id, i.name AS name,
                    ii.location_id AS location_id, ii.count AS count
                FROM item_location ii
                JOIN item i ON ii.item_id = i.id
                WHERE ii.location_id = :location_id;
            """
        ),
        {"location_id": location_id},
    ).fetchall()

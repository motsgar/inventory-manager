from sqlalchemy import text

from database import db


def get_category(path: list[str]):
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
                SELECT id, name FROM category_hierarchy
                WHERE path = :path;
            """
        ),
        {"path": "/".join(path)},
    ).fetchone()


def get_subcategories(category_id: int | None):
    if category_id is None:
        sql = text(
            """
                SELECT id, name
                FROM category
                WHERE parent_id IS NULL;
            """
        )
    else:
        sql = text(
            """
                SELECT id, name
                FROM category
                WHERE parent_id = :category_id;
            """
        )

    return db.session.execute(
        sql,
        {"category_id": category_id},
    ).fetchall()


def get_all_categories():
    categories = db.session.execute(
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
                SELECT id, name, path, parent_id FROM category_hierarchy;
            """
        )
    ).fetchall()
    return [
        {
            "id": category.id,
            "parent_id": category.parent_id,
            "name": category.name,
            "path": category.path,
        }
        for category in categories
    ]


def get_category_properties(category_id: int):
    result = db.session.execute(
        text(
            """
                SELECT name
                FROM category_property
                WHERE category_id = :category_id;
            """
        ),
        {"category_id": category_id},
    ).fetchall()

    return [row.name for row in result]


def create_category(category_name: str, parent_id: int | None, properties: list[str]):
    new_category_id = db.session.execute(
        text(
            """
                INSERT INTO category (name, parent_id)
                VALUES (:name, :parent_id)
                RETURNING id;
            """
        ),
        {"name": category_name, "parent_id": parent_id},
    ).scalar()

    for property_name in properties:
        db.session.execute(
            text(
                """
                INSERT INTO category_property (category_id, name)
                VALUES (:category_id, :property_name);
                """
            ),
            {"category_id": new_category_id, "property_name": property_name},
        )

    db.session.commit()

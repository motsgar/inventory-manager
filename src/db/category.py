from sqlalchemy import text

from database import db


def get_categories():
    return db.session.execute(
        text(
            """
                SELECT id, name
                FROM category;
            """
        )
    ).fetchall()


def get_category_properties(category_name: str):
    result = db.session.execute(
        text(
            """
                SELECT name
                FROM category_property
                WHERE category_id = (
                    SELECT id
                    FROM category
                    WHERE name = :category_name
                );
            """
        ),
        {"category_name": category_name},
    ).fetchall()

    return [row.name for row in result]

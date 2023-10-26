import random
import string

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

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


class CategoryExistsError(Exception):
    pass


def create_category(category_name: str, parent_id: int | None, properties: list[str]):
    try:
        try:
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
        except IntegrityError:
            db.session.rollback()
            raise CategoryExistsError()
            # this is thrown also when a slash exists in the path

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

    except Exception as e:
        db.session.rollback()
        raise e


class PropertyDoesNotExistOnCategoryError(Exception):
    pass


class DuplicatePropertyNameError(Exception):
    pass


def edit_category_properties(category_id: int, properties: dict):
    # update each property name to the new name without breaking unique constraints if 2 names swap using a single sql query
    # first update all properties to a temporary random name returning the id and the old name
    # then update all properties to the new name using the id and the old name
    try:
        name_id_pairs = {}

        for old_name, new_name in properties.items():
            random_name = "".join(
                random.choices(string.ascii_uppercase + string.digits, k=30)
            )

            name_id_pairs[old_name] = db.session.execute(
                text(
                    """
                        UPDATE category_property
                        SET name = :temp_name
                        WHERE category_id = :category_id AND name = :old_name
                        RETURNING id;
                    """
                ),
                {
                    "temp_name": random_name,
                    "category_id": category_id,
                    "old_name": old_name,
                },
            ).fetchone()
            if name_id_pairs[old_name] is None:
                raise PropertyDoesNotExistOnCategoryError()

        for old_name, new_name in properties.items():
            try:
                db.session.execute(
                    text(
                        """
                            UPDATE category_property
                            SET name = :new_name
                            WHERE id = :id;
                        """
                    ),
                    {"new_name": new_name, "id": name_id_pairs[old_name].id},
                )
            except IntegrityError:
                raise DuplicatePropertyNameError()

        db.session.commit()

    except Exception as e:
        db.session.rollback()
        raise e


class CategoryDoesNotExistError(Exception):
    pass


def edit_category(category_id: int, new_name: str) -> str:
    try:
        category_parent_path = db.session.execute(
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
                    SELECT path FROM category_hierarchy
                    WHERE id = :category_id;
                """
            ),
            {"category_id": category_id},
        ).scalar()

        if category_parent_path is None:
            raise CategoryDoesNotExistError()

        try:
            db.session.execute(
                text(
                    """
                        UPDATE category
                        SET name = :new_name
                        WHERE id = :category_id;
                    """
                ),
                {"category_id": category_id, "new_name": new_name},
            )
        except IntegrityError:
            raise CategoryExistsError()

        db.session.commit()
        return "/".join(category_parent_path.split("/")[:-1])

    except Exception as e:
        db.session.rollback()
        raise e


def delete_category(category_id: int):
    try:
        db.session.execute(
            text(
                """
                    DELETE FROM category
                    WHERE id = :category_id;
                """
            ),
            {"category_id": category_id},
        )
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e

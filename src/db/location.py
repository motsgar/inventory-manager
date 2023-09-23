from database import db
from sqlalchemy import text


def get_sublocations(location_id):
    result = db.session.execute(
        text("SELECT * FROM location WHERE parent_id = :location_id"),
        {"location_id": location_id},
    )
    return list(map(lambda x: x.data, result.fetchall()))


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

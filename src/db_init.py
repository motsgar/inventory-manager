import os

from sqlalchemy import create_engine, text

engine = create_engine(os.getenv("DATABASE_URL"))
db = engine.connect()


with open("schema.sql", "r") as f:
    db.execute(text(f.read()))
    db.commit()

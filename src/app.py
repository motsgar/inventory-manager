import os

from flask import Flask

from database import db
from routes import category, index, item, location

app = Flask(__name__, template_folder="templates")
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
db.init_app(app)

app.register_blueprint(index.index_bp)
app.register_blueprint(location.location_bp)
app.register_blueprint(location.location_api_bp)
app.register_blueprint(category.category_api_bp)
app.register_blueprint(item.item_bp)

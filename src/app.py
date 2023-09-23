from flask import Flask
from database import db
from routes import index


app = Flask(__name__, template_folder="templates")
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config[
    "SQLALCHEMY_DATABASE_URI"
] = "postgresql://postgres:inventorypassword@localhost/postgres"
db.init_app(app)

app.register_blueprint(index.index_bp)

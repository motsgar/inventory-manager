import os

from flask import Flask, redirect
from werkzeug.middleware.proxy_fix import ProxyFix

from database import db
from routes import category, item, location

app = Flask(__name__, template_folder="templates")

app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1)

app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["PREFERRED_URL_SCHEME"] = "https"
app.config["APPLICATION_ROOT"] = "/"

db.init_app(app)


@app.route("/")
def index():
    return redirect("/location")


app.register_blueprint(location.location_bp)
app.register_blueprint(location.location_api_bp)
app.register_blueprint(category.category_bp)
app.register_blueprint(category.category_api_bp)
app.register_blueprint(item.item_bp)

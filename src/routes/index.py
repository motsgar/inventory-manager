from flask import Blueprint, render_template
from db.location import get_parent_list

index_bp = Blueprint("index", __name__)


@index_bp.route("/")
def index() -> str:
    locations = get_parent_list(5)

    return render_template("index.html", locations=locations)

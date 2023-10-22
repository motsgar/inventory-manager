from flask import Blueprint, redirect, render_template, request, url_for

from db.category import get_categories
from db.item import get_items_in_location
from db.location import (
    create_location,
    get_all_locations,
    get_location,
    get_sublocations,
)

location_bp = Blueprint("location", __name__, url_prefix="/location")
location_api_bp = Blueprint("location_api", __name__, url_prefix="/api/location")


def parse_path(raw_path: str) -> list[str]:
    if raw_path == "":
        return []
    else:
        return raw_path.split("/")


@location_api_bp.route("/all")
def fetch_locations():
    locations = get_all_locations()
    return locations


@location_bp.route("/", defaults={"raw_path": ""})
@location_bp.route("/<path:raw_path>/")
def location(raw_path):
    path = parse_path(raw_path)

    if len(path) == 0:
        location_info = None
        child_locations = get_sublocations(None)
        items = None
    else:
        location_info = get_location(path)
        if location_info is None:
            return (
                render_template(
                    "location.html",
                    not_found=True,
                ),
                404,
            )
        child_locations = get_sublocations(location_info.id)
        items = get_items_in_location(location_info.id)

    categories = get_categories()

    return render_template(
        "location.html",
        path=path,
        sublocations=child_locations,
        items=items,
        location_info=location_info,
        categories=[category.name for category in categories],
    )


@location_bp.route("/", defaults={"raw_path": ""}, methods=["POST"])
@location_bp.route("/<path:raw_path>/", methods=["POST"])
def new_location(raw_path):
    path = parse_path(raw_path)

    if len(path) == 0:
        parent_id = None
    else:
        parent_id = get_location(path).id

    location_name = request.form["name"]

    create_location(location_name, parent_id)

    return redirect(url_for("location.location", raw_path=raw_path))

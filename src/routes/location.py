from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from sqlalchemy.exc import IntegrityError

from db.item import (
    CategoryDoesNotExistError,
    PropertyDoesNotExistOnCategoryError,
    add_items,
    create_item_and_location,
    get_items_in_location,
)
from db.location import (
    LocationExistsError,
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
                    "not_found.html",
                    error_message="Location not found",
                    solve_message="To base location",
                    base_path="/location/",
                ),
                404,
            )
        child_locations = get_sublocations(location_info.id)
        items = get_items_in_location(location_info.id)

    return render_template(
        "location.html",
        path=path,
        sublocations=child_locations,
        items=items,
        location_info=location_info,
    )


def route_new_location():
    try:
        location_id = int(request.form["location-id"])
        location_name = request.form["name"]
    except KeyError:
        abort(400)
    except ValueError:
        abort(400)

    try:
        create_location(location_name, location_id)
    except LocationExistsError:
        flash("A location with that name already exists in current path", "error")


def route_new_item():
    try:
        properties = {}
        for key, value in request.form.items():
            if key.startswith("property."):
                properties[key[9:]] = value

        name = request.form["name"]
        count = int(request.form["count"])
        if count < 1 or count > 2147483647:
            abort(400)
        category_id = int(request.form["category-id"])
        location_id = int(request.form["location-id"])
    except KeyError:
        abort(400)
    except ValueError:
        abort(400)

    try:
        create_item_and_location(
            name,
            properties,
            category_id,
            location_id,
            count,
        )
    except CategoryDoesNotExistError:
        flash("Tried to create a item for a non existent category", "error")
    except PropertyDoesNotExistOnCategoryError:
        flash(
            "Tried to create a item with a property that does not exist on the category",
            "error",
        )


@location_bp.route("/", defaults={"raw_path": ""}, methods=["POST"])
@location_bp.route("/<path:raw_path>/", methods=["POST"])
def new_location(raw_path):
    action = request.form.get("action")

    if action == "new-location":
        route_new_location()
    elif action == "new-item":
        route_new_item()
    else:
        abort(400)

    return redirect(request.path)

from flask import Blueprint, abort, flash, redirect, render_template, request

from db.item import get_items_in_location
from db.location import (
    LocationExistsError,
    create_location,
    delete_location,
    edit_location,
    get_all_locations,
    get_location,
    get_sublocations,
)
from routes.item import route_new_item

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


def route_edit_location():
    try:
        location_id = int(request.form["location-id"])
        new_name = request.form["name"]
    except KeyError:
        abort(400)
    except ValueError:
        abort(400)

    new_name = new_name.strip()

    if new_name == "":
        flash("Location name cannot be empty", "error")
        return

    if "/" in new_name:
        flash("Location name cannot contain a slash", "error")
        return

    try:
        parent_location_path = edit_location(location_id, new_name)
        return "/location/" + parent_location_path + "/" + new_name + "/"
    except LocationExistsError:
        flash("A location with that name already exists in current path", "error")


def route_delete_location():
    try:
        location_id = int(request.form["location-id"])
    except KeyError:
        abort(400)
    except ValueError:
        abort(400)

    # Nothing can go wrong here
    delete_location(location_id)


def route_new_location():
    try:
        location_id_str = request.form["location-id"]
        if location_id_str == "":
            location_id = None
        else:
            location_id = int(location_id_str)
        location_name = request.form["name"]
    except KeyError:
        abort(400)
    except ValueError:
        abort(400)

    location_name = location_name.strip()

    if location_name == "":
        flash("Location name cannot be empty", "error")
        return

    if "/" in location_name:
        flash("Location name cannot contain a slash", "error")
        return

    try:
        create_location(location_name, location_id)
    except LocationExistsError:
        flash("A location with that name already exists in current path", "error")


@location_bp.route("/", defaults={"raw_path": ""}, methods=["POST"])
@location_bp.route("/<path:raw_path>/", methods=["POST"])
def new_location(raw_path):
    action = request.form.get("action")

    if action == "edit-location":
        new_location_path = route_edit_location()
        if new_location_path is not None:
            return redirect(new_location_path)
    elif action == "delete-location":
        route_delete_location()
    elif action == "new-location":
        route_new_location()
    elif action == "new-item":
        route_new_item()
    else:
        abort(400)

    return redirect(request.path)

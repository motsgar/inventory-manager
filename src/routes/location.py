from flask import Blueprint, redirect, render_template, request, url_for
from db.location import (
    create_location,
    get_location,
    get_sublocations,
)

location_bp = Blueprint("location", __name__)


def parse_path(raw_path: str) -> list[str]:
    if raw_path == "":
        return []
    else:
        return raw_path.split("/")


@location_bp.route("/", defaults={"raw_path": ""})
@location_bp.route("/<path:raw_path>/")
def location(raw_path):
    path = parse_path(raw_path)

    if len(path) == 0:
        location_info = None
        child_locations = get_sublocations(None)
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

    return render_template(
        "location.html",
        path=path,
        sublocations=child_locations,
        location_info=location_info,
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

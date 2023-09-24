from flask import Blueprint, render_template
from db.location import (
    get_location,
    get_parent_list,
    get_sublocations,
    get_sublocations_by_id,
)

location_bp = Blueprint("location", __name__)


@location_bp.route("/", defaults={"raw_path": ""})
@location_bp.route("/<path:raw_path>/")
def location(raw_path) -> str:
    if raw_path == "":
        path = []
    else:
        path = raw_path.split("/")

    if len(path) == 0:
        location_info = None
        child_locations = get_sublocations_by_id(None)
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
        child_locations = get_sublocations_by_id(location_info.id)

    return render_template(
        "location.html", sublocations=child_locations, location_info=location_info
    )

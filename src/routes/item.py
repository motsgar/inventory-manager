from flask import Blueprint, abort, redirect, render_template, request

from db.item import (
    add_items,
    create_item_and_location,
    edit_item_location_count,
    edit_properties,
    get_item_info,
    get_item_locations,
    get_item_properties,
    move_items,
)

item_bp = Blueprint("item", __name__, url_prefix="/item")


@item_bp.route("/<int:item_id>/")
def item(item_id):
    item_info = get_item_info(item_id)
    if item_info is None:
        abort(404)
    locations = get_item_locations(item_id)
    properties = get_item_properties(item_id)

    return render_template(
        "item.html",
        locations=sorted(locations, key=lambda location: location["path"]),
        properties=properties,
        item_info=item_info,
    )


@item_bp.route("/<int:item_id>/", methods=["POST"])
def item_new(item_id):
    action = request.args.get("action")

    if action == "new":
        count_str = request.form.get("count")
        location_str = request.form.get("location")
        if count_str is None or location_str is None:
            abort(404)

        count = int(count_str)
        new_location_id = int(location_str)

        add_items(item_id, new_location_id, count)

    elif action == "edit":
        properties = {}
        for key, value in request.form.items():
            if key.startswith("property."):
                properties[key[9:]] = value

        edit_properties(item_id, properties)

    return redirect(request.referrer)


@item_bp.route("/<int:item_id>/<int:item_location_id>/", methods=["POST"])
def item_action(item_id, item_location_id: int):
    action = request.args.get("action")

    if action == "edit":
        count_str = request.form.get("count")
        if count_str is None:
            abort(404)

        count = int(count_str)

        edit_item_location_count(item_location_id, count)
    elif action == "move":
        count_str = request.form.get("count")
        location_str = request.form.get("location")
        if count_str is None or location_str is None:
            abort(404)

        count = int(count_str)
        new_location_id = int(location_str)

        move_items(item_location_id, new_location_id, count)

    return redirect(request.referrer)


@item_bp.route("/", methods=["POST"])
def new_item():
    properties = {}
    for key, value in request.form.items():
        if key.startswith("property."):
            properties[key[9:]] = value

    create_item_and_location(
        request.form["name"],
        properties,
        request.form["category-id"],
        request.form["location-id"],
        request.form["count"],
    )
    return redirect(request.referrer)

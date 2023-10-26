from flask import Blueprint, abort, flash, redirect, render_template, request

from db.category import PropertyDoesNotExistOnCategoryError
from db.item import (
    CategoryDoesNotExistError,
    IntegerTooLargeError,
    ItemInstanceDoesNotExistError,
    LocationOrItemDoesNotExistError,
    MoreItemsThanSourceError,
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
        return (
            render_template(
                "not_found.html",
                error_message="Item not found",
                solve_message="To location browsing",
                base_path="/location/",
            ),
            404,
        )
    locations = get_item_locations(item_id)
    properties = get_item_properties(item_id)

    return render_template(
        "item.html",
        locations=sorted(locations, key=lambda location: location["path"]),
        properties=properties,
        item_info=item_info,
    )


def route_edit_item_properties(item_id: int):
    properties = {}
    for key, value in request.form.items():
        if key.startswith("property."):
            properties[key[9:]] = value.strip()

    try:
        edit_properties(item_id, properties)
    except PropertyDoesNotExistOnCategoryError:
        flash(
            "Tried to edit a item property that does not exist on the category of the item",
            "error",
        )


def route_add_item_instances(item_id: int):
    try:
        count = int(request.form["count"])
        if count < 1 or count > 2147483647:
            abort(400)
        location_id = int(request.form["location-id"])
    except KeyError:
        abort(400)
    except ValueError:
        abort(400)

    try:
        add_items(item_id, location_id, count)
    except IntegerTooLargeError:
        flash(
            "The total amount of items in one location exceded the limit of 2147483647 items",
            "error",
        )
    except LocationOrItemDoesNotExistError:
        flash("Tried to add item instances to a non existent location or item", "error")


def route_edit_item_instance_count():
    try:
        count = int(request.form["count"])
        if count < 0 or count > 2147483647:
            abort(400)
        item_instance_id = int(request.form["item-instance-id"])
    except KeyError:
        abort(400)
    except ValueError:
        abort(400)

    # Nothing can go wrong here
    edit_item_location_count(item_instance_id, count)


def route_move_item_instance():
    try:
        count = int(request.form["count"])
        if count < 1 or count > 2147483647:
            abort(400)
        item_instance_id = int(request.form["item-instance-id"])
        location_id = int(request.form["location-id"])
    except KeyError:
        abort(400)
    except ValueError:
        abort(400)

    try:
        move_items(item_instance_id, location_id, count)
    except IntegerTooLargeError:
        flash(
            "The total amount of items in one location exceded the limit of 2147483647 items",
            "error",
        )
    except ItemInstanceDoesNotExistError:
        flash("Tried to move a non existent item instance", "error")
    except MoreItemsThanSourceError:
        flash("Tried to move more items than the source has", "error")


@item_bp.route("/<int:item_id>/", methods=["POST"])
def item_new(item_id):
    action = request.form.get("action")

    if action == "edit-item-properties":
        route_edit_item_properties(item_id)
    elif action == "add-item-instance":
        route_add_item_instances(item_id)
    elif action == "edit-item-instance-count":
        route_edit_item_instance_count()
    elif action == "move-item-instance":
        route_move_item_instance()
    else:
        abort(400)

    return redirect(request.path)


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

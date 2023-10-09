from flask import Blueprint, redirect, render_template, request, url_for

from db.item import create_item_and_location

item_bp = Blueprint("item", __name__, url_prefix="/item")


@item_bp.route("/", methods=["POST"])
def new_item():
    properties = {}
    for key, value in request.form.items():
        print(key, value)
        if key.startswith("property."):
            properties[key[9:]] = value

    create_item_and_location(
        request.form["name"],
        properties,
        request.form["category"],
        request.form["location"],
        request.form["count"],
    )
    return redirect(request.referrer)

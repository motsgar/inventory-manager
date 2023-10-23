from flask import Blueprint, abort, redirect, render_template, request, url_for

from db.category import (
    create_category,
    get_all_categories,
    get_category,
    get_category_properties,
    get_subcategories,
)
from db.item import get_items_in_category

category_bp = Blueprint("category", __name__, url_prefix="/category")
category_api_bp = Blueprint("category_api", __name__, url_prefix="/api/category")


def parse_path(raw_path: str) -> list[str]:
    if raw_path == "":
        return []
    else:
        return raw_path.split("/")


@category_api_bp.route("/properties/<int:category_id>")
def get_properties(category_id):
    properties = get_category_properties(category_id)
    return properties


@category_api_bp.route("/all")
def get_categories():
    categories = get_all_categories()
    return categories


@category_bp.route("/", defaults={"raw_path": ""})
@category_bp.route("/<path:raw_path>/")
def location(raw_path):
    path = parse_path(raw_path)

    if len(path) == 0:
        category_info = None
        child_categories = get_subcategories(None)
        items = None
        category_properties = None
    else:
        category_info = get_category(path)
        if category_info is None:
            abort(404)
        child_categories = get_subcategories(category_info.id)
        items = get_items_in_category(category_info.id)
        category_properties = get_category_properties(category_info.id)

    return render_template(
        "category.html",
        path=path,
        subcategories=child_categories,
        items=items,
        category_info=category_info,
        category_properties=category_properties,
    )


@category_bp.route("/", defaults={"raw_path": ""}, methods=["POST"])
@category_bp.route("/<path:raw_path>/", methods=["POST"])
def new_location(raw_path):
    path = parse_path(raw_path)

    if len(path) == 0:
        parent_id = None
    else:
        parent_category = get_category(path)
        if parent_category is None:
            return (
                render_template(
                    "category.html",
                    not_found=True,
                ),
                404,
            )

        parent_id = parent_category.id

    name = request.form.get("name")
    properties = request.form.getlist("category-property-name")

    if name is None or properties is None:
        abort(404)

    create_category(name, parent_id, properties)

    return redirect(request.referrer)

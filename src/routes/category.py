from flask import Blueprint, abort, flash, redirect, render_template, request

from db.category import (
    CategoryExistsError,
    DuplicatePropertyNameError,
    PropertyDoesNotExistOnCategoryError,
    create_category,
    delete_category,
    edit_category,
    edit_category_properties,
    get_all_categories,
    get_category,
    get_category_properties,
    get_subcategories,
)
from db.item import get_items_in_category
from routes.item import route_new_item

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
def category(raw_path):
    path = parse_path(raw_path)

    if len(path) == 0:
        category_info = None
        child_categories = get_subcategories(None)
        items = None
        category_properties = None
    else:
        category_info = get_category(path)
        if category_info is None:
            return (
                render_template(
                    "not_found.html",
                    error_message="Category not found",
                    solve_message="To base category",
                    base_path="/category/",
                ),
                404,
            )
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


def route_edit_category():
    try:
        category_id = int(request.form["category-id"])
        new_name = request.form["name"]
    except KeyError:
        abort(400)
    except ValueError:
        abort(400)

    new_name = new_name.strip()

    if new_name == "":
        flash("Category name cannot be empty", "error")
        return

    if "/" in new_name:
        flash("Category name cannot contain a slash", "error")
        return

    try:
        parent_category_path = edit_category(category_id, new_name)
        return "/location/" + parent_category_path + "/" + new_name + "/"
    except CategoryExistsError:
        flash("A category with that name already exists in current path", "error")


def route_delete_category():
    try:
        category_id = int(request.form["category-id"])
    except KeyError:
        abort(400)
    except ValueError:
        abort(400)

    # Nothing can go wrong here
    delete_category(category_id)


def route_new_subcategory():
    print(request.form)
    try:
        category_id_str = request.form["category-id"]
        if category_id_str == "":
            category_id = None
        else:
            category_id = int(category_id_str)
        category_name = request.form["name"]
        properties = request.form.getlist("category-property-name")
    except KeyError:
        abort(400)
    except ValueError:
        abort(400)

    category_name = category_name.strip()

    original_length = len(properties)
    properties = list(set([property.strip() for property in properties]))
    if len(properties) != original_length:
        flash("Duplicate properties are not allowed", "error")
        return
    for property in properties:
        if property == "":
            flash("Property name cannot be empty", "error")
            return

    if category_name == "":
        flash("Category name cannot be empty", "error")
        return

    if "/" in category_name:
        flash("Category name cannot contain a slash", "error")
        return

    try:
        create_category(category_name, category_id, properties)
    except CategoryExistsError:
        flash("A category with that name already exists in current path", "error")


def route_edit_properties():
    try:
        category_id = int(request.form["category-id"])
    except KeyError:
        abort(400)
    except ValueError:
        abort(400)

    properties = {}
    for key, value in request.form.items():
        if key.startswith("property."):
            properties[key[9:]] = value.strip()

    try:
        edit_category_properties(category_id, properties)
    except PropertyDoesNotExistOnCategoryError:
        flash("Tried to change the name of a non existent property", "error")
    except DuplicatePropertyNameError:
        flash("Tried to set name of two properties to the same value", "error")


@category_bp.route("/", defaults={"raw_path": ""}, methods=["POST"])
@category_bp.route("/<path:raw_path>/", methods=["POST"])
def new_category(raw_path):
    action = request.form.get("action")

    if action == "edit-category":
        new_category_path = route_edit_category()
        if new_category_path is not None:
            return redirect(new_category_path)
    elif action == "delete-category":
        route_delete_category()
    elif action == "new-subcategory":
        route_new_subcategory()
    elif action == "edit-properties":
        route_edit_properties()
    elif action == "new-item":
        route_new_item()
    else:
        abort(400)

    return redirect(request.path)

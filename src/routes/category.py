from flask import Blueprint, redirect, render_template, request, url_for

from db.category import get_category_properties

category_api_bp = Blueprint("category", __name__, url_prefix="/api/category")


@category_api_bp.route("/properties/<string:category_name>")
def get_properties(category_name):
    properties = get_category_properties(category_name)
    return properties

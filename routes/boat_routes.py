"""Customer-facing boat browsing routes."""

from flask import Blueprint, abort, render_template

from services.boat_service import BoatCatalog


boats_bp = Blueprint("boats", __name__, url_prefix="/boats")


@boats_bp.get("/")
def list_boats():
    boats = BoatCatalog().available_boats()
    return render_template("boats.html", boats=boats)


@boats_bp.get("/<int:boat_id>")
def boat_details(boat_id):
    boat = BoatCatalog().find_boat(boat_id)
    if boat is None:
        abort(404)
    return render_template("boat_details.html", boat=boat)

"""Public destination browsing routes."""
from flask import Blueprint, abort, render_template
from models.destination import Destination
from services.destination_image_service import destination_image_catalog
from services.destination_content_service import destination_content_catalog

destinations_bp = Blueprint("destinations", __name__, url_prefix="/destinations")

@destinations_bp.get("/")
def index():
    destinations = Destination.query.filter_by(is_active=True).order_by(Destination.municipality, Destination.name).all()
    groups = {"Infanta Nearby": [], "Baluti Island": [], "Burdeos": [], "Polillo": [], "Panukulan": []}
    for destination in destinations:
        name = destination.name.lower()
        municipality = destination.municipality.lower()
        if "baluti" in name:
            groups["Baluti Island"].append(destination)
        elif municipality in {"infanta", "general nakar"}:
            groups["Infanta Nearby"].append(destination)
        elif municipality == "burdeos":
            groups["Burdeos"].append(destination)
        elif municipality in {"polillo", "polilio"}:
            groups["Polillo"].append(destination)
        elif municipality == "panukulan":
            groups["Panukulan"].append(destination)
        else:
            groups.setdefault(destination.municipality, []).append(destination)
    destination_groups = [(name, items) for name, items in groups.items() if items]
    return render_template(
        "destinations.html",
        destination_groups=destination_groups,
        destination_image=destination_image_catalog.get,
        destination_content=destination_content_catalog.get,
    )

@destinations_bp.get("/<int:destination_id>")
def details(destination_id):
    destination = Destination.query.filter_by(id=destination_id, is_active=True).first()
    if destination is None:
        abort(404)
    return render_template(
        "destination_details.html",
        destination=destination,
        image_record=destination_image_catalog.get(destination.name),
        destination_content=destination_content_catalog.get(destination.name),
    )


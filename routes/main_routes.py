"""Public informational pages and visitor inquiries."""

import re
import time

from flask import Blueprint, flash, redirect, render_template, request, url_for
from sqlalchemy.exc import SQLAlchemyError

from extensions import db
from models.contact_inquiry import ContactInquiry
from services.destination_image_service import destination_image_catalog


main_bp = Blueprint("main", __name__)
_inquiry_attempts = {}


@main_bp.get("/about")
def about():
    image = destination_image_catalog.get("Dero Beach")
    return render_template("about.html", hero_image=image)


@main_bp.route("/contact", methods=["GET", "POST"])
def contact():
    inquiry_types = (
        "Destination Inquiry",
        "Boat Rental Inquiry",
        "Existing Reservation",
        "General Question",
    )
    values = request.form if request.method == "POST" else {}
    if request.method == "POST":
        client_key = request.remote_addr or "unknown"
        now = time.monotonic()
        recent_attempts = [stamp for stamp in _inquiry_attempts.get(client_key, []) if now - stamp < 60]
        if len(recent_attempts) >= 3:
            flash("Please wait a moment before sending another inquiry.", "warning")
            return render_template("contact.html", inquiry_types=inquiry_types, values=request.form), 429
        recent_attempts.append(now)
        _inquiry_attempts[client_key] = recent_attempts
        full_name = " ".join(request.form.get("full_name", "").split())
        email = request.form.get("email", "").strip().lower()
        inquiry_type = request.form.get("inquiry_type", "").strip()
        booking_reference = request.form.get("booking_reference", "").strip().upper()
        message = request.form.get("message", "").strip()
        errors = []
        if not 2 <= len(full_name) <= 150:
            errors.append("Enter your full name.")
        if not re.fullmatch(r"[^@\s]{1,100}@[^@\s]{1,100}\.[^@\s]{2,30}", email):
            errors.append("Enter a valid email address.")
        if inquiry_type not in inquiry_types:
            errors.append("Choose a valid inquiry type.")
        if len(booking_reference) > 40 or (booking_reference and not re.fullmatch(r"[A-Z0-9-]+", booking_reference)):
            errors.append("Enter a valid booking reference.")
        if not 1 <= len(message) <= 4000:
            errors.append("Enter a message of up to 4,000 characters.")
        if errors:
            for error in errors:
                flash(error, "danger")
            return render_template("contact.html", inquiry_types=inquiry_types, values=values), 400
        record = ContactInquiry(
            full_name=full_name,
            email=email,
            inquiry_type=inquiry_type,
            booking_reference=booking_reference or None,
            message=message,
            status="New",
        )
        try:
            db.session.add(record)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            flash("We couldn't send your message right now. Please try again.", "danger")
            return render_template("contact.html", inquiry_types=inquiry_types, values=values), 503
        flash("Your message has been received. Thank you for contacting Infanta, I Hopping. Our team will review your inquiry.", "success")
        return redirect(url_for("main.contact"))
    return render_template("contact.html", inquiry_types=inquiry_types, values=values)


@main_bp.get("/safety")
def safety():
    return render_template("safety.html")

"""Customer dashboard and reservation history routes."""

from flask import Blueprint, redirect, render_template, url_for
from flask_login import current_user, login_required


customer_bp = Blueprint("customer", __name__, url_prefix="/customer")


@customer_bp.get("/dashboard")
@login_required
def dashboard():
    """Preserve the legacy URL while using My Bookings as the customer hub."""
    return redirect(url_for("customer.my_bookings"), code=302)


@customer_bp.get("/bookings")
@login_required
def my_bookings():
    bookings = Booking.query.filter_by(user_id=current_user.id).order_by(Booking.created_at.desc()).all()
    return render_template("customer/my_bookings.html", bookings=bookings)


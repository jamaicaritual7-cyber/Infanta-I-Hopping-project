"""Customer booking request routes."""

from datetime import datetime, timedelta, timezone
from uuid import uuid4

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from extensions import db
from forms.booking_forms import BookingForm
from models.booking import Booking
from models.boat import Boat
from models.destination import Destination
from services.destination_image_service import destination_image_catalog


booking_bp = Blueprint("booking", __name__, url_prefix="/booking")
PH_TIMEZONE = timezone(timedelta(hours=8), name="Asia/Manila")


@booking_bp.route("/book", methods=["GET", "POST"])
@login_required
def book_trip():
    form = BookingForm()
    destinations = Destination.query.filter_by(is_active=True).order_by(Destination.name).all()
    boats = Boat.query.filter_by(is_active=True, availability_status="available").order_by(Boat.name).all()
    form.destination_id.choices = [(item.id, item.name) for item in destinations]
    form.boat_id.choices = [(item.id, item.name) for item in boats]
    selected_destination_id = request.args.get("destination_id", type=int)
    selected_boat_id = request.args.get("boat_id", type=int)
    selected_destination = next((item for item in destinations if item.id == selected_destination_id), None)
    if request.method == "GET" and selected_destination is not None:
        form.destination_id.data = selected_destination.id
    if request.method == "GET" and selected_boat_id in {boat.id for boat in boats}:
        form.boat_id.data = selected_boat_id

    if form.validate_on_submit():
        boat = Boat.query.filter_by(
            id=form.boat_id.data,
            is_active=True,
            availability_status="available",
        ).first()
        destination = Destination.query.filter_by(id=form.destination_id.data, is_active=True).first()
        if boat is None:
            form.boat_id.errors.append("Please choose an available boat.")
        elif destination is None:
            form.destination_id.errors.append("Please choose an available destination.")
        elif form.passenger_count.data > boat.passenger_capacity:
            form.passenger_count.errors.append(
                f"Passenger count exceeds this boat's capacity of {boat.passenger_capacity}."
            )
        elif form.trip_date.data < datetime.now(PH_TIMEZONE).date():
            form.trip_date.errors.append("Please choose today or a future date.")
        else:
            conflicting_booking = Booking.query.filter(
                Booking.boat_id == boat.id,
                Booking.trip_date == form.trip_date.data,
                Booking.status.in_(("pending", "confirmed")),
            ).first()
            if conflicting_booking:
                form.trip_date.errors.append("This boat already has a booking for that date.")
                return render_template(
                    "customer/book_trip.html",
                    form=form,
                    destinations=destinations,
                    boats=boats,
                    selected_destination=selected_destination,
                )
            booking = Booking(
                booking_reference=f"BK-{uuid4().hex[:8].upper()}",
                user_id=current_user.id,
                boat_id=form.boat_id.data,
                destination_id=form.destination_id.data,
                trip_date=form.trip_date.data,
                passenger_count=form.passenger_count.data,
                special_request=form.special_request.data,
            )
            db.session.add(booking)
            db.session.commit()
            flash("Your booking request was submitted for operator review.", "success")
            return redirect(url_for("booking.booking_summary", booking_id=booking.id))

    return render_template(
        "customer/book_trip.html",
        form=form,
        destinations=destinations,
        boats=boats,
        selected_destination=selected_destination,
        destination_image=destination_image_catalog.get,
    )


@booking_bp.get("/<int:booking_id>/summary")
@login_required
def booking_summary(booking_id):
    booking = Booking.query.filter_by(id=booking_id, user_id=current_user.id).first_or_404()
    return render_template("customer/booking_summary.html", booking=booking)


@booking_bp.post("/<int:booking_id>/cancel")
@login_required
def cancel_booking(booking_id):
    booking = Booking.query.filter_by(id=booking_id, user_id=current_user.id).first_or_404()
    if booking.status != "pending":
        abort(400, description="Only pending booking requests can be cancelled.")

    booking.status = "cancelled"
    db.session.commit()
    flash(f"Booking {booking.booking_reference} was cancelled.", "success")
    return redirect(url_for("booking.booking_summary", booking_id=booking.id))


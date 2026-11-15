"""Protected administration routes for reservation monitoring."""

from functools import wraps

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError

from extensions import db
from forms.boat_forms import BoatForm
from forms.admin_forms import AdminProfileForm
from models.booking import Booking
from models.boat import Boat
from models.destination import Destination
from models.user import User
from models.contact_inquiry import ContactInquiry


admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def admin_required(view_function):
    """Allow only authenticated users whose role is administrator."""
    @wraps(view_function)
    @login_required
    def protected_view(*args, **kwargs):
        if current_user.role != "admin":
            abort(403)
        return view_function(*args, **kwargs)

    return protected_view


@admin_bp.get("/login")
def admin_login():
    """Provide a separate administrator entry point without duplicating auth."""
    return redirect(url_for("auth.login", portal="admin"))


@admin_bp.get("/dashboard")
@admin_required
def dashboard():
    bookings = Booking.query.order_by(Booking.created_at.desc()).limit(10).all()
    stats = {
        "total": Booking.query.count(),
        "pending": Booking.query.filter_by(status="pending").count(),
        "confirmed": Booking.query.filter_by(status="confirmed").count(),
        "cancelled": Booking.query.filter_by(status="cancelled").count(),
        "completed": Booking.query.filter_by(status="completed").count(),
    }
    return render_template("admin/dashboard.html", bookings=bookings, stats=stats)


@admin_bp.route("/profile", methods=["GET", "POST"])
@admin_required
def profile():
    form = AdminProfileForm(obj=current_user)
    if form.validate_on_submit():
        current_user.full_name = " ".join(form.full_name.data.split())
        current_user.contact_number = form.contact_number.data.strip()
        if form.password.data:
            current_user.set_password(form.password.data)
        db.session.commit()
        flash("Your administrator profile was updated.", "success")
        return redirect(url_for("admin.profile"))
    return render_template("admin/profile.html", form=form)


@admin_bp.get("/bookings")
@admin_required
def bookings():
    status = request.args.get("status", "").strip().lower()
    valid_statuses = {"pending", "confirmed", "completed", "cancelled"}
    if status and status not in valid_statuses:
        abort(400)

    query = Booking.query
    if status:
        query = query.filter_by(status=status)
    records = query.order_by(Booking.created_at.desc()).all()
    return render_template("admin/bookings.html", bookings=records, selected_status=status)


@admin_bp.get("/bookings/<int:booking_id>")
@admin_required
def booking_detail(booking_id):
    booking = db.get_or_404(Booking, booking_id)
    return render_template("admin/booking_detail.html", booking=booking)


@admin_bp.get("/boats")
@admin_required
def boats():
    records = Boat.query.order_by(Boat.name.asc()).all()
    return render_template("admin/boats.html", boats=records)


def _normalise_boat_name(value):
    return " ".join((value or "").split())


@admin_bp.route("/boats/new", methods=["GET", "POST"])
@admin_required
def create_boat():
    form = BoatForm()
    if form.validate_on_submit():
        name = _normalise_boat_name(form.name.data)
        duplicate = Boat.query.filter(func.lower(Boat.name) == name.lower()).first()
        if duplicate:
            form.name.errors.append("A boat with this name already exists.")
        else:
            boat = Boat(
                name=name,
                fuel_type=form.fuel_type.data.strip(),
                passenger_capacity=form.passenger_capacity.data,
                description=(form.description.data or "").strip() or None,
                photograph_path=(form.photograph_path.data or "").strip() or None,
                availability_status=form.availability_status.data,
                is_active=form.is_active.data,
            )
            try:
                db.session.add(boat)
                db.session.commit()
            except SQLAlchemyError:
                db.session.rollback()
                form.name.errors.append("The boat could not be saved. Please try again.")
            else:
                flash(f"Boat {boat.name} was created.", "success")
                return redirect(url_for("admin.boats"))
    return render_template("admin/boat_form.html", form=form, heading="Add boat")


@admin_bp.route("/boats/<int:boat_id>/edit", methods=["GET", "POST"])
@admin_required
def edit_boat(boat_id):
    boat = db.get_or_404(Boat, boat_id)
    form = BoatForm(obj=boat)
    if form.validate_on_submit():
        name = _normalise_boat_name(form.name.data)
        duplicate = Boat.query.filter(
            func.lower(Boat.name) == name.lower(),
            Boat.id != boat.id,
        ).first()
        if duplicate:
            form.name.errors.append("A boat with this name already exists.")
        else:
            boat.name = name
            boat.fuel_type = form.fuel_type.data.strip()
            boat.passenger_capacity = form.passenger_capacity.data
            boat.description = (form.description.data or "").strip() or None
            boat.photograph_path = (form.photograph_path.data or "").strip() or None
            boat.availability_status = form.availability_status.data
            boat.is_active = form.is_active.data
            try:
                db.session.commit()
            except SQLAlchemyError:
                db.session.rollback()
                form.name.errors.append("The boat could not be saved. Please try again.")
            else:
                flash(f"Boat {boat.name} was updated.", "success")
                return redirect(url_for("admin.boats"))
    return render_template("admin/boat_form.html", form=form, heading="Edit boat", boat=boat)


@admin_bp.post("/boats/<int:boat_id>/availability/<status>")
@admin_required
def update_boat_availability(boat_id, status):
    if status not in {"available", "unavailable", "maintenance"}:
        abort(400)
    boat = db.get_or_404(Boat, boat_id)
    boat.availability_status = status
    db.session.commit()
    flash(f"Boat {boat.name} is now {status}.", "success")
    return redirect(url_for("admin.boats"))


@admin_bp.post("/bookings/<int:booking_id>/status/<status>")
@admin_required
def update_booking_status(booking_id, status):
    if status not in {"confirmed", "cancelled", "pending", "completed"}:
        abort(400)

    # Lock the row where the database supports it, then enforce the workflow
    # on the server.  The status in the URL is never trusted by itself.
    booking = (
        Booking.query.filter_by(id=booking_id)
        .with_for_update()
        .first_or_404()
    )
    allowed_transitions = {
        "pending": {"confirmed", "cancelled"},
        "confirmed": {"completed", "cancelled"},
        "cancelled": set(),
        "completed": set(),
    }
    if status not in allowed_transitions.get(booking.status, set()):
        flash(
            f"A {booking.status} booking cannot be changed to {status}.",
            "warning",
        )
        return redirect(url_for("admin.booking_detail", booking_id=booking.id))

    if status == "confirmed":
        if not booking.boat.is_active or booking.boat.availability_status != "available":
            flash("This boat is not currently available for confirmation.", "warning")
            return redirect(url_for("admin.booking_detail", booking_id=booking.id))

        conflicting_booking = Booking.query.filter(
            Booking.id != booking.id,
            Booking.boat_id == booking.boat_id,
            Booking.trip_date == booking.trip_date,
            Booking.status.in_(("pending", "confirmed")),
        ).first()
        if conflicting_booking:
            flash(
                "This boat already has another reservation for that trip date.",
                "warning",
            )
            return redirect(url_for("admin.booking_detail", booking_id=booking.id))

    try:
        booking.status = status
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        flash("The booking update could not be saved. Please try again.", "danger")
        return redirect(url_for("admin.booking_detail", booking_id=booking.id))

    flash(f"Booking {booking.booking_reference} is now {status}.", "success")
    return redirect(url_for("admin.bookings"))


@admin_bp.get("/reports")
@admin_required
def reports():
    destination_counts = (
        Booking.query.join(Destination, Booking.destination_id == Destination.id)
        .with_entities(Destination.name, func.count(Booking.id).label("booking_count"))
        .group_by(Destination.id, Destination.name)
        .order_by(func.count(Booking.id).desc())
        .all()
    )
    return render_template("admin/reports.html", destination_counts=destination_counts)


@admin_bp.get("/customers")
@admin_required
def customers():
    records = User.query.filter_by(role="customer").order_by(User.created_at.desc()).all()
    return render_template("admin/customers.html", customers=records)




@admin_bp.get("/inquiries")
@admin_required
def inquiries():
    status = request.args.get("status", "").strip()
    if status and status not in {"New", "In Progress", "Resolved"}:
        abort(400)
    query = ContactInquiry.query
    if status:
        query = query.filter_by(status=status)
    records = query.order_by(ContactInquiry.created_at.desc()).all()
    return render_template("admin/inquiries.html", inquiries=records, selected_status=status)


@admin_bp.post("/inquiries/<int:inquiry_id>/status/<status>")
@admin_required
def update_inquiry_status(inquiry_id, status):
    if status not in {"New", "In Progress", "Resolved"}:
        abort(400)
    inquiry = db.get_or_404(ContactInquiry, inquiry_id)
    inquiry.status = status
    db.session.commit()
    flash(f"Inquiry status updated to {status}.", "success")
    return redirect(url_for("admin.inquiries"))

"""Reservation model for customer boat-rental requests."""

from extensions import db, utcnow


class Booking(db.Model):
    __tablename__ = "bookings"

    id = db.Column(db.Integer, primary_key=True)
    booking_reference = db.Column(db.String(30), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    boat_id = db.Column(db.Integer, db.ForeignKey("boats.id"), nullable=False)
    destination_id = db.Column(db.Integer, db.ForeignKey("destinations.id"), nullable=False)
    trip_date = db.Column(db.Date, nullable=False)
    passenger_count = db.Column(db.Integer, nullable=False)
    special_request = db.Column(db.Text)
    status = db.Column(db.String(30), nullable=False, default="pending")
    created_at = db.Column(db.DateTime, nullable=False, default=utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=utcnow, onupdate=utcnow)

    user = db.relationship("User", backref=db.backref("bookings", lazy=True))
    boat = db.relationship("Boat")
    destination = db.relationship("Destination")


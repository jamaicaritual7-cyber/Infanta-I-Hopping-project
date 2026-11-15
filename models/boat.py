"""Boat model for operator-managed vessels."""
from extensions import db, utcnow


class Boat(db.Model):
    __tablename__ = "boats"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    fuel_type = db.Column(db.String(50), nullable=False, default="Diesel")
    passenger_capacity = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text)
    photograph_path = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    availability_status = db.Column(db.String(30), nullable=False, default="available")
    created_at = db.Column(db.DateTime, nullable=False, default=utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=utcnow, onupdate=utcnow)


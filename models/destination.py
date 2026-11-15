"""Destination and geographic verification data."""
from extensions import db, utcnow


class Destination(db.Model):
    __tablename__ = "destinations"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    municipality = db.Column(db.String(100), nullable=False)
    province = db.Column(db.String(100), nullable=False, default="Quezon")
    latitude = db.Column(db.Numeric(10, 7))
    longitude = db.Column(db.Numeric(10, 7))
    google_maps_url = db.Column(db.String(500))
    straight_line_distance_km = db.Column(db.Numeric(8, 2))
    straight_line_distance_nm = db.Column(db.Numeric(8, 2))
    verified_sailing_distance_km = db.Column(db.Numeric(8, 2))
    estimated_travel_minutes = db.Column(db.Integer)
    coordinate_source = db.Column(db.String(255))
    verification_status = db.Column(db.String(30), nullable=False, default="unverified")
    verification_date = db.Column(db.Date)
    description = db.Column(db.Text)
    image_path = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=utcnow, onupdate=utcnow)


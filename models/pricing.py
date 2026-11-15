"""Database-managed provisional and confirmed package prices."""
from extensions import db, utcnow


class Pricing(db.Model):
    __tablename__ = "pricing"
    id = db.Column(db.Integer, primary_key=True)
    package_id = db.Column(db.Integer, db.ForeignKey("packages.id"), nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    currency = db.Column(db.String(3), nullable=False, default="PHP")
    price_type = db.Column(db.String(30), nullable=False, default="provisional")
    valid_from = db.Column(db.Date)
    valid_until = db.Column(db.Date)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=utcnow)
    package = db.relationship("Package", backref=db.backref("prices", lazy=True))


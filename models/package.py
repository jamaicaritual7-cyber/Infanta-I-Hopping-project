"""Trip packages and their ordered destination attractions."""
from extensions import db, utcnow

package_destinations = db.Table(
    "package_destinations",
    db.Column("package_id", db.Integer, db.ForeignKey("packages.id"), primary_key=True),
    db.Column("destination_id", db.Integer, db.ForeignKey("destinations.id"), primary_key=True),
    db.Column("stop_order", db.Integer, nullable=False, default=1),
)


class Package(db.Model):
    __tablename__ = "packages"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(180), nullable=False)
    municipality = db.Column(db.String(100), nullable=False)
    package_type = db.Column(db.String(30), nullable=False, default="nearby")
    description = db.Column(db.Text)
    route_status = db.Column(db.String(30), nullable=False, default="proposed")
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=utcnow, onupdate=utcnow)
    destinations = db.relationship("Destination", secondary=package_destinations, lazy="select")


"""Database models exported for application registration."""
from models.boat import Boat
from models.booking import Booking
from models.destination import Destination
from models.package import Package, package_destinations
from models.pricing import Pricing
from models.otp import OTPCode
from models.user import User

__all__ = ["Boat", "Booking", "Destination", "OTPCode", "Package", "Pricing", "User", "package_destinations"]


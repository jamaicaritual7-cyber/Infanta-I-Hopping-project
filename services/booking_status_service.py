"""Object-oriented booking status presentation rules."""

from abc import ABC, abstractmethod


class BookingStatus(ABC):
    """Abstract interface for a booking status presentation."""

    @property
    @abstractmethod
    def label(self):
        """Return the user-facing status label."""

    @property
    @abstractmethod
    def badge_class(self):
        """Return the Bootstrap badge class for the status."""


class PendingStatus(BookingStatus):
    @property
    def label(self):
        return "Pending"

    @property
    def badge_class(self):
        return "text-bg-warning"


class ConfirmedStatus(BookingStatus):
    @property
    def label(self):
        return "Confirmed"

    @property
    def badge_class(self):
        return "text-bg-success"


class CancelledStatus(BookingStatus):
    @property
    def label(self):
        return "Cancelled"

    @property
    def badge_class(self):
        return "text-bg-danger"


def get_booking_status(status):
    """Return the correct status object through polymorphic dispatch."""
    status_types = {
        "pending": PendingStatus,
        "confirmed": ConfirmedStatus,
        "cancelled": CancelledStatus,
    }
    return status_types.get(status, PendingStatus)()

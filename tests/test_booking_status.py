"""Tests for the booking-status polymorphism example."""

from services.booking_status_service import (
    CancelledStatus,
    ConfirmedStatus,
    PendingStatus,
    get_booking_status,
)


def test_status_factory_returns_different_polymorphic_objects():
    assert isinstance(get_booking_status("pending"), PendingStatus)
    assert isinstance(get_booking_status("confirmed"), ConfirmedStatus)
    assert isinstance(get_booking_status("cancelled"), CancelledStatus)


def test_status_objects_provide_the_same_interface_with_different_values():
    statuses = [
        get_booking_status("pending"),
        get_booking_status("confirmed"),
        get_booking_status("cancelled"),
    ]

    assert [status.label for status in statuses] == ["Pending", "Confirmed", "Cancelled"]
    assert [status.badge_class for status in statuses] == [
        "text-bg-warning",
        "text-bg-success",
        "text-bg-danger",
    ]

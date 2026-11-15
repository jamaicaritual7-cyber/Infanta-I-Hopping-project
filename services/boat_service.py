"""Business logic for displaying boats available for island-hopping trips.

The service keeps database queries out of route functions and provides a small
object-oriented seam that can be reused by customer and administrator pages.
"""

from models.boat import Boat


class BoatCatalog:
    """Encapsulates the rules used when customers browse active boats."""

    def __init__(self, boat_model=Boat):
        self._boat_model = boat_model

    def available_boats(self):
        """Return active boats in a stable display order."""
        return (
            self._boat_model.query.filter_by(is_active=True, availability_status="available")
            .order_by(self._boat_model.name.asc())
            .all()
        )

    def find_boat(self, boat_id):
        """Return one active boat or ``None`` when it is not available."""
        return self._boat_model.query.filter_by(
            id=boat_id,
            is_active=True,
            availability_status="available",
        ).first()

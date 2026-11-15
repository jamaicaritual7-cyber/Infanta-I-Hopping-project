"""Destination image catalog with explicit verification and licensing metadata."""

import json
from pathlib import Path


class DestinationImageCatalog:
    """Load destination image metadata without changing the database schema."""

    def __init__(self, manifest_path=None):
        self.manifest_path = manifest_path or (
            Path(__file__).resolve().parent.parent
            / "static/images/destinations/attribution.json"
        )
        self._records = None

    def _load(self):
        # Reload the small manifest so an approved photograph can be added
        # without a database migration or an application restart.
        with self.manifest_path.open("r", encoding="utf-8") as manifest:
            self._records = json.load(manifest)
        return self._records

    def get(self, destination_name):
        record = self._load().get(destination_name)
        if record is not None:
            return record
        return {
            "local_path": None,
            "status": "NO SUITABLE IMAGE FOUND",
            "source_url": None,
            "photographer": None,
            "license": "No reuse permission established",
            "verification_evidence": "No verified image record exists for this destination.",
            "date_checked": None,
        }


destination_image_catalog = DestinationImageCatalog()

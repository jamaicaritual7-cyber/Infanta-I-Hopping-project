import json
from pathlib import Path


class DestinationContentCatalog:
    """Presentation copy for destinations without requiring a database migration."""

    def __init__(self, content_path=None):
        self.content_path = Path(content_path or Path(__file__).with_name("destination_content.json"))
        self._records = None

    def _load(self):
        # Reload the small presentation catalog so content edits are reflected
        # without requiring a process restart during local development.
        with self.content_path.open("r", encoding="utf-8") as content_file:
            self._records = json.load(content_file)
        return self._records

    def get(self, destination_name):
        return self._load().get(destination_name, {})


destination_content_catalog = DestinationContentCatalog()

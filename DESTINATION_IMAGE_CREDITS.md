# Destination image verification record

The application reads `static/images/destinations/attribution.json` through `DestinationImageCatalog`. A destination is rendered with a local photograph only when its record has a `local_path`. Records without a local path intentionally render a neutral, status-labeled placeholder.

Baluti Island now uses the Wikimedia Commons photograph `baluti-island.jpg`, credited to Liamai168 under CC BY-SA 4.0. The source page identifies the view as overlooking Real Municipality and Baluti Cove.

As checked on 2026-11-15, the research found exact-location references for some destinations, but the available pages did not grant reuse permission. Those photographs were not copied. The manifest preserves the source URL, photographer/credit when available, the permission status, and the verification evidence.

To install a future approved photograph, place it under `static/images/destinations/`, confirm the exact destination and license, then set that record's `local_path` to the relative static path. No database migration is required.

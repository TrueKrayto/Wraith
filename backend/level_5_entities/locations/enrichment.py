from .location import Location
from .schemas import LocationEnrichmentData


def apply_location_enrichment(
    location: Location,
    enrichment: LocationEnrichmentData,
) -> Location:
    """
    Apply validated enrichment data to an existing Location.

    Enrichment must never change the location's identity or structure.
    """

    if enrichment.location_id != location.location_id:
        raise ValueError(
            "Enrichment target does not match Location."
        )

    location.description = enrichment.description
    location.enriched = True

    return location
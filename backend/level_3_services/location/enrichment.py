from backend.level_4_systems import (
    generate_location_enrichment,
    get_llm_client,
    get_llm_model,
    get_location_repository,
)

from backend.level_5_entities import (
    apply_location_enrichment,
)


def enrich_location(
    location_id: str,
):
    """
    Enrich one existing location and persist the result.

    Parent and known child locations are supplied as contextual anchors.
    """

    repository = get_location_repository()

    location = repository.get(
        location_id
    )

    if location is None:
        return None

    if location.enriched:
        return location

    # --------------------------------------------------------------
    # CONTEXT
    # --------------------------------------------------------------

    parent = None

    if location.parent_id is not None:
        parent = repository.get(
            location.parent_id
        )

    children = repository.get_children(
        location.location_id
    )

    # --------------------------------------------------------------
    # GENERATION
    # --------------------------------------------------------------

    client = get_llm_client()
    model = get_llm_model()

    enrichment = generate_location_enrichment(
        client=client,
        model=model,
        location=location,
        parent=parent,
        children=children,
    )

    # --------------------------------------------------------------
    # APPLY + SAVE
    # --------------------------------------------------------------

    apply_location_enrichment(
        location=location,
        enrichment=enrichment,
    )

    repository.save(
        location
    )

    return location
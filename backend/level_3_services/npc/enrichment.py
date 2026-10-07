from backend.level_4_systems import (
    generate_npc_enrichment,
    get_llm_client,
    get_llm_model,
    get_npc_repository,
)
from backend.level_5_entities import apply_npc_enrichment


def enrich_npc(
    npc_id: str,
):
    """
    Enrich one NPC's stable narrative identity.

    Loads the NPC, generates enrichment, applies it,
    persists the updated NPC, and returns it.
    """

    repository = get_npc_repository()

    npc = repository.get(npc_id)

    if npc is None:
        return None

    # Do not spend another LLM call on an NPC that has
    # already completed enrichment.
    if npc.enriched:
        return npc

    client = get_llm_client()
    model = get_llm_model()

    enrichment = generate_npc_enrichment(
        client=client,
        model=model,
        npc=npc,
    )

    apply_npc_enrichment(
        npc=npc,
        enrichment=enrichment,
    )

    repository.save(npc)

    return npc
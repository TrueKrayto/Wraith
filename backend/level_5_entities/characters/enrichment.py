from .npc import NPC
from .schemas import NPCEnrichmentData


def apply_npc_enrichment(
    npc: NPC,
    enrichment: NPCEnrichmentData,
) -> NPC:
    """
    Apply stable narrative enrichment to an NPC.

    This changes character identity data only.
    Persistence is handled elsewhere.
    """

    if enrichment.npc_id != npc.npc_id:
        raise ValueError(
            "Enrichment target does not match NPC."
        )

    npc.description = enrichment.description
    npc.personality = enrichment.personality
    npc.appearance = enrichment.appearance
    npc.mannerisms = enrichment.mannerisms
    npc.speech_style = enrichment.speech_style

    npc.enriched = True

    return npc
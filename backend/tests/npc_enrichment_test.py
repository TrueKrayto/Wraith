import json

from backend.entities.characters.temp_store import load_npcs
from backend.llm.client import (
    get_llm_client,
    get_llm_model,
)
from backend.llm.npc_enricher import generate_npc_enrichment


SCENE_PROMPT = """
You are narrating a short scene in a freeform fantasy RPG.

Use the supplied NPC data as the source of truth.

Describe the NPC briefly, then have them interact with a made-up
character named Rowan.

Rowan is a travelling stranger who approaches the NPC and says:

"Excuse me. I'm looking for somewhere safe to spend the night.
Do you know anywhere nearby?"

Write the NPC's response and immediate behaviour.

Keep the scene short:
- one brief descriptive paragraph
- a short interaction
- no more than roughly 150 words

Do not invent major history, relationships, quests, possessions,
or world lore.

Do not mention stats, levels, skills, or game mechanics directly.

The purpose of this test is to see how the supplied character
information affects portrayal, behaviour, and dialogue.
"""


def build_base_context(npc) -> dict:
    """
    Character context before enrichment.
    """

    return {
        "name": npc.name,
        "age": npc.age,
        "species": npc.species,
        "sex": npc.sex,

        "faction": npc.faction,
        "occupation": npc.occupation,
        "rank": npc.rank,
        "home": npc.home,

        "tier": npc.tier,
        "level": npc.level,

        "description": npc.description,
        "personality": npc.personality,

        "attributes": npc.attributes,
        "skills": npc.skills,
    }


def build_enriched_context(
    npc,
    enrichment,
) -> dict:
    """
    Same character context, but with the proposed enrichment included.
    """

    context = build_base_context(npc)

    context.update(
        {
            "description": enrichment.description,
            "personality": enrichment.personality,
            "appearance": enrichment.appearance,
            "mannerisms": enrichment.mannerisms,
            "speech_style": enrichment.speech_style,
        }
    )

    return context


def generate_scene(context: dict) -> str:
    """
    Generate one short comparison scene using supplied character data.
    """

    client = get_llm_client()
    model = get_llm_model()

    prompt = f"""
{SCENE_PROMPT}

NPC DATA:
{json.dumps(context, indent=2)}

Write the scene now.
"""

    response = client.responses.create(
        model=model,
        input=prompt,
    )

    return response.output_text.strip()


def print_enrichment(enrichment):
    print("\n--- GENERATED ENRICHMENT ---")
    print(f"Description:  {enrichment.description}")
    print(f"Personality:  {enrichment.personality}")
    print(f"Appearance:   {enrichment.appearance}")
    print(f"Mannerisms:   {enrichment.mannerisms}")
    print(f"Speech Style: {enrichment.speech_style}")


npcs = load_npcs()

print("\n=== NPC ENRICHMENT SCENE TEST ===")

for npc in npcs.values():

    print("\n")
    print("=" * 78)
    print(f"{npc.name} ({npc.npc_id})")
    print(f"Tier: {npc.tier}")
    print("=" * 78)

    # --------------------------------------------------------------
    # NON-ENRICHED SCENE
    # --------------------------------------------------------------

    base_context = build_base_context(npc)

    try:
        print("\n--- SCENE BEFORE ENRICHMENT ---\n")

        before_scene = generate_scene(
            base_context
        )

        print(before_scene)

        # ----------------------------------------------------------
        # GENERATE ENRICHMENT
        # ----------------------------------------------------------

        enrichment = generate_npc_enrichment(
            npc
        )

        print_enrichment(
            enrichment
        )

        # ----------------------------------------------------------
        # ENRICHED SCENE
        # ----------------------------------------------------------

        enriched_context = build_enriched_context(
            npc,
            enrichment,
        )

        print("\n--- SCENE AFTER ENRICHMENT ---\n")

        after_scene = generate_scene(
            enriched_context
        )

        print(after_scene)

    except Exception as error:
        print(
            f"\nERROR testing {npc.name}: {error}"
        )
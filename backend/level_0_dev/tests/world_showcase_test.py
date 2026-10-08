import time

from openai import RateLimitError

from backend.level_3_services.location import (
    create_location_from_prompt,
    enrich_location,
)
from backend.level_3_services.npc import (
    create_npc_from_prompt,
    enrich_npc,
)
from backend.level_4_systems import (
    get_llm_client,
    get_llm_model,
    get_location_repository,
)

from backend.level_0_dev.tests.characters.character_sheet_showcase import (
    print_character_sheet,
)


# ==================================================================
# RATE LIMIT HANDLING
# ==================================================================

RATE_LIMIT_WAIT_SECONDS = 5


def run_with_rate_limit_retry(
    operation,
    *args,
    **kwargs,
):
    """
    Run an operation and retry indefinitely if the LLM provider
    returns a rate-limit error.

    This behaviour is deliberately test-only.

    Any non-rate-limit exception is allowed to propagate normally.
    """

    while True:
        try:
            return operation(
                *args,
                **kwargs,
            )

        except RateLimitError:
            print(
                "\nRate limit reached."
                f" Waiting {RATE_LIMIT_WAIT_SECONDS} seconds..."
            )

            time.sleep(
                RATE_LIMIT_WAIT_SECONDS
            )

            print(
                "Retrying..."
            )


# ==================================================================
# HELPERS
# ==================================================================

def build_location_context(
    locations,
) -> str:
    """
    Build canonical location context for NPC creation.
    """

    by_id = {
        location.location_id: location
        for location in locations
    }

    lines = []

    for location in locations:
        parent = (
            by_id.get(location.parent_id)
            if location.parent_id
            else None
        )

        parent_name = (
            parent.name
            if parent is not None
            else "None"
        )

        lines.append(
            f"""
Location: {location.name}
Type: {location.location_type}
Parent: {parent_name}
Brief: {location.brief_description}
Description: {location.description}
""".strip()
        )

    return "\n\n".join(lines)


def build_npc_creation_prompt(
    *,
    stub,
    root,
    location_context: str,
) -> str:
    """
    Convert a location-generated NPC stub into an NPC creation request.

    This is intentionally test-only glue.

    It gives the existing NPC creator enough world context to ground
    the resulting NPC without changing the production pipeline yet.
    """

    return f"""
Create this canonical key NPC for the location {root.name}.

The NPC was established during location generation.

CANONICAL NPC STUB:

Name: {stub.name}
Occupation: {stub.occupation}
Rank: {stub.rank}
Brief description: {stub.brief_description}

CANONICAL LOCATION:

Name: {root.name}
Type: {root.location_type}
Brief description: {root.brief_description}

KNOWN LOCATION STRUCTURE:

{location_context}

Rules:

- Preserve the NPC's supplied name.
- Preserve the supplied occupation and rank where present.
- Preserve the supplied brief character concept.
- This NPC is an important figure in this location.
- Use medium or high tier where appropriate to their importance.
- Ground their identity in the supplied location.
- If their role clearly belongs to one of the known sublocations,
  current_location may use that exact existing location name.
- Otherwise current_location should be {root.name}.
- Do not invent additional named locations.
- Do not invent relationships with other NPCs.
"""


def build_showcase_prompt(
    *,
    root,
    locations,
    npcs,
) -> str:
    """
    Build the final presentation prompt from canonical generated data.
    """

    location_sections = []

    for location in locations:
        location_sections.append(
            f"""
NAME: {location.name}
TYPE: {location.location_type}
BRIEF: {location.brief_description}

FULL DESCRIPTION:
{location.description}
""".strip()
        )

    npc_sections = []

    for npc in npcs:
        npc_sections.append(
            f"""
NAME: {npc.name}
SPECIES: {npc.species}
AGE: {npc.age}
SEX: {npc.sex}
OCCUPATION: {npc.occupation}
RANK: {npc.rank}
CURRENT LOCATION: {npc.current_location}
TIER: {npc.tier}
LEVEL: {npc.level}

DESCRIPTION:
{npc.description}

PERSONALITY:
{npc.personality}

APPEARANCE:
{npc.appearance}

MANNERISMS:
{npc.mannerisms}

SPEECH STYLE:
{npc.speech_style}
""".strip()
        )

    locations_text = "\n\n".join(
        location_sections
    )

    npcs_text = "\n\n".join(
        npc_sections
    )

    return f"""
Using ONLY the canonical world information supplied below, write a short
setting overview suitable for presenting this generated Wraith location.

Write normal prose, not bullet points.

Use roughly 4-6 paragraphs.

Structure it approximately like this:

- Introduce {root.name} and establish what kind of place it is.
- Describe its important internal areas and how they fit together.
- Mention especially notable individual areas where useful.
- Finish with a section in prose about the famous or important people
  associated with the location.

Do not invent:

- new named characters
- new named locations
- new factions
- new history
- relationships
- quests
- current events
- possessions

You may connect and summarize established facts naturally.

Do not mention game mechanics, generation, schemas, prompts, levels,
tiers, IDs, or AI.

CANONICAL LOCATIONS:

{locations_text}


CANONICAL IMPORTANT PEOPLE:

{npcs_text}
"""


# ==================================================================
# TEST START
# ==================================================================

print()
print("=" * 78)
print("WRAITH WORLD SHOWCASE TEST")
print("=" * 78)

WORLD_PROMPT = input(
    "\nDescribe a location in a few words:\n> "
).strip()

if not WORLD_PROMPT:
    raise ValueError(
        "A location prompt is required."
    )


# ==================================================================
# 1. LOCATION CREATION
# ==================================================================

print()
print("=" * 78)
print("1. GENERATING LOCATION STRUCTURE")
print("=" * 78)

location_result = run_with_rate_limit_retry(
    create_location_from_prompt,
    location_prompt=WORLD_PROMPT,
)

root = location_result.locations[0]

print(
    f"\nCreated {root.name}"
    f" [{root.location_type}]"
)

print(
    f"Creation shape: "
    f"{location_result.creation_shape}"
)

print(
    f"Locations generated: "
    f"{len(location_result.locations)}"
)

print(
    f"Key NPC stubs: "
    f"{len(location_result.key_npcs)}"
)


# ==================================================================
# 2. ENRICH ALL GENERATED LOCATIONS
# ==================================================================

print()
print("=" * 78)
print("2. ENRICHING LOCATIONS")
print("=" * 78)

for index, location in enumerate(
    location_result.locations,
    start=1,
):
    print(
        f"\n[{index}/{len(location_result.locations)}] "
        f"Enriching {location.name}..."
    )

    enriched = run_with_rate_limit_retry(
        enrich_location,
        location.location_id,
    )

    if enriched is None:
        raise RuntimeError(
            f"Location disappeared during enrichment: "
            f"{location.location_id}"
        )

    print(
        f"Finished: {enriched.name}"
    )


# ==================================================================
# 3. RELOAD ENRICHED LOCATION DATA
# ==================================================================

location_repository = get_location_repository()

enriched_locations = []

for original in location_result.locations:
    persisted = location_repository.get(
        original.location_id
    )

    if persisted is None:
        raise RuntimeError(
            f"Persisted location missing: "
            f"{original.location_id}"
        )

    enriched_locations.append(
        persisted
    )


root = enriched_locations[0]

location_context = build_location_context(
    enriched_locations
)


# ==================================================================
# 4. CREATE NPC ENTITIES FROM LOCATION STUBS
# ==================================================================

print()
print("=" * 78)
print("3. CREATING KEY NPCS")
print("=" * 78)

created_npcs = []

for index, stub in enumerate(
    location_result.key_npcs,
    start=1,
):
    print(
        f"\n[{index}/{len(location_result.key_npcs)}] "
        f"Creating {stub.name}..."
    )

    npc_prompt = build_npc_creation_prompt(
        stub=stub,
        root=root,
        location_context=location_context,
    )

    npc = run_with_rate_limit_retry(
        create_npc_from_prompt,
        npc_prompt,
    )

    created_npcs.append(
        npc
    )

    print(
        f"Created: {npc.name}"
        f" | {npc.occupation}"
        f" | location={npc.current_location}"
    )


# ==================================================================
# 5. ENRICH NPCS
# ==================================================================

print()
print("=" * 78)
print("4. ENRICHING KEY NPCS")
print("=" * 78)

enriched_npcs = []

for index, npc in enumerate(
    created_npcs,
    start=1,
):
    print(
        f"\n[{index}/{len(created_npcs)}] "
        f"Enriching {npc.name}..."
    )

    enriched = run_with_rate_limit_retry(
        enrich_npc,
        npc.npc_id,
    )

    if enriched is None:
        raise RuntimeError(
            f"NPC disappeared during enrichment: "
            f"{npc.npc_id}"
        )

    enriched_npcs.append(
        enriched
    )

    print(
        f"Finished: {enriched.name}"
    )


# ==================================================================
# 6. FINAL SYNTHESIS
#
# Deliberately one final LLM call purely for this showcase.
# It does not persist or modify world state.
# ==================================================================

print()
print("=" * 78)
print("5. BUILDING FINAL WORLD DESCRIPTION")
print("=" * 78)

client = get_llm_client()
model = get_llm_model()

showcase_prompt = build_showcase_prompt(
    root=root,
    locations=enriched_locations,
    npcs=enriched_npcs,
)

response = run_with_rate_limit_retry(
    client.responses.create,
    model=model,
    input=showcase_prompt,
)

showcase_text = (
    response.output_text
    .strip()
)


# ==================================================================
# FINAL OUTPUT
# ==================================================================

print()
print()
print("=" * 78)
print(
    root.name.upper()
)
print("=" * 78)
print()
print(
    showcase_text
)


# ==================================================================
# CHARACTER SHEETS
# ==================================================================

print()
print()
print("=" * 78)
print("GENERATED CHARACTER SHEETS")
print("=" * 78)

for npc in enriched_npcs:

    print()

    print_character_sheet(
        npc.npc_id
    )

    print()


# ==================================================================
# GENERATION SUMMARY
# ==================================================================

print()
print()
print("=" * 78)
print("GENERATION SUMMARY")
print("=" * 78)

print(
    f"Root location: "
    f"{root.name}"
)

print(
    f"Creation shape: "
    f"{location_result.creation_shape}"
)

print(
    f"Locations created/enriched: "
    f"{len(enriched_locations)}"
)

print(
    f"Key NPCs created/enriched: "
    f"{len(enriched_npcs)}"
)
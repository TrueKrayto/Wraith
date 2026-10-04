from backend.level_4_systems.data import get_npc_repository
from backend.level_4_systems.llm.clients import (
    get_llm_client,
    get_llm_model,
)
from backend.level_4_systems.llm.npc import generate_npc_enrichment


client = get_llm_client()
model = get_llm_model()

repository = get_npc_repository()

npc_ids = repository.get_unenriched_ids()


print("\n=== NPC ENRICHMENT TEST ===")


if not npc_ids:
    print("\nNo unenriched NPCs found.")


for npc_id in npc_ids:

    npc = repository.get(npc_id)

    if npc is None:
        continue

    print("\n")
    print("=" * 78)
    print(f"{npc.name} ({npc.npc_id})")
    print("=" * 78)

    try:
        enrichment = generate_npc_enrichment(
            client=client,
            model=model,
            npc=npc,
        )

        print(f"Name:         {npc.name}")
        print(f"Age:          {npc.age}")
        print(f"Species:      {npc.species}")
        print(f"Sex:          {npc.sex}")
        print(f"Faction:      {npc.faction}")
        print(f"Occupation:   {npc.occupation}")
        print(f"Rank:         {npc.rank}")
        print(f"Home:         {npc.home}")
        print(f"Location:     {npc.current_location}")
        print(f"Tier:         {npc.tier}")
        print(f"Level:        {npc.level}")

        print("\n--- ENRICHMENT ---")

        print(f"Description:  {enrichment.description}")
        print(f"Personality:  {enrichment.personality}")
        print(f"Appearance:   {enrichment.appearance}")
        print(f"Mannerisms:   {enrichment.mannerisms}")
        print(f"Speech Style: {enrichment.speech_style}")

    except Exception as error:
        print(
            f"\nERROR enriching {npc.name}: {error}"
        )
from dataclasses import asdict
from pprint import pprint

from backend.entities.characters import apply_npc_mutation
from backend.entities.characters.temp_store import (
    load_npcs,
    save_npcs,
)
from backend.llm.temp_npc_mutator import generate_npc_mutation


print("\n--- NPC MUTATION TEST ---")
print("Type a natural-language mutation.")
print("Type 'list' to show NPCs.")
print("Type 'quit' to exit.")


while True:
    instruction = input("\nMutation: ").strip()

    if not instruction:
        continue

    if instruction.lower() == "quit":
        break

    if instruction.lower() == "list":
        npcs = load_npcs()

        print("\n--- STORED NPCS ---")

        for npc_id, npc in npcs.items():
            print(f"{npc.name} - {npc_id}")

        continue

    try:
        # LLM converts natural language into a structured mutation.
        mutation = generate_npc_mutation(
            instruction
        )

        print("\n--- MODEL MUTATION ---")
        pprint(
            mutation.model_dump(),
            sort_dicts=False,
        )

        # Reload the latest persistent state.
        npcs = load_npcs()

        npc = npcs.get(
            mutation.npc_id
        )

        if npc is None:
            print("\nNPC not found.")
            continue

        # Apply the mutation through the character engine.
        apply_npc_mutation(
            npc=npc,
            mutation=mutation,
        )

        # Persist the changed NPC.
        save_npcs(npcs)

        print("\n--- UPDATED NPC ---")
        pprint(
            asdict(npc),
            sort_dicts=False,
        )

    except Exception as error:
        print(f"\nERROR: {error}")
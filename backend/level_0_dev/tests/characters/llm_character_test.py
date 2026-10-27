from backend.level_3_services import (
    create_npc_from_prompt,
)

from backend.level_0_dev.tests.characters.character_sheet_showcase import (
    print_character_sheet,
)


print()
print("=" * 78)
print("WRAITH NPC CREATION TEST")
print("=" * 78)

prompt = input(
    "\nDescribe your character:\n> "
).strip()

if not prompt:
    raise ValueError(
        "Character prompt is required."
    )


# ==================================================================
# NPC CREATION PIPELINE
# ==================================================================

npc = create_npc_from_prompt(
    prompt
)


# ==================================================================
# CHARACTER SHEET
# ==================================================================

print()
print_character_sheet(
    npc.npc_id
)


# ==================================================================
# SUMMARY
# ==================================================================

print()
print("=" * 78)
print("NPC CREATION COMPLETE")
print("=" * 78)

print(f"NPC: {npc.name}")
print(f"NPC ID: {npc.npc_id}")
print("Persisted: Yes")
print(f"Enriched: {npc.enriched}")
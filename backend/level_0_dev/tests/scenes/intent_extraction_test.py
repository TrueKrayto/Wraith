from backend.level_4_systems import (
    LLMRole,
    extract_player_intent,
    get_llm_client_manager,
    get_location_repository,
    get_npc_repository,
)

from backend.level_5_entities import (
    IntentResult,
)


# ==================================================================
# SETUP
# ==================================================================

print()
print("=" * 78)
print("WRAITH INTENT EXTRACTION TEST")
print("=" * 78)

location_repository = get_location_repository()
npc_repository = get_npc_repository()

llm_manager = get_llm_client_manager()

llm = llm_manager.get(
    LLMRole.INTENT_EXTRACTION
)

print()
print(f"Model: {llm.model}")


# ==================================================================
# 1. SELECT LOCATION
# ==================================================================

print()
print("=" * 78)
print("1. SELECT LOCATION")
print("=" * 78)

location_id = input(
    "\nEnter location UID:\n> "
).strip()

location = location_repository.get(
    location_id
)

if location is None:
    raise ValueError(
        f"Location not found: {location_id}"
    )

print()
print(f"Location: {location.name}")
print(f"Type: {location.location_type}")


# ==================================================================
# 2. SELECT NPCS
# ==================================================================

print()
print("=" * 78)
print("2. SELECT NPCS")
print("=" * 78)

raw_ids = input(
    "\nEnter NPC UIDs (comma separated, blank for none):\n> "
).strip()

npc_ids = [
    npc_id.strip()
    for npc_id in raw_ids.split(",")
    if npc_id.strip()
]

npcs = []

for npc_id in npc_ids:

    npc = npc_repository.get(
        npc_id
    )

    if npc is None:
        raise ValueError(
            f"NPC not found: {npc_id}"
        )

    npcs.append(npc)

print()
print("--- AVAILABLE NPCS ---")

if not npcs:
    print("None")

for npc in npcs:
    print(
        f"- {npc.name} "
        f"({npc.npc_id})"
    )


# ==================================================================
# 3. INTERACTIVE EXTRACTION TEST
# ==================================================================

print()
print("=" * 78)
print("3. INTENT EXTRACTION")
print("=" * 78)

print()
print("Enter player actions to extract their intentions.")
print("Type 'quit' or 'exit' to finish.")

tests_completed = 0

while True:

    player_input = input(
        "\nWhat do you do?\n> "
    ).strip()

    if player_input.lower() in {
        "quit",
        "exit",
    }:
        break

    if not player_input:
        print("Player input cannot be empty.")
        continue

    # --------------------------------------------------------------
    # EXTRACT
    # --------------------------------------------------------------

    print()
    print("Extracting intentions...")

    result = extract_player_intent(
        client=llm.client,
        model=llm.model,
        player_input=player_input,
        location=location,
        npcs=tuple(npcs),
    )

    # --------------------------------------------------------------
    # VALIDATE
    # --------------------------------------------------------------

    assert isinstance(
        result,
        IntentResult,
    ), "Extractor did not return IntentResult."

    assert isinstance(
        result.actions,
        list,
    ), "Actions must be a list."

    # --------------------------------------------------------------
    # PRINT STRUCTURED OUTPUT
    # --------------------------------------------------------------

    print()
    print("=" * 78)
    print("EXTRACTED INTENT JSON")
    print("=" * 78)

    print()
    print(
        result.model_dump_json(
            indent=2
        )
    )

    # --------------------------------------------------------------
    # HUMAN READABLE SUMMARY
    # --------------------------------------------------------------

    print()
    print("=" * 78)
    print("ACTION SUMMARY")
    print("=" * 78)

    if not result.actions:
        print("\nNo actionable intentions identified.")

    for index, action in enumerate(
        result.actions,
        start=1,
    ):

        print()
        print(f"Action {index}")
        print(f"  Type: {action.action_type}")
        print(f"  Intent: {action.intent}")
        print(f"  Target: {action.target_reference}")
        print(f"  Destination: {action.destination_reference}")
        print(f"  Dialogue: {action.dialogue}")
        print(f"  Original: {action.original_text}")

    print()
    print("--- UNRESOLVED REFERENCES ---")

    if result.unresolved_references:

        for reference in result.unresolved_references:
            print(f"- {reference}")

    else:
        print("None")

    tests_completed += 1

    print()
    print("PASS: Valid IntentResult returned.")
    print("NOTE: Semantic accuracy requires inspection.")


# ==================================================================
# SUMMARY
# ==================================================================

print()
print("=" * 78)
print("INTENT EXTRACTION TEST SUMMARY")
print("=" * 78)

print()
print(f"Model: {llm.model}")
print(f"Location: {location.name}")
print(f"NPCs supplied: {len(npcs)}")
print(f"Tests completed: {tests_completed}")

print()
print("No game mechanics executed.")
print("No world-state mutations requested.")

print()
print("=" * 78)
print("INTENT EXTRACTION TEST COMPLETE")
print("=" * 78)
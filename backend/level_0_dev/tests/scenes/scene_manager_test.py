
from backend.level_3_services import create_scene_manager

from backend.level_4_systems import (
    get_location_repository,
    get_npc_repository,
)

from backend.level_5_entities import ActionProposal


# ==============================================================
# SETUP
# ==============================================================

print()
print("=" * 78)
print("WRAITH SCENE MANAGER INTEGRATION TEST")
print("=" * 78)

manager = create_scene_manager()

location_repository = get_location_repository()
npc_repository = get_npc_repository()


# ==============================================================
# 1. SELECT LOCATION
# ==============================================================

location_id = input(
    "\nEnter location UID:\n> "
).strip()

location = location_repository.get(location_id)

if location is None:
    raise ValueError(
        f"Location not found: {location_id}"
    )

print(f"\nLocation: {location.name}")


# ==============================================================
# 2. SELECT PLAYER AND NPCS
# ==============================================================

player_character_id = input(
    "\nEnter player ID (blank for test-player):\n> "
).strip() or "test-player"

raw_npc_ids = input(
    "\nEnter NPC UIDs (comma separated, blank for none):\n> "
).strip()

npc_ids = [
    value.strip()
    for value in raw_npc_ids.split(",")
    if value.strip()
]


# ==============================================================
# 3. CREATE SCENE
# ==============================================================

scene = manager.start_scene(
    location_id=location_id,
    player_character_id=player_character_id,
    npc_ids=npc_ids,
)

assert scene.phase == "ready"
assert scene.turn_number == 0
assert scene.pending_turn_id is None

print()
print("=" * 78)
print("SCENE CREATED")
print("=" * 78)

print(f"Scene ID: {scene.scene_id}")
print(f"Location ID: {scene.location_id}")
print(f"Player ID: {scene.player_character_id}")
print(f"NPC count: {len(scene.npc_ids)}")

for npc_id in scene.npc_ids:
    npc = npc_repository.get(npc_id)
    print(f"- {npc.name} ({npc.npc_id})")


# ==============================================================
# 4. INTERACTIVE TURN TEST
# ==============================================================

tests_completed = 0

while True:

    player_input = input(
        "\nWhat do you do? (quit to exit)\n> "
    ).strip()

    if player_input.lower() in {"quit", "exit"}:
        break

    if not player_input:
        continue

    # ----------------------------------------------------------
    # PREPARE TURN
    # ----------------------------------------------------------

    prepared = manager.prepare_turn(
        scene_id=scene.scene_id,
        player_input=player_input,
    )

    # ----------------------------------------------------------
    # VALIDATE PREPARED TURN
    # ----------------------------------------------------------

    assert isinstance(
        prepared.proposal,
        ActionProposal,
    )

    assert prepared.scene_id == scene.scene_id
    assert prepared.location_id == scene.location_id
    assert prepared.player_character_id == scene.player_character_id
    assert prepared.npc_ids == tuple(scene.npc_ids)
    assert prepared.player_input == player_input
    assert prepared.turn_number == scene.turn_number + 1

    current_scene = manager.get_scene(scene.scene_id)

    assert current_scene.phase == "awaiting_resolution"
    assert current_scene.pending_turn_id == prepared.turn_id

    print()
    print("=" * 78)
    print("PREPARED TURN")
    print("=" * 78)

    print(f"Turn ID: {prepared.turn_id}")
    print(f"Turn number: {prepared.turn_number}")
    print(f"Scene phase: {current_scene.phase}")

    print()
    print("--- ACTION PROPOSAL ---")

    print(
        prepared.proposal.model_dump_json(
            indent=2
        )
    )

    # ----------------------------------------------------------
    # PENDING TURN PROTECTION
    # ----------------------------------------------------------

    try:
        manager.prepare_turn(
            scene_id=scene.scene_id,
            player_input="Attempt duplicate turn",
        )

    except RuntimeError:
        print("\nPASS: Duplicate pending turn rejected.")

    else:
        raise AssertionError(
            "SceneManager allowed a second pending turn."
        )

    # ----------------------------------------------------------
    # COMPLETE TURN
    # ----------------------------------------------------------

    completed = manager.complete_turn(
        scene_id=scene.scene_id,
        turn_id=prepared.turn_id,
    )

    assert completed.phase == "ready"
    assert completed.pending_turn_id is None
    assert completed.turn_number == prepared.turn_number

    tests_completed += 1

    print()
    print("PASS: ActionProposal returned.")
    print("PASS: Turn lifecycle completed.")
    print("NOTE: No mechanical resolution performed.")


# ==============================================================
# SUMMARY
# ==============================================================

print()
print("=" * 78)
print("SCENE MANAGER TEST SUMMARY")
print("=" * 78)

print(f"Scene ID: {scene.scene_id}")
print(f"Turns completed: {tests_completed}")
print(f"Final phase: {scene.phase}")

assert scene.phase == "ready"
assert scene.pending_turn_id is None

print()
print("SCENE MANAGER INTEGRATION TEST PASSED")

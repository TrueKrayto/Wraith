from backend.level_4_systems import (
    SceneManager,
    get_location_repository,
    get_npc_repository,
)


# ==================================================================
# SETUP
# ==================================================================

print()
print("=" * 78)
print("WRAITH SCENE MANAGER TEST")
print("=" * 78)

manager = SceneManager()

location_repository = get_location_repository()
npc_repository = get_npc_repository()


# ==================================================================
# 1. SELECT LOCATION
# ==================================================================

print()
print("1. SELECT LOCATION")
print("-" * 78)

location_id = input(
    "\nEnter location UID:\n> "
).strip()

if not location_id:
    raise ValueError(
        "Location UID is required."
    )

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
print(f"Enriched: {location.enriched}")


# ==================================================================
# 2. PLAYER CHARACTER
# ==================================================================

print()
print("2. PLAYER CHARACTER")
print("-" * 78)

# Player character persistence has not been implemented yet.
# For this test, we use a placeholder player ID.

player_character_id = input(
    "\nEnter player character ID (blank for test-player):\n> "
).strip()

if not player_character_id:
    player_character_id = "test-player"


# ==================================================================
# 3. NPC SELECTION
# ==================================================================

print()
print("3. NPC SELECTION")
print("-" * 78)

raw_npc_ids = input(
    "\nEnter NPC UIDs (comma separated, blank for none):\n> "
).strip()

npc_ids = []

if raw_npc_ids:
    npc_ids = [
        npc_id.strip()
        for npc_id in raw_npc_ids.split(",")
        if npc_id.strip()
    ]

print()
print(f"NPCs requested: {len(npc_ids)}")


# ==================================================================
# 4. START SCENE
# ==================================================================

print()
print("=" * 78)
print("4. STARTING SCENE")
print("=" * 78)

scene = manager.start_scene(
    location_id=location_id,
    player_character_id=player_character_id,
    npc_ids=npc_ids,
)

assert scene.phase == "ready"
assert scene.turn_number == 0
assert scene.pending_turn_id is None

print()
print(f"Scene ID: {scene.scene_id}")
print(f"Location: {location.name}")
print(f"Player ID: {scene.player_character_id}")
print(f"NPCs present: {len(scene.npc_ids)}")
print(f"Turn number: {scene.turn_number}")
print(f"Phase: {scene.phase}")

print()
print("--- PRESENT NPCS ---")

if not scene.npc_ids:
    print("None")

for npc_id in scene.npc_ids:

    npc = npc_repository.get(npc_id)

    if npc is None:
        raise RuntimeError(
            f"NPC disappeared: {npc_id}"
        )

    print(
        f"- {npc.name} | "
        f"{npc.occupation or 'Unknown occupation'} | "
        f"Level {npc.level}"
    )


# ==================================================================
# 5. INTERACTIVE TURN LOOP
# ==================================================================

print()
print("=" * 78)
print("5. INTERACTIVE SCENE TEST")
print("=" * 78)

print()
print("Enter player actions to test scene preparation.")
print("Type 'quit' or 'exit' to finish.")

while True:

    print()
    print("-" * 78)

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
    # PREPARE TURN
    # --------------------------------------------------------------

    prepared = manager.prepare_turn(
        scene_id=scene.scene_id,
        player_input=player_input,
    )

    # --------------------------------------------------------------
    # VALIDATE PREPARED STATE
    # --------------------------------------------------------------

    current_scene = manager.get_scene(
        scene.scene_id
    )

    assert current_scene is not None
    assert current_scene.phase == "awaiting_resolution"
    assert current_scene.pending_turn_id == prepared.turn_id

    assert prepared.scene_id == scene.scene_id
    assert prepared.turn_number == scene.turn_number + 1
    assert prepared.player_input == player_input
    assert prepared.location.location_id == scene.location_id

    assert [
        npc.npc_id
        for npc in prepared.npcs
    ] == scene.npc_ids

    # --------------------------------------------------------------
    # PRINT PREPARED TURN
    # --------------------------------------------------------------

    print()
    print("=" * 78)
    print("PREPARED TURN")
    print("=" * 78)

    print()
    print(f"Turn ID: {prepared.turn_id}")
    print(f"Scene ID: {prepared.scene_id}")
    print(f"Turn number: {prepared.turn_number}")
    print(f"Player ID: {prepared.player_character_id}")

    print()
    print("--- PLAYER INPUT ---")
    print(prepared.player_input)

    print()
    print("--- CANONICAL LOCATION ---")

    print(f"Name: {prepared.location.name}")
    print(f"Type: {prepared.location.location_type}")
    print(f"ID: {prepared.location.location_id}")

    print()
    print("Brief description:")
    print(
        prepared.location.brief_description
        or "None"
    )

    print()
    print("Full description:")
    print(
        prepared.location.description
        or "Not enriched"
    )

    print()
    print("--- PRESENT NPCS ---")

    if not prepared.npcs:
        print("None")

    for npc in prepared.npcs:

        print()
        print(f"Name: {npc.name}")
        print(f"ID: {npc.npc_id}")
        print(f"Occupation: {npc.occupation}")
        print(f"Tier: {npc.tier}")
        print(f"Level: {npc.level}")
        print(f"Enriched: {npc.enriched}")

        print(
            f"Description: "
            f"{npc.description or 'None'}"
        )

        print(
            f"Personality: "
            f"{npc.personality or 'None'}"
        )

    print()
    print("--- TURN STATE ---")

    print(f"Phase: {current_scene.phase}")
    print(f"Pending turn: {current_scene.pending_turn_id}")

    # --------------------------------------------------------------
    # VALIDATE PENDING-TURN PROTECTION
    # --------------------------------------------------------------

    try:

        manager.prepare_turn(
            scene_id=scene.scene_id,
            player_input="Attempt duplicate turn",
        )

    except RuntimeError:

        print()
        print("PASS: Duplicate pending turn rejected.")

    else:

        raise AssertionError(
            "SceneManager allowed a second pending turn."
        )

    # --------------------------------------------------------------
    # COMPLETE TURN
    #
    # Temporary lifecycle completion only.
    # No mechanical resolution or world mutation occurs.
    # --------------------------------------------------------------

    completed_scene = manager.complete_turn(
        scene_id=scene.scene_id,
        turn_id=prepared.turn_id,
    )

    assert completed_scene.phase == "ready"
    assert completed_scene.pending_turn_id is None
    assert completed_scene.turn_number == prepared.turn_number

    print()
    print("--- TURN COMPLETED ---")

    print(f"Turn number: {completed_scene.turn_number}")
    print(f"Phase: {completed_scene.phase}")
    print(f"Pending turn: {completed_scene.pending_turn_id}")

    print()
    print("PASS: Turn lifecycle completed successfully.")


# ==================================================================
# FINAL SUMMARY
# ==================================================================

final_scene = manager.get_scene(
    scene.scene_id
)

assert final_scene is not None

print()
print()
print("=" * 78)
print("SCENE MANAGER TEST SUMMARY")
print("=" * 78)

print()
print(f"Scene ID: {final_scene.scene_id}")
print(f"Location: {location.name}")
print(f"Player ID: {final_scene.player_character_id}")
print(f"NPCs present: {len(final_scene.npc_ids)}")
print(f"Turns completed: {final_scene.turn_number}")
print(f"Final phase: {final_scene.phase}")

assert final_scene.phase == "ready"
assert final_scene.pending_turn_id is None

print()
print("=" * 78)
print("SCENE MANAGER TEST PASSED")
print("=" * 78)
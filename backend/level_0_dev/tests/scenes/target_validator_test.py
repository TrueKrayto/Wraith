
from types import SimpleNamespace

from backend.level_4_systems import SceneManager

from backend.level_5_entities import (
    ActionProposal,
    ProposedAction,
)


# ==============================================================
# MANUALLY DEFINED SCENE
# ==============================================================

LOCATION_ID = "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"

MARCUS_1 = "11111111-1111-4111-8111-111111111111"
MARCUS_2 = "22222222-2222-4222-8222-222222222222"
BILL = "33333333-3333-4333-8333-333333333333"
SILVERSONG = "44444444-4444-4444-8444-444444444444"
MARK = "55555555-5555-4555-8555-555555555555"

INVALID_ID = "99999999-9999-4999-8999-999999999999"


# Lightweight test objects.
# No NPC creation, database or LLM calls.

location = SimpleNamespace(
    location_id=LOCATION_ID,
    name="Castle Great Hall",
    location_type="hall",
)

npcs = [
    SimpleNamespace(
        npc_id=MARCUS_1,
        name="Marcus",
        occupation="Guard",
        rank="Soldier",
    ),
    SimpleNamespace(
        npc_id=MARCUS_2,
        name="Marcus",
        occupation="Guard",
        rank="Captain",
    ),
    SimpleNamespace(
        npc_id=BILL,
        name="Bill",
        occupation="Guard",
        rank="Soldier",
    ),
    SimpleNamespace(
        npc_id=SILVERSONG,
        name="Silversong",
        occupation="Spirit",
        rank=None,
    ),
    SimpleNamespace(
        npc_id=MARK,
        name="Mark",
        occupation="Guard",
        rank="Soldier",
    ),
]


# ==============================================================
# FAKE REPOSITORY
# ==============================================================

class FakeRepository:

    def __init__(self, objects, id_field):
        self._objects = {
            str(getattr(obj, id_field)): obj
            for obj in objects
        }

    def get(self, entity_id):
        return self._objects.get(str(entity_id))


location_repository = FakeRepository(
    [location],
    "location_id",
)

npc_repository = FakeRepository(
    npcs,
    "npc_id",
)


# ==============================================================
# MANUAL TEST CASES
# ==============================================================

TEST_CASES = [
    {
        "name": "Correct explicit NPC",
        "input": "I attack Bill.",
        "reference": "Bill",
        "given_id": BILL,
        "given_status": "explicit",
        "type": "npc",
        "expected_id": BILL,
        "expected_status": "explicit",
    },
    {
        "name": "Wrong but valid NPC ID",
        "input": "I attack Bill.",
        "reference": "Bill",
        "given_id": SILVERSONG,
        "given_status": "explicit",
        "type": "npc",
        "expected_id": BILL,
        "expected_status": "explicit",
    },
    {
        "name": "Invented UUID, valid name",
        "input": "I attack Bill.",
        "reference": "Bill",
        "given_id": INVALID_ID,
        "given_status": "explicit",
        "type": "npc",
        "expected_id": BILL,
        "expected_status": "explicit",
    },
    {
        "name": "Two guards, no selected ID",
        "input": "I attack the guard.",
        "reference": "guard",
        "given_id": None,
        "given_status": "unresolved",
        "type": "npc",
        "expected_id": MARCUS_1,
        "expected_status": "default",
    },
    {
        "name": "Duplicate names, second Marcus",
        "input": "I attack Marcus.",
        "reference": "Marcus",
        "given_id": MARCUS_2,
        "given_status": "explicit",
        "type": "npc",
        "expected_id": MARCUS_2,
        "expected_status": "explicit",
    },
    {
        "name": "Unknown name with WRONG valid ID",
        "input": "I attack Rowan.",
        "reference": "Rowan",
        "given_id": SILVERSONG,
        "given_status": "explicit",
        "type": "npc",
        "expected_id": None,
        "expected_status": "unresolved",
    },
    {
        "name": "Unknown name with no ID",
        "input": "I attack Rowan.",
        "reference": "Rowan",
        "given_id": None,
        "given_status": "unresolved",
        "type": "npc",
        "expected_id": None,
        "expected_status": "unresolved",
    },
    {
        "name": "Descriptive fork",
        "input": "I pick up a fork.",
        "reference": "fork",
        "given_id": None,
        "given_status": "descriptive",
        "type": "object",
        "expected_id": None,
        "expected_status": "descriptive",
    },
    {
        "name": "Object with invented UUID",
        "input": "I pick up a fork.",
        "reference": "fork",
        "given_id": INVALID_ID,
        "given_status": "explicit",
        "type": "object",
        "expected_id": None,
        "expected_status": "descriptive",
    },
    {
        "name": "Impossible descriptive action",
        "input": "I lift the castle.",
        "reference": "castle",
        "given_id": None,
        "given_status": "descriptive",
        "type": "object",
        "expected_id": None,
        "expected_status": "descriptive",
    },
    {
        "name": "Action without a target",
        "input": "I laugh.",
        "reference": None,
        "given_id": None,
        "given_status": None,
        "type": None,
        "expected_id": None,
        "expected_status": None,
    },
]


# ==============================================================
# RUN TEST CASES
# ==============================================================

print()
print("=" * 78)
print("WRAITH MANUAL TARGET VALIDATION TEST")
print("=" * 78)

print("\nManually supplied NPCs:")

for npc in npcs:
    print(
        f"  {npc.name:<12} "
        f"{npc.occupation:<8} "
        f"{npc.rank or 'None':<10} "
        f"{npc.npc_id}"
    )

passed = 0
failed = 0

for number, case in enumerate(TEST_CASES, start=1):

    print()
    print("=" * 78)
    print(f"TEST {number}: {case['name']}")
    print("=" * 78)

    # ----------------------------------------------------------
    # CONSTRUCT OUR OWN LLM OUTPUT
    # ----------------------------------------------------------

    action = ProposedAction(
        action_type=(
            "combat"
            if case["type"] == "npc"
            else "manipulation"
            if case["type"] == "object"
            else "expression"
        ),
        intent=case["input"],
        target_reference=case["reference"],
        target_id=case["given_id"],
        target_type=case["type"],
        target_resolution=case["given_status"],
        original_text=case["input"],
    )

    raw_proposal = ActionProposal(
        actions=[action]
    )

    # The proposer returns our deliberately
    # constructed proposal instead of calling an LLM.

    def fake_action_proposer(
        *,
        player_input,
        location,
        npcs,
    ):
        return raw_proposal

    manager = SceneManager(
        action_proposer=fake_action_proposer,
        location_repository=location_repository,
        npc_repository=npc_repository,
    )

    scene = manager.start_scene(
        location_id=LOCATION_ID,
        player_character_id="test-player",
        npc_ids=[npc.npc_id for npc in npcs],
    )

    # ----------------------------------------------------------
    # RUN THROUGH REAL SCENE MANAGER + VALIDATOR
    # ----------------------------------------------------------

    prepared = manager.prepare_turn(
        scene_id=scene.scene_id,
        player_input=case["input"],
    )

    result = prepared.proposal.actions[0]

    # ----------------------------------------------------------
    # COMPARE
    # ----------------------------------------------------------

    print(f"\nPlayer: {case['input']}")
    print(f"Reference: {case['reference']}")

    print()
    print(f"Given ID:       {case['given_id']}")
    print(f"Validated ID:   {result.target_id}")
    print(f"Expected ID:    {case['expected_id']}")

    print()
    print(f"Given status:    {case['given_status']}")
    print(f"Validated status:{result.target_resolution}")
    print(f"Expected status: {case['expected_status']}")

    correct_id = (
        result.target_id == case["expected_id"]
    )

    correct_status = (
        result.target_resolution == case["expected_status"]
    )

    if correct_id and correct_status:
        passed += 1
        print("\nPASS")
    else:
        failed += 1
        print("\nFAIL - Target validation mismatch")

    # Confirm the scene can still complete its turn,
    # including for unresolved or descriptive targets.

    completed = manager.complete_turn(
        scene_id=scene.scene_id,
        turn_id=prepared.turn_id,
    )

    assert completed.phase == "ready"
    assert completed.turn_number == 1


# ==============================================================
# SUMMARY
# ==============================================================

print()
print("=" * 78)
print("TARGET VALIDATION TEST SUMMARY")
print("=" * 78)

print(f"\nPassed: {passed}")
print(f"Failed: {failed}")
print(f"Total:  {len(TEST_CASES)}")

print()
print("No LLM calls performed.")
print("No database writes performed.")
print("No gameplay mechanics resolved.")

if failed:
    raise AssertionError(
        f"{failed} target validation tests failed."
    )

print()
print("ALL TARGET VALIDATION TESTS PASSED")

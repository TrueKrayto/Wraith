
import re
import time
from types import SimpleNamespace

from backend.level_4_systems import (
    LLMRole,
    SceneManager,
    generate_action_proposal,
    get_llm_client_manager,
)


# ==============================================================
# SETTINGS
# ==============================================================

BETWEEN_CALLS_SECONDS = 8
MAX_ATTEMPTS = 5
RETRY_DELAYS = (15, 30, 60, 90)

LOCATION_ID = "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"


# ==============================================================
# MANUAL NPC DATA
# ==============================================================

NPC_DATA = [
    (
        "11111111-1111-4111-8111-111111111111",
        "John Smith",
        "Guard",
        "Captain",
    ),
    (
        "22222222-2222-4222-8222-222222222222",
        "John Brown",
        "Baker",
        None,
    ),
    (
        "33333333-3333-4333-8333-333333333333",
        "James Miller",
        "Guard",
        "Soldier",
    ),
    (
        "44444444-4444-4444-8444-444444444444",
        "Jane Smith",
        "Healer",
        None,
    ),
    (
        "55555555-5555-4555-8555-555555555555",
        "Mary Jones",
        "Merchant",
        None,
    ),
    (
        "66666666-6666-4666-8666-666666666666",
        "Mark Davis",
        "Guard",
        "Soldier",
    ),
    (
        "77777777-7777-4777-8777-777777777777",
        "Martin Davis",
        "Merchant",
        "Apprentice",
    ),
]

location = SimpleNamespace(
    location_id=LOCATION_ID,
    name="Old Town Square",
    location_type="town_square",
)

npcs = [
    SimpleNamespace(
        npc_id=npc_id,
        name=name,
        species="Human",
        occupation=occupation,
        rank=rank,
    )
    for npc_id, name, occupation, rank in NPC_DATA
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
# STRESS TEST INPUTS
# ==============================================================

TEST_CASES = [
    {
        "name": "Two Johns, different targets",
        "input": (
            "I approach John Smith and warn him, "
            "then turn to John Brown and ask him "
            "whether he has seen James Miller."
        ),
        "review": (
            "John Smith and John Brown must not be "
            "confused. James is mentioned, not addressed."
        ),
    },
    {
        "name": "Same surname, pronoun distraction",
        "input": (
            "I tell Jane Smith that John Smith is lying, "
            "then ask her to keep it secret."
        ),
        "review": (
            "Both communications should target Jane. "
            "John is only the subject of the conversation."
        ),
    },
    {
        "name": "Mark versus Martin",
        "input": (
            "I don't attack Mark Davis. "
            "I attack Martin Davis instead."
        ),
        "review": (
            "Only Martin should be attacked. "
            "The negated attack on Mark is not an action."
        ),
    },
    {
        "name": "Multiple guards and a captain",
        "input": (
            "I approach the guard and ask him to "
            "bring his captain to me."
        ),
        "review": (
            "Choose a reasonable guard. Both actions "
            "should address the same guard. The captain "
            "is mentioned, not directly commanded."
        ),
    },
    {
        "name": "Ambiguous first name",
        "input": (
            "I walk up to John and ask him "
            "what happened here."
        ),
        "review": (
            "Two NPCs are named John. Use a reasonable "
            "default and preserve the same ID for 'him'."
        ),
    },
    {
        "name": "Absent NPC with similar surname",
        "input": (
            "I grab Robert Brown by the collar "
            "and demand an explanation."
        ),
        "review": (
            "Robert Brown is absent. Do not silently "
            "substitute John Brown or another NPC."
        ),
    },
    {
        "name": "Environmental object and NPC",
        "input": (
            "I pick up a cup from the table, "
            "walk over to Mary Jones and hand it to her."
        ),
        "review": (
            "The cup must not need an ID. "
            "Mary must be identified canonically."
        ),
    },
    {
        "name": "Conditional actions and pronouns",
        "input": (
            "If James Miller attacks me, I dodge "
            "and shout for Mark Davis to help me. "
            "Otherwise, I ask James to lower his weapon."
        ),
        "review": (
            "Preserve the alternative conditions, "
            "and distinguish James from Mark."
        ),
    },
    {
        "name": "Competing first names and surnames",
        "input": (
            "I tell John Brown to stay away from "
            "Jane Smith, then I confront John Smith "
            "and accuse him of threatening her."
        ),
        "review": (
            "John Brown, John Smith and Jane Smith "
            "must remain distinct. 'Him' refers to "
            "John Smith and 'her' refers to Jane."
        ),
    },
]


# ==============================================================
# RATE-LIMIT / PROVIDER RETRY HELPERS
# ==============================================================

def is_retryable(error):

    status = getattr(error, "status_code", None)

    if status in (429, 500, 502, 503, 504):
        return True

    error_type = type(error).__name__.lower()
    message = str(error).lower()

    indicators = (
        "ratelimit",
        "rate limit",
        "too many requests",
        "timeout",
        "connection error",
        "temporarily unavailable",
        "tokens per minute",
        "requests per minute",
    )

    if any(
        indicator in error_type or indicator in message
        for indicator in indicators
    ):
        return True

    if (
        isinstance(error, ValueError)
        and "LLM could not generate valid action proposal"
        in str(error)
    ):
        return True

    return False


def get_retry_delay(error, attempt):

    fallback = RETRY_DELAYS[
        min(attempt - 1, len(RETRY_DELAYS) - 1)
    ]

    # Respect a Retry-After header if present.

    response = getattr(error, "response", None)
    headers = getattr(response, "headers", None)

    if headers:
        value = headers.get("retry-after")

        if value:
            try:
                return max(
                    fallback,
                    float(value) + 2,
                )
            except (TypeError, ValueError):
                pass

    # Groq may include a wait duration in its
    # error message instead of a Retry-After header.

    match = re.search(
        r"try again in\s+"
        r"(?:(\d+(?:\.\d+)?)m)?"
        r"\s*(\d+(?:\.\d+)?)s",
        str(error),
        re.IGNORECASE,
    )

    if match:
        minutes = float(match.group(1) or 0)
        seconds = float(match.group(2))

        return max(
            fallback,
            minutes * 60 + seconds + 2,
        )

    return fallback


def prepare_with_retry(
    *,
    manager,
    scene_id,
    player_input,
):

    for attempt in range(1, MAX_ATTEMPTS + 1):

        print(
            f"\nLLM attempt {attempt}/{MAX_ATTEMPTS}"
        )

        try:
            return manager.prepare_turn(
                scene_id=scene_id,
                player_input=player_input,
            )

        except Exception as error:

            print(
                f"Error: {type(error).__name__}: "
                f"{error}"
            )

            if not is_retryable(error):
                raise

            if attempt == MAX_ATTEMPTS:
                raise

            delay = get_retry_delay(
                error,
                attempt,
            )

            print(
                f"Retrying after {delay:.1f} seconds..."
            )

            time.sleep(delay)

    raise RuntimeError(
        "Maximum LLM attempts exhausted."
    )


# ==============================================================
# REAL LLM CLIENT
# ==============================================================

llm_manager = get_llm_client_manager()

selection = llm_manager.get(
    LLMRole.ACTION_PROPOSAL
)

client = selection.client
model = selection.model

# Capture the Action Proposal before validation.

raw_capture = {"proposal": None}


def capturing_action_proposer(
    *,
    player_input,
    location,
    npcs,
):

    proposal = generate_action_proposal(
        client=client,
        model=model,
        player_input=player_input,
        location=location,
        npcs=npcs,
    )

    raw_capture["proposal"] = proposal

    return proposal


# ==============================================================
# REAL SCENE MANAGER, FAKE WORLD DATA
# ==============================================================

manager = SceneManager(
    action_proposer=capturing_action_proposer,
    location_repository=location_repository,
    npc_repository=npc_repository,
)

scene = manager.start_scene(
    location_id=LOCATION_ID,
    player_character_id="test-player",
    npc_ids=[npc.npc_id for npc in npcs],
)


# ==============================================================
# RUN TESTS
# ==============================================================

print()
print("=" * 78)
print("WRAITH ACTION PROPOSER - MULTI-NPC LLM STRESS TEST")
print("=" * 78)

print(f"\nModel: {model}")
print(f"Location: {location.name}")

print("\nManually supplied NPCs:\n")

for npc in npcs:
    print(
        f"  {npc.name:<16}"
        f"{npc.occupation:<12}"
        f"{str(npc.rank or '-'):<12}"
        f"{npc.npc_id}"
    )

completed = 0
failed = 0

for index, case in enumerate(TEST_CASES, start=1):

    print()
    print("=" * 78)
    print(
        f"TEST {index}/{len(TEST_CASES)}: "
        f"{case['name']}"
    )
    print("=" * 78)

    print(f"\nPLAYER INPUT:\n{case['input']}")
    print(f"\nEXPECTED BEHAVIOUR:\n{case['review']}")

    raw_capture["proposal"] = None

    try:

        prepared = prepare_with_retry(
            manager=manager,
            scene_id=scene.scene_id,
            player_input=case["input"],
        )

        raw = raw_capture["proposal"]
        validated = prepared.proposal

        # ------------------------------------------------------
        # PRINT ORIGINAL LLM PROPOSAL
        # ------------------------------------------------------

        print("\n--- RAW LLM ACTION PROPOSAL ---\n")

        print(
            raw.model_dump_json(indent=2)
        )

        # ------------------------------------------------------
        # PRINT VALIDATED PROPOSAL
        # ------------------------------------------------------

        print("\n--- VALIDATED ACTION PROPOSAL ---\n")

        print(
            validated.model_dump_json(indent=2)
        )

        # ------------------------------------------------------
        # DISPLAY VALIDATOR CHANGES
        # ------------------------------------------------------

        print("\n--- VALIDATOR CHANGES ---\n")

        changes = 0

        for action_number, (before, after) in enumerate(
            zip(raw.actions, validated.actions),
            start=1,
        ):

            old_target = (
                before.target_id,
                before.target_type,
                before.target_resolution,
            )

            new_target = (
                after.target_id,
                after.target_type,
                after.target_resolution,
            )

            if old_target != new_target:

                changes += 1

                print(
                    f"Action {action_number}: "
                    f"{before.target_reference}"
                )

                print(
                    f"  Before: {old_target}"
                )

                print(
                    f"  After:  {new_target}"
                )

        if changes == 0:
            print("No target changes.")

        # ------------------------------------------------------
        # COMPLETE TEST TURN
        # ------------------------------------------------------

        manager.complete_turn(
            scene_id=scene.scene_id,
            turn_id=prepared.turn_id,
        )

        completed += 1

        print("\nRESULT: PROPOSAL GENERATED")

    except Exception as error:

        failed += 1

        print(
            "\nRESULT: ERROR - "
            f"{type(error).__name__}: {error}"
        )

        # Do not silently reset a pending scene turn.
        # This indicates a test/processing issue.

        if scene.phase != "ready":
            raise

    # ----------------------------------------------------------
    # PAUSE BEFORE NEXT LLM CALL
    # ----------------------------------------------------------

    if index < len(TEST_CASES):

        print(
            f"\nPausing {BETWEEN_CALLS_SECONDS} "
            "seconds before next test..."
        )

        time.sleep(BETWEEN_CALLS_SECONDS)


# ==============================================================
# SUMMARY
# ==============================================================

print()
print("=" * 78)
print("MULTI-NPC LLM STRESS TEST COMPLETE")
print("=" * 78)

print(f"\nScenarios: {len(TEST_CASES)}")
print(f"Generated: {completed}")
print(f"Errors:    {failed}")

print(f"\nFinal scene turn: {scene.turn_number}")

print("\nNo real database used.")
print("No game mechanics resolved.")

print()
print(
    "Review the LLM and validated outputs "
    "for interpretation accuracy."
)

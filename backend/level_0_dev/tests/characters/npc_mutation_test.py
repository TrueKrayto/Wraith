from dataclasses import asdict

from backend.level_3_services import (
    mutate_npc_from_prompt,
)

from backend.level_4_systems import (
    get_npc_repository,
)

from backend.level_0_dev.tests.characters.character_sheet_showcase import (
    print_character_sheet,
)


# ==================================================================
# HELPERS
# ==================================================================

def find_changes(
    before,
    after,
    path="",
):
    """
    Recursively compare two character-state dictionaries.

    Returns changes as:
        (field_path, old_value, new_value)
    """

    changes = []

    if isinstance(before, dict) and isinstance(after, dict):

        keys = set(before) | set(after)

        for key in sorted(keys):

            field_path = (
                f"{path}.{key}"
                if path
                else key
            )

            if key not in before:
                changes.append(
                    (field_path, "<missing>", after[key])
                )

            elif key not in after:
                changes.append(
                    (field_path, before[key], "<removed>")
                )

            else:
                changes.extend(
                    find_changes(
                        before[key],
                        after[key],
                        field_path,
                    )
                )

    elif before != after:

        changes.append(
            (path, before, after)
        )

    return changes


# ==================================================================
# TEST START
# ==================================================================

print()
print("=" * 78)
print("WRAITH NPC MUTATION TEST")
print("=" * 78)

repository = get_npc_repository()


# ==================================================================
# 1. SELECT NPC
# ==================================================================

npc_id = input(
    "\nEnter NPC UID:\n> "
).strip()

if not npc_id:
    raise ValueError(
        "NPC UID is required."
    )

npc = repository.get(
    npc_id
)

if npc is None:
    raise ValueError(
        f"NPC not found: {npc_id}"
    )

before_state = asdict(
    npc
)


# ==================================================================
# 2. BEFORE MUTATION
# ==================================================================

print()
print("=" * 78)
print("1. CHARACTER BEFORE MUTATION")
print("=" * 78)
print()

print_character_sheet(
    npc_id
)


# ==================================================================
# 3. GET MUTATION INSTRUCTION
# ==================================================================

print()
print("=" * 78)
print("2. MUTATION INSTRUCTION")
print("=" * 78)

instruction = input(
    f"\nWhat should change about {npc.name}?\n> "
).strip()

if not instruction:
    raise ValueError(
        "Mutation instruction is required."
    )

# Explicitly identify the canonical NPC so the interpreter
# does not have to rely on a name match alone.

mutation_prompt = f"""
TARGET NPC:
Name: {npc.name}
NPC ID: {npc.npc_id}

Apply the following changes to this NPC only:

{instruction}
"""


# ==================================================================
# 4. RUN MUTATION PIPELINE
# ==================================================================

print()
print("=" * 78)
print("3. RUNNING NPC MUTATION")
print("=" * 78)

print(
    f"\nTarget: {npc.name}"
)

print(
    f"UID: {npc.npc_id}"
)

print(
    f"Instruction: {instruction}"
)

print(
    "\nRunning mutation..."
)

mutated_npc = mutate_npc_from_prompt(
    prompt=mutation_prompt,
    npc_id=npc_id,
)

if mutated_npc is None:
    raise RuntimeError(
        "Mutation service did not return an NPC."
    )

if mutated_npc.npc_id != npc_id:
    raise AssertionError(
        "Mutation selected the wrong NPC!\n"
        f"Expected: {npc_id}\n"
        f"Received: {mutated_npc.npc_id}"
    )


# ==================================================================
# 5. RELOAD FROM PERSISTENCE
# ==================================================================

persisted_npc = repository.get(
    npc_id
)

if persisted_npc is None:
    raise RuntimeError(
        "NPC disappeared after mutation."
    )

after_state = asdict(
    persisted_npc
)


# ==================================================================
# 6. COMPARE CHANGES
# ==================================================================

print()
print("=" * 78)
print("4. DETECTED STATE CHANGES")
print("=" * 78)

changes = find_changes(
    before_state,
    after_state,
)

if changes:

    for field, old_value, new_value in changes:

        print()
        print(
            f"Field: {field}"
        )

        print(
            f"  Before: {old_value}"
        )

        print(
            f"  After:  {new_value}"
        )

else:

    print(
        "\nNo state changes detected."
    )


# ==================================================================
# 7. CHARACTER AFTER MUTATION
# ==================================================================

print()
print()
print("=" * 78)
print("5. CHARACTER AFTER MUTATION")
print("=" * 78)
print()

print_character_sheet(
    npc_id
)


# ==================================================================
# 8. TEST SUMMARY
# ==================================================================

print()
print("=" * 78)
print("NPC MUTATION TEST SUMMARY")
print("=" * 78)

print(
    f"NPC: {persisted_npc.name}"
)

print(
    f"NPC UID: {persisted_npc.npc_id}"
)

print(
    f"Fields changed: {len(changes)}"
)

print(
    "Persisted: Yes"
)

if not changes:
    raise AssertionError(
        "Mutation completed but made no state changes."
    )

print()
print("=" * 78)
print("NPC MUTATION TEST PASSED")
print("=" * 78)
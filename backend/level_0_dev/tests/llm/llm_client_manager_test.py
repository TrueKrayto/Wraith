from backend.level_4_systems.llm.LLMClientManager import (
    LLMRole,
    get_llm_client_manager,
)


TEST_MODEL = "test/model-do-not-call"


print()
print("=" * 78)
print("WRAITH LLM CLIENT MANAGER TEST")
print("=" * 78)


# ==================================================================
# 1. LOAD MANAGER
# ==================================================================

manager = get_llm_client_manager()

print()
print("1. MANAGER LOADED")
print("-" * 78)

default_selection = manager.get(
    LLMRole.DEFAULT
)

print(
    f"Default model: "
    f"{default_selection.model}"
)

print(
    f"Client type: "
    f"{type(default_selection.client).__name__}"
)


# ==================================================================
# 2. CHECK ALL CURRENT ROLE ASSIGNMENTS
# ==================================================================

print()
print("2. CURRENT ROLE ASSIGNMENTS")
print("-" * 78)

for role in LLMRole:

    selection = manager.get(
        role
    )

    print(
        f"{role.value:<24} "
        f"{selection.model}"
    )


# ==================================================================
# 3. SWITCH ONE ROLE
# ==================================================================

print()
print("3. SWITCH NPC ENRICHMENT MODEL")
print("-" * 78)

original_npc_model = manager.get_model(
    LLMRole.NPC_ENRICHMENT
)

original_location_model = manager.get_model(
    LLMRole.LOCATION_ENRICHMENT
)

manager.set_model(
    LLMRole.NPC_ENRICHMENT,
    TEST_MODEL,
)

new_npc_model = manager.get_model(
    LLMRole.NPC_ENRICHMENT
)

unchanged_location_model = manager.get_model(
    LLMRole.LOCATION_ENRICHMENT
)

print(
    f"NPC enrichment before: "
    f"{original_npc_model}"
)

print(
    f"NPC enrichment after:  "
    f"{new_npc_model}"
)

print(
    f"Location enrichment:   "
    f"{unchanged_location_model}"
)


assert (
    new_npc_model
    == TEST_MODEL
)

assert (
    unchanged_location_model
    == original_location_model
)

print()
print(
    "PASS: NPC enrichment changed independently."
)


# ==================================================================
# 4. STRING ROLE LOOKUP
# ==================================================================

print()
print("4. STRING ROLE LOOKUP")
print("-" * 78)

string_selection = manager.get(
    "npc_enrichment"
)

print(
    f"npc_enrichment -> "
    f"{string_selection.model}"
)

assert (
    string_selection.model
    == TEST_MODEL
)

print()
print(
    "PASS: String role resolved correctly."
)


# ==================================================================
# 5. RESET SINGLE ROLE
# ==================================================================

print()
print("5. RESET NPC ENRICHMENT")
print("-" * 78)

manager.reset_model(
    LLMRole.NPC_ENRICHMENT
)

reset_npc_model = manager.get_model(
    LLMRole.NPC_ENRICHMENT
)

print(
    f"Reset model: "
    f"{reset_npc_model}"
)

assert (
    reset_npc_model
    == default_selection.model
)

print()
print(
    "PASS: Role reset to default model."
)


# ==================================================================
# 6. INVALID ROLE SHOULD FAIL
# ==================================================================

print()
print("6. INVALID ROLE CHECK")
print("-" * 78)

try:

    manager.get(
        "npc_enricment"
    )

except ValueError as error:

    print(
        f"Expected failure: "
        f"{error}"
    )

else:

    raise AssertionError(
        "Invalid LLM role did not raise ValueError."
    )

print()
print(
    "PASS: Invalid role rejected."
)


# ==================================================================
# 7. RESET EVERYTHING
# ==================================================================

print()
print("7. RESET ALL")
print("-" * 78)

manager.set_model(
    LLMRole.NPC_CREATION,
    TEST_MODEL,
)

manager.set_model(
    LLMRole.LOCATION_CREATION,
    TEST_MODEL,
)

manager.reset_all()

for role in LLMRole:

    model = manager.get_model(
        role
    )

    assert (
        model
        == default_selection.model
    )

print(
    "PASS: Every role restored to default."
)


# ==================================================================
# RESULT
# ==================================================================

print()
print("=" * 78)
print("LLM CLIENT MANAGER TEST PASSED")
print("=" * 78)
print()
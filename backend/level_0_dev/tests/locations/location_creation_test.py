from backend.level_3_services.location.creation import (
    create_location_from_prompt,
)


LOCATION_PROMPT = """
Azzinoth the dark temple of scurge lord Radan
"""


print("\n=== LOCATION CREATION TEST ===")


result = create_location_from_prompt(
    location_prompt=LOCATION_PROMPT,    
)


print("\n--- LOCATION TREE ---")

for location in result.locations:

    if location.parent_id is None:
        depth = 0

    else:
        parent = next(
            (
                candidate
                for candidate in result.locations
                if candidate.location_id
                == location.parent_id
            ),
            None,
        )

        if parent is None:
            depth = 1

        elif parent.parent_id is None:
            depth = 1

        else:
            depth = 2

    indent = "    " * depth

    print(
        f"{indent}"
        f"{location.name} "
        f"[{location.location_type}]"
    )


    print(
        f"{indent}"
        f"  ID: {location.location_id}"
    )

    print(
        f"{indent}"
        f"  Parent: {location.parent_id}"
    )

    print(
        f"{indent}"
        f"  Structure generated: "
        f"{location.structure_generated}"
    )

    print(
        f"{indent}"
        f"  Enriched: {location.enriched}"
    )

    print(
        f"{indent}"
        f"  Brief: {location.brief_description}"
    )


print("\n--- KEY NPC SKELETONS ---")

if not result.key_npcs:
    print("None")

for npc in result.key_npcs:
    print(
        f"- {npc.name}"
        f" | occupation={npc.occupation}"
        f" | rank={npc.rank}"
        f" | {npc.brief_description}"
    )


print("\n--- SUMMARY ---")

print(
    f"Locations created: "
    f"{len(result.locations)}"
)

print(
    f"Creation shape: "
    f"{result.creation_shape}"
)

print(
    f"Key NPC skeletons: "
    f"{len(result.key_npcs)}"
)

print(
    f"Already generated: "
    f"{result.already_generated}"
)
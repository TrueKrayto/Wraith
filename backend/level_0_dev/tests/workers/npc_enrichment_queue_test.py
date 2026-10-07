import json
import time
from urllib.request import Request, urlopen

from backend.level_4_systems import get_npc_repository


API_URL = "http://127.0.0.1:8000/npc/create"


NPC_PROMPTS = [
    (
        "Create a level 6 human male farmer named Tomas. "
        "He is patient, hardworking, and skilled at farming."
    ),
    (
        "Create a level 9 human female hunter named Mira. "
        "She is observant, independent, and skilled at tracking."
    ),
    (
        "Create a level 12 dwarf male guard named Borin. "
        "He is disciplined, stubborn, and experienced in combat."
    ),
    (
        "Create a level 7 human female healer named Lena. "
        "She is calm, practical, and skilled at medicine."
    ),
    (
        "Create a level 15 elf male scout named Cael. "
        "He is alert, reserved, and highly skilled at scouting."
    ),
]


repository = get_npc_repository()

created_npcs = []


def create_npc(prompt: str) -> dict:
    payload = json.dumps(
        {
            "prompt": prompt,
        }
    ).encode("utf-8")

    request = Request(
        API_URL,
        data=payload,
        headers={
            "Content-Type": "application/json",
        },
        method="POST",
    )

    with urlopen(request) as response:
        return json.loads(
            response.read().decode("utf-8")
        )


def print_statuses():
    print("\nCurrent enrichment state:")

    for index, created in enumerate(
        created_npcs,
        start=1,
    ):
        npc = repository.get(
            created["npc_id"]
        )

        if npc is None:
            status = "MISSING"
        elif npc.enriched:
            status = "ENRICHED"
        else:
            status = "WAITING"

        print(
            f"  {index}. "
            f"{created['name']}: "
            f"{status}"
        )


print("\n=== NPC ENRICHMENT QUEUE TEST ===")


for index, prompt in enumerate(
    NPC_PROMPTS,
    start=1,
):
    print(
        f"\n{'=' * 60}"
    )
    print(
        f"CREATING NPC {index}/{len(NPC_PROMPTS)}"
    )
    print(
        f"{'=' * 60}"
    )

    npc = create_npc(prompt)

    created_npcs.append(npc)

    print(
        f"Created: {npc['name']} "
        f"({npc['npc_id']})"
    )

    print(
        f"Creation response enriched: "
        f"{npc['enriched']}"
    )

    print_statuses()


print(
    "\n"
    + "=" * 60
)
print("ALL NPC CREATION REQUESTS COMPLETE")
print("=" * 60)

print_statuses()


# --------------------------------------------------------------
# OPTIONAL CATCH-UP OBSERVATION
#
# Watch the worker finish whatever remains in its queue.
# --------------------------------------------------------------

print(
    "\nWatching enrichment worker finish remaining jobs..."
)

while True:
    remaining = []

    for created in created_npcs:
        npc = repository.get(
            created["npc_id"]
        )

        if npc is not None and not npc.enriched:
            remaining.append(
                npc.name
            )

    if not remaining:
        break

    print(
        "Waiting on: "
        + ", ".join(remaining)
    )

    time.sleep(1)


print("\nAll five NPCs enriched.")

print_statuses()
import json
from dataclasses import asdict
from pathlib import Path

from backend.level_5_entities.characters import (
    NPC,
    StatusEffect,
)


STORE_PATH = (
    Path(__file__).resolve().parent
    / "temp_npcs.json"
)


def save_npcs(
    npcs: dict[str, NPC],
) -> None:
    """
    Save the current temporary NPC store to disk.
    """

    STORE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    data = {
        npc_id: asdict(npc)
        for npc_id, npc in npcs.items()
    }

    STORE_PATH.write_text(
        json.dumps(
            data,
            indent=2,
        ),
        encoding="utf-8",
    )


def load_npcs() -> dict[str, NPC]:
    """
    Load NPCs from the temporary JSON store.
    """

    if not STORE_PATH.exists():
        return {}

    raw_data = json.loads(
        STORE_PATH.read_text(
            encoding="utf-8",
        )
    )

    npcs: dict[str, NPC] = {}

    for npc_id, npc_data in raw_data.items():

        status_data = npc_data.pop(
            "status_effects",
            {},
        )

        status_effects = {
            name: StatusEffect(**effect)
            for name, effect in status_data.items()
        }

        npc = NPC(
            **npc_data,
            status_effects=status_effects,
        )

        npcs[npc_id] = npc

    return npcs
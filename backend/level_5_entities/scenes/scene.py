from dataclasses import dataclass, field
from typing import Literal
from uuid import uuid4

from .intent import IntentResult


ScenePhase = Literal[
    "ready",
    "awaiting_resolution",
]


@dataclass
class Scene:
    """
    Lightweight scene metadata.

    Stores canonical references only.
    No dependency on NPC or Location structures.
    """

    location_id: str
    player_character_id: str

    npc_ids: list[str] = field(
        default_factory=list
    )

    turn_number: int = 0

    phase: ScenePhase = "ready"

    pending_turn_id: str | None = None

    scene_id: str = field(
        default_factory=lambda: str(uuid4())
    )


@dataclass(frozen=True)
class PreparedTurn:
    """
    Player input and extracted intentions.

    Contains references to scene entities,
    never the entities themselves.
    """

    turn_id: str
    scene_id: str
    turn_number: int

    player_input: str
    player_character_id: str

    location_id: str
    npc_ids: tuple[str, ...]

    intent: IntentResult
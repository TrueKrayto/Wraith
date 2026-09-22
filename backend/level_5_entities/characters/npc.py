from dataclasses import dataclass, field
from uuid import uuid4

from .status_effects import StatusEffect


@dataclass
class NPC:
    # Identity
    name: str
    age: int | None = None
    species: str = "Human"
    sex: str | None = None

    # Social / world identity
    faction: str | None = None
    occupation: str | None = None
    rank: str | None = None
    home: str | None = None

    # Current world state
    current_location: str | None = None
    alive: bool = True

    # Character importance / progression
    tier: str = "low"
    level: int = 1

    # Stable narrative identity
    description: str | None = None
    personality: str | None = None
    appearance: str | None = None
    mannerisms: str | None = None
    speech_style: str | None = None

    # Enrichment state
    enriched: bool = False

    # Mechanical character data
    attributes: dict[str, int] = field(default_factory=dict)
    skills: dict[str, int] = field(default_factory=dict)
    resources: dict[str, dict[str, int]] = field(
        default_factory=dict
    )

    # Active character state
    status_effects: dict[str, StatusEffect] = field(
        default_factory=dict
    )

    # Internal unique identifier
    npc_id: str = field(
        default_factory=lambda: str(uuid4())
    )
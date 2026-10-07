from dataclasses import dataclass, field
from uuid import uuid4


@dataclass
class Location:
    # Identity
    name: str
    location_type: str

    # Hierarchy
    parent_id: str | None = None

    # Canonical skeleton information
    brief_description: str | None = None

    # Rich location information
    description: str | None = None

    # Generation state
    structure_generated: bool = False
    enriched: bool = False

    # Expansion rules
    children_locked: bool = False
    child_limit: int | None = None

    # Internal unique identifier
    location_id: str = field(
        default_factory=lambda: str(uuid4())
    )
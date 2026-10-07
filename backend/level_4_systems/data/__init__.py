from .location_repository import (
    LocationRepository,
    TempJSONLocationRepository,
    get_location_repository,
    set_location_repository,
)

from .npc_repository import (
    NPCRepository,
    TempJSONNPCRepository,
    get_npc_repository,
    set_npc_repository,
)


__all__ = [
    "LocationRepository",
    "TempJSONLocationRepository",
    "get_location_repository",
    "set_location_repository",
    "NPCRepository",
    "TempJSONNPCRepository",
    "get_npc_repository",
    "set_npc_repository",
]
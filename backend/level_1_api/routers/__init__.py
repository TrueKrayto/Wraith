from .actions import router as actions_router
from .attributes import router as attributes_router
from .characters import router as characters_router
from .checks import router as checks_router
from .combat import router as combat_router
from .npc import router as npc_router
from .play import router as play_router
from .resources import router as resources_router
from .skills import router as skills_router


__all__ = [
    "actions_router",
    "attributes_router",
    "characters_router",
    "checks_router",
    "combat_router",
    "npc_router",
    "play_router",
    "resources_router",
    "skills_router",
]
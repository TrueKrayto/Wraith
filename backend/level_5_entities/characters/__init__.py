from . import schemas

from .attributes import (
    ATTRIBUTE_NAMES,
    clamp_attribute,
    
)

from .levels import (
    MIN_LEVEL,
    MAX_LEVEL,
    clamp_level,
)

from .npc import NPC
from .npc_manager import create_npc
from .enrichment import apply_npc_enrichment

from .resources import (
    clamp_resource,  
    apply_damage,
    apply_healing,
)

from .skills import (
    CORE_SKILLS,
    get_skill_cap,
    clamp_skill,    
)

from .stat_bands import StatBand
from .statblock_generator import generate_character_statblock
from .status_effects import StatusEffect

from .mutations import (
    update_npc,
    update_attribute,
    add_skill,
    update_skill,
    remove_skill,
    update_resource,
    add_status_effect,
    update_status_effect,
    remove_status_effect,
    has_status_effect,
    apply_npc_mutation,
)
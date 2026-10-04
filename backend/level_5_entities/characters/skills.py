from .levels import clamp_level


SKILL_CAP_PER_LEVEL = 5


# Universal skills available to all characters.
# More specific skills can be added dynamically later.
CORE_SKILLS = (
    "charisma",
    "stealth",
    "perception",
    "survival",
    "combat",
    "magic",
)


def get_skill_cap(character_level: int) -> int:
    """Return the maximum skill level allowed for a character level."""
    level = clamp_level(character_level)
    return level * SKILL_CAP_PER_LEVEL


def clamp_skill(skill_level: int, character_level: int) -> int:
    """Keep a skill between 0 and the character's current skill cap."""
    maximum = get_skill_cap(character_level)
    return max(0, min(skill_level, maximum))


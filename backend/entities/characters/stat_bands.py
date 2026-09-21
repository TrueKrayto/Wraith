from enum import Enum

from .attributes import clamp_attribute
from .levels import (
    MIN_LEVEL,
    MAX_LEVEL,
    clamp_level,
)
from .skills import get_skill_cap


class StatBand(str, Enum):
    LOW = "low"
    MID = "mid"
    HIGH = "high"


# Attribute bands use the fixed 1-20 attribute scale.
#
# Each band contains:
# (
#     (level_1_min, level_1_max),
#     (level_50_min, level_50_max),
# )
#
# The valid range moves upward as character level increases.

ATTRIBUTE_BANDS = {
    StatBand.LOW: (
        (1, 4),
        (3, 7),
    ),
    StatBand.MID: (
        (4, 8),
        (8, 14),
    ),
    StatBand.HIGH: (
        (8, 12),
        (14, 20),
    ),
}


# Skill bands are percentages of the character's
# current skill cap.
#
# Skill cap = character level * 5

SKILL_BANDS = {
    StatBand.LOW: (0.05, 0.25),
    StatBand.MID: (0.30, 0.60),
    StatBand.HIGH: (0.65, 0.90),
}


def get_attribute_range(
    band: StatBand,
    level: int,
) -> tuple[int, int]:
    """Return the valid attribute range for a band and level."""

    level = clamp_level(level)

    (
        (level_1_min, level_1_max),
        (level_50_min, level_50_max),
    ) = ATTRIBUTE_BANDS[band]

    # 0.0 at level 1
    # 1.0 at level 50
    progress = (
        (level - MIN_LEVEL)
        / (MAX_LEVEL - MIN_LEVEL)
    )

    minimum = round(
        level_1_min
        + (level_50_min - level_1_min) * progress
    )

    maximum = round(
        level_1_max
        + (level_50_max - level_1_max) * progress
    )

    return (
        clamp_attribute(minimum),
        clamp_attribute(maximum),
    )


def get_skill_range(
    band: StatBand,
    level: int,
) -> tuple[int, int]:
    """Return the valid skill range for a band and level."""

    level = clamp_level(level)

    skill_cap = get_skill_cap(level)

    minimum_percent, maximum_percent = SKILL_BANDS[band]

    minimum = round(skill_cap * minimum_percent)
    maximum = round(skill_cap * maximum_percent)

    return minimum, maximum
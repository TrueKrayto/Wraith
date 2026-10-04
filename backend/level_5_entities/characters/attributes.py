MIN_ATTRIBUTE = 1
MAX_ATTRIBUTE = 20


ATTRIBUTE_NAMES = (
    "strength",
    "agility",
    "endurance",
    "intellect",
    "attunement",
    "presence",
)


def clamp_attribute(value: int) -> int:
    """Keep an attribute inside the valid range."""
    return max(MIN_ATTRIBUTE, min(value, MAX_ATTRIBUTE))



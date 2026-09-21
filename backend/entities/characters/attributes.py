MIN_ATTRIBUTE = 1
MAX_ATTRIBUTE = 20
DEFAULT_ATTRIBUTE = 5


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


def default_attributes() -> dict[str, int]:
    """Return a fresh default attribute set for a new character."""
    return {
        name: DEFAULT_ATTRIBUTE
        for name in ATTRIBUTE_NAMES
    }
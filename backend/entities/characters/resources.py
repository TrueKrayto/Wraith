DEFAULT_RESOURCES = {
    "health": 100,
    "mana": 100,
    "stamina": 100,
}


def default_resources() -> dict[str, dict[str, int]]:
    """Return a fresh set of default character resources."""
    return {
        name: {
            "current": maximum,
            "maximum": maximum,
        }
        for name, maximum in DEFAULT_RESOURCES.items()
    }


def clamp_resource(current: int, maximum: int) -> int:
    """Keep a resource between 0 and its maximum."""
    return max(0, min(current, maximum))


def apply_damage(current_health: int, damage: int) -> int:
    """Apply damage and return the new health value."""
    return max(0, current_health - max(0, damage))


def apply_healing(
    current_health: int,
    maximum_health: int,
    healing: int,
) -> int:
    """Apply healing without exceeding maximum health."""
    return min(
        maximum_health,
        current_health + max(0, healing),
    )
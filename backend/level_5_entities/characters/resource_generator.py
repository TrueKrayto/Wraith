from .levels import clamp_level


def generate_resources(
    level: int,
    attributes: dict[str, int],
) -> dict[str, dict[str, int]]:
    """Generate character resources from level and attributes."""

    level = clamp_level(level)

    endurance = attributes["endurance"]
    attunement = attributes["attunement"]
    agility = attributes["agility"]

    health = (
        40
        + (endurance * 10)
        + (level * 10)
    )

    mana = (
        40
        + (attunement * 10)
        + (level * 10)
    )

    stamina = (
        40
        + (endurance * 5)
        + (agility * 5)
        + (level * 10)
    )

    maximums = {
        "health": health,
        "mana": mana,
        "stamina": stamina,
    }

    return {
        name: {
            "current": maximum,
            "maximum": maximum,
        }
        for name, maximum in maximums.items()
    }
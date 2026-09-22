from backend.level_5_entities.characters import clamp_level


def calculate_damage(
    base_damage: int,
    character_level: int,
    core_skill: int,
    specialization: int = 0,
    power_multiplier: float = 1.0,
    gear_bonus: int = 0,
) -> int:
    level = clamp_level(character_level)

    damage = (
        base_damage
        + level
        + core_skill
        + specialization
        + gear_bonus
    )

    damage *= power_multiplier

    return max(0, round(damage))
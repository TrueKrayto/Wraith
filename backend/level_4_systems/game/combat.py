from .checks import opposed_check
from .damage import calculate_damage

def resolve_attack(
    attacker_power: int,
    defender_power: int,
    base_damage: int,
    character_level: int,
    core_skill: int,
    specialization: int = 0,
    power_multiplier: float = 1.0,
    gear_bonus: int = 0,
) -> dict:
    check = opposed_check(
        attacker_power=attacker_power,
        defender_power=defender_power,
    )

    if not check["success"]:
        return {
            **check,
            "hit": False,
            "damage": 0,
        }

    damage = calculate_damage(
        base_damage=base_damage,
        character_level=character_level,
        core_skill=core_skill,
        specialization=specialization,
        power_multiplier=power_multiplier,
        gear_bonus=gear_bonus,
    )

    return {
        **check,
        "hit": True,
        "damage": damage,
    }
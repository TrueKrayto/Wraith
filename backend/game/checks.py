from backend.game.dice import roll_d20
from backend.game.levels import clamp_level


def calculate_check_power(
    character_level: int,
    attribute: int,
    core_skill: int,
    specialization: int = 0,
    gear_bonus: int = 0,
    situational_bonus: int = 0,
) -> int:
    level = clamp_level(character_level)

    return (
        level
        + attribute
        + core_skill
        + specialization
        + gear_bonus
        + situational_bonus
    )


def opposed_check(
    attacker_power: int,
    defender_power: int,
) -> dict:
    attacker_roll = roll_d20()
    defender_roll = roll_d20()

    attacker_total = attacker_power + attacker_roll
    defender_total = defender_power + defender_roll

    return {
        "attacker_roll": attacker_roll,
        "defender_roll": defender_roll,
        "attacker_total": attacker_total,
        "defender_total": defender_total,
        "success": attacker_total > defender_total,
    }

def difficulty_check(
    character_power: int,
    difficulty: int,
) -> dict:
    roll = roll_d20()
    total = character_power + roll

    return {
        "roll": roll,
        "total": total,
        "difficulty": difficulty,
        "success": total >= difficulty,
    }
from sqlalchemy.orm import Session

from backend.game.checks import difficulty_check, opposed_check
from backend.services.resources import spend_resource
from backend.services.stats import get_check_power


def resolve_character_check(
    db: Session,
    character_id: int,
    attribute_name: str,
    core_skill_name: str,
    difficulty: int,
    specialization_name: str | None = None,
    gear_bonus: int = 0,
    situational_bonus: int = 0,
    resource_name: str | None = None,
    resource_cost: int = 0,
) -> dict:
    """
    Resolve a difficulty check using the character's stored stats.

    Optionally spend a resource before resolving the check.
    """

    character_power = get_check_power(
        db=db,
        character_id=character_id,
        attribute_name=attribute_name,
        core_skill_name=core_skill_name,
        specialization_name=specialization_name,
        gear_bonus=gear_bonus,
        situational_bonus=situational_bonus,
    )

    if resource_name is not None and resource_cost > 0:
        resource = spend_resource(
            db=db,
            character_id=character_id,
            resource_name=resource_name,
            amount=resource_cost,
        )

        resource_remaining = resource.current
    else:
        resource_remaining = None

    result = difficulty_check(
        character_power=character_power,
        difficulty=difficulty,
    )

    result["character_power"] = character_power

    if resource_name is not None:
        result["resource_name"] = resource_name
        result["resource_cost"] = resource_cost
        result["resource_remaining"] = resource_remaining

    return result


def resolve_opposed_character_check(
    db: Session,
    attacker_character_id: int,
    defender_character_id: int,
    attacker_attribute: str,
    attacker_core_skill: str,
    defender_attribute: str,
    defender_core_skill: str,
    attacker_specialization: str | None = None,
    defender_specialization: str | None = None,
    attacker_gear_bonus: int = 0,
    defender_gear_bonus: int = 0,
    attacker_situational_bonus: int = 0,
    defender_situational_bonus: int = 0,
) -> dict:
    """
    Resolve an opposed check using both characters' stored stats.
    """

    attacker_power = get_check_power(
        db=db,
        character_id=attacker_character_id,
        attribute_name=attacker_attribute,
        core_skill_name=attacker_core_skill,
        specialization_name=attacker_specialization,
        gear_bonus=attacker_gear_bonus,
        situational_bonus=attacker_situational_bonus,
    )

    defender_power = get_check_power(
        db=db,
        character_id=defender_character_id,
        attribute_name=defender_attribute,
        core_skill_name=defender_core_skill,
        specialization_name=defender_specialization,
        gear_bonus=defender_gear_bonus,
        situational_bonus=defender_situational_bonus,
    )

    result = opposed_check(
        attacker_power=attacker_power,
        defender_power=defender_power,
    )

    result["attacker_power"] = attacker_power
    result["defender_power"] = defender_power

    return result
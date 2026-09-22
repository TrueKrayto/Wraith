from sqlalchemy.orm import Session

from backend.level_4_systems.game import resolve_attack

from .resources import (
    change_resource,
    spend_resource,
)
from .stats import (
    get_character,
    get_check_power,
    get_skill_level,
)


def resolve_and_apply_attack(
    db: Session,
    attacker_character_id: int,
    defender_character_id: int,
    attacker_attribute: str,
    attacker_core_skill: str,
    attacker_specialization: str | None,
    defender_attribute: str,
    defender_core_skill: str,
    defender_specialization: str | None,
    base_damage: int,
    power_multiplier: float = 1.0,
    gear_bonus: int = 0,
    resource_name: str | None = None,
    resource_cost: int = 0,
) -> dict:
    """
    Resolve an attack using stored character stats,
    optionally spend a resource cost,
    then apply damage to the defender's health.
    """

    attacker = get_character(
        db=db,
        character_id=attacker_character_id,
    )

    attacker_power = get_check_power(
        db=db,
        character_id=attacker_character_id,
        attribute_name=attacker_attribute,
        core_skill_name=attacker_core_skill,
        specialization_name=attacker_specialization,
    )

    defender_power = get_check_power(
        db=db,
        character_id=defender_character_id,
        attribute_name=defender_attribute,
        core_skill_name=defender_core_skill,
        specialization_name=defender_specialization,
    )

    attacker_core_skill_level = get_skill_level(
        db=db,
        character_id=attacker_character_id,
        skill_name=attacker_core_skill,
    )

    attacker_specialization_level = 0

    if attacker_specialization is not None:
        attacker_specialization_level = get_skill_level(
            db=db,
            character_id=attacker_character_id,
            skill_name=attacker_specialization,
        )

    if resource_name is not None and resource_cost > 0:
        spend_resource(
            db=db,
            character_id=attacker_character_id,
            resource_name=resource_name,
            amount=resource_cost,
        )

    result = resolve_attack(
        attacker_power=attacker_power,
        defender_power=defender_power,
        base_damage=base_damage,
        character_level=attacker.level,
        core_skill=attacker_core_skill_level,
        specialization=attacker_specialization_level,
        power_multiplier=power_multiplier,
        gear_bonus=gear_bonus,
    )

    if result["hit"] and result["damage"] > 0:
        health = change_resource(
            db=db,
            character_id=defender_character_id,
            resource_name="health",
            amount=-result["damage"],
        )
    else:
        health = change_resource(
            db=db,
            character_id=defender_character_id,
            resource_name="health",
            amount=0,
        )

    result["attacker_power"] = attacker_power
    result["defender_power"] = defender_power
    result["defender_health"] = health.current

    return result
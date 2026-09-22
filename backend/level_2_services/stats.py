from sqlalchemy.orm import Session

from backend import models
from backend.game.checks import calculate_check_power


def get_character(
    db: Session,
    character_id: int,
) -> models.Character:
    character = (
        db.query(models.Character)
        .filter(models.Character.id == character_id)
        .first()
    )

    if character is None:
        raise ValueError(
            f"Character {character_id} not found."
        )

    return character


def get_attribute_value(
    db: Session,
    character_id: int,
    attribute_name: str,
) -> int:
    attribute = (
        db.query(models.CharacterAttribute)
        .filter(
            models.CharacterAttribute.character_id == character_id,
            models.CharacterAttribute.name == attribute_name,
        )
        .first()
    )

    if attribute is None:
        raise ValueError(
            f"Character {character_id} has no attribute named "
            f"'{attribute_name}'."
        )

    return attribute.value


def get_skill_level(
    db: Session,
    character_id: int,
    skill_name: str,
) -> int:
    skill = (
        db.query(models.CharacterSkill)
        .filter(
            models.CharacterSkill.character_id == character_id,
            models.CharacterSkill.name == skill_name,
        )
        .first()
    )

    if skill is None:
        return 0

    return skill.level


def get_check_power(
    db: Session,
    character_id: int,
    attribute_name: str,
    core_skill_name: str,
    specialization_name: str | None = None,
    gear_bonus: int = 0,
    situational_bonus: int = 0,
) -> int:
    character = get_character(
        db=db,
        character_id=character_id,
    )

    attribute = get_attribute_value(
        db=db,
        character_id=character_id,
        attribute_name=attribute_name,
    )

    core_skill = get_skill_level(
        db=db,
        character_id=character_id,
        skill_name=core_skill_name,
    )

    specialization = 0

    if specialization_name is not None:
        specialization = get_skill_level(
            db=db,
            character_id=character_id,
            skill_name=specialization_name,
        )

    return calculate_check_power(
        character_level=character.level,
        attribute=attribute,
        core_skill=core_skill,
        specialization=specialization,
        gear_bonus=gear_bonus,
        situational_bonus=situational_bonus,
    )
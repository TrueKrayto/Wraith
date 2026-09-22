from backend.database import SessionLocal
from backend.services.stats import (
    get_attribute_value,
    get_character,
    get_check_power,
    get_skill_level,
)


db = SessionLocal()

try:
    character_id = 5

    character = get_character(
        db=db,
        character_id=character_id,
    )

    strength = get_attribute_value(
        db=db,
        character_id=character_id,
        attribute_name="strength",
    )

    combat = get_skill_level(
        db=db,
        character_id=character_id,
        skill_name="combat",
    )

    swordsmanship = get_skill_level(
        db=db,
        character_id=character_id,
        skill_name="swordsmanship",
    )

    combat_power = get_check_power(
        db=db,
        character_id=character_id,
        attribute_name="strength",
        core_skill_name="combat",
        specialization_name="swordsmanship",
    )

    print("Level:", character.level)
    print("Strength:", strength)
    print("Combat:", combat)
    print("Swordsmanship:", swordsmanship)
    print("Combat power:", combat_power)

finally:
    db.close()
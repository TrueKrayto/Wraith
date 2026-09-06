from backend.database import SessionLocal
from backend.services.checks import resolve_character_check


db = SessionLocal()

try:
    character_id = 5

    result = resolve_character_check(
        db=db,
        character_id=character_id,
        attribute_name="strength",
        core_skill_name="combat",
        specialization_name="swordsmanship",
        difficulty=60,
    )

    print(result)

finally:
    db.close()
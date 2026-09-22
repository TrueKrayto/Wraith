from backend.database import SessionLocal
from backend.services.combat import resolve_and_apply_attack
from backend.services.resources import get_resource


db = SessionLocal()

try:
    attacker_character_id = 1
    defender_character_id = 5

    health = get_resource(
        db=db,
        character_id=defender_character_id,
        resource_name="health",
    )

    print("Starting defender health:", health.current)

    result = resolve_and_apply_attack(
        db=db,
        attacker_character_id=attacker_character_id,
        defender_character_id=defender_character_id,
        attacker_attribute="strength",
        attacker_core_skill="combat",
        attacker_specialization="swordsmanship",
        defender_attribute="agility",
        defender_core_skill="combat",
        defender_specialization="swordsmanship",
        base_damage=10,
    )

    print("Attack result:", result)
    print("Health after attack:", health.current)

finally:
    # Test only — don't permanently damage character 5.
    db.rollback()
    db.close()
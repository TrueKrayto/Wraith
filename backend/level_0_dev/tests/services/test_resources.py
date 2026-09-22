from backend.database import SessionLocal
from backend.services.resources import (
    get_resource,
    restore_resource,
    spend_resource,
)


db = SessionLocal()

try:
    character_id = 5

    mana = get_resource(
        db=db,
        character_id=character_id,
        resource_name="mana",
    )

    print("Starting mana:", mana.current)

    spend_resource(
        db=db,
        character_id=character_id,
        resource_name="mana",
        amount=25,
    )

    print("After spending 25:", mana.current)

    restore_resource(
        db=db,
        character_id=character_id,
        resource_name="mana",
        amount=10,
    )

    print("After restoring 10:", mana.current)

    try:
        spend_resource(
            db=db,
            character_id=character_id,
            resource_name="mana",
            amount=200,
        )
    except ValueError as error:
        print("Overspend blocked:", error)

finally:
    db.rollback()
    db.close()
from backend import models
from backend.database import SessionLocal
from backend.entities.characters.attributes import default_attributes
from backend.entities.characters.resources import default_resources
from backend.entities.characters.skills import default_skills


db = SessionLocal()

try:
    characters = db.query(models.Character).all()

    for character in characters:
        existing_skills = {
            skill.name
            for skill in (
                db.query(models.CharacterSkill)
                .filter(
                    models.CharacterSkill.character_id == character.id
                )
                .all()
            )
        }

        existing_attributes = {
            attribute.name
            for attribute in (
                db.query(models.CharacterAttribute)
                .filter(
                    models.CharacterAttribute.character_id == character.id
                )
                .all()
            )
        }

        existing_resources = {
            resource.name
            for resource in (
                db.query(models.CharacterResource)
                .filter(
                    models.CharacterResource.character_id == character.id
                )
                .all()
            )
        }

        for name, level in default_skills().items():
            if name not in existing_skills:
                db.add(
                    models.CharacterSkill(
                        character_id=character.id,
                        name=name,
                        level=level,
                    )
                )

        for name, value in default_attributes().items():
            if name not in existing_attributes:
                db.add(
                    models.CharacterAttribute(
                        character_id=character.id,
                        name=name,
                        value=value,
                    )
                )

        for name, values in default_resources().items():
            if name not in existing_resources:
                db.add(
                    models.CharacterResource(
                        character_id=character.id,
                        name=name,
                        current=values["current"],
                        maximum=values["maximum"],
                    )
                )

        print(f"Checked character {character.id}: {character.name}")

    db.commit()
    print("Backfill complete.")

finally:
    db.close()
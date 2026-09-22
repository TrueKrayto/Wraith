from backend.level_4_systems.data import (
    SessionLocal,
    Character,
    CharacterSkill,
    CharacterAttribute,
    CharacterResource,
)

from backend.level_5_entities.characters import (
    default_attributes,
    default_resources,
    default_skills,
)


db = SessionLocal()

try:
    characters = db.query(Character).all()

    for character in characters:
        existing_skills = {
            skill.name
            for skill in (
                db.query(CharacterSkill)
                .filter(
                    CharacterSkill.character_id == character.id
                )
                .all()
            )
        }

        existing_attributes = {
            attribute.name
            for attribute in (
                db.query(CharacterAttribute)
                .filter(
                    CharacterAttribute.character_id == character.id
                )
                .all()
            )
        }

        existing_resources = {
            resource.name
            for resource in (
                db.query(CharacterResource)
                .filter(
                    CharacterResource.character_id == character.id
                )
                .all()
            )
        }

        for name, level in default_skills().items():
            if name not in existing_skills:
                db.add(
                    CharacterSkill(
                        character_id=character.id,
                        name=name,
                        level=level,
                    )
                )

        for name, value in default_attributes().items():
            if name not in existing_attributes:
                db.add(
                    CharacterAttribute(
                        character_id=character.id,
                        name=name,
                        value=value,
                    )
                )

        for name, values in default_resources().items():
            if name not in existing_resources:
                db.add(
                    CharacterResource(
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
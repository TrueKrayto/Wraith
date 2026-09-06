from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend import models, schemas
from backend.database import get_db
from backend.game.attributes import default_attributes
from backend.game.levels import clamp_level
from backend.game.resources import default_resources
from backend.game.skills import default_skills


router = APIRouter(
    prefix="/characters",
    tags=["characters"],
)


@router.post("", response_model=schemas.CharacterRead)
def create_character(
    character: schemas.CharacterCreate,
    db: Session = Depends(get_db),
):
    level = clamp_level(character.level)

    new_character = models.Character(
        name=character.name,
        role=character.role,
        level=level,
    )

    db.add(new_character)

    # Assign an ID before creating related rows.
    db.flush()

    for name, skill_level in default_skills().items():
        db.add(
            models.CharacterSkill(
                character_id=new_character.id,
                name=name,
                level=skill_level,
            )
        )

    for name, value in default_attributes().items():
        db.add(
            models.CharacterAttribute(
                character_id=new_character.id,
                name=name,
                value=value,
            )
        )

    for name, values in default_resources().items():
        db.add(
            models.CharacterResource(
                character_id=new_character.id,
                name=name,
                current=values["current"],
                maximum=values["maximum"],
            )
        )

    db.commit()
    db.refresh(new_character)

    return new_character


@router.get("", response_model=list[schemas.CharacterRead])
def get_characters(
    db: Session = Depends(get_db),
):
    return db.query(models.Character).all()
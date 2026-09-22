from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend import models, schemas
from backend.database import get_db
from backend.entities.characters.attributes import default_attributes
from backend.entities.characters.levels import clamp_level
from backend.entities.characters.resources import default_resources
from backend.entities.characters.skills import default_skills


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


@router.patch("/{character_id}", response_model=schemas.CharacterRead)
def update_character(
    character_id: int,
    character_update: schemas.CharacterUpdate,
    db: Session = Depends(get_db),
):
    character = (
        db.query(models.Character)
        .filter(models.Character.id == character_id)
        .first()
    )

    if character is None:
        raise HTTPException(
            status_code=404,
            detail="Character not found",
        )

    if character_update.name is not None:
        character.name = character_update.name

    if character_update.role is not None:
        character.role = character_update.role

    db.commit()
    db.refresh(character)

    return character
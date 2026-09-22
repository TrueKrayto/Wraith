from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.level_4_systems.data import (
    Character,
    CharacterAttribute,
    CharacterResource,
    CharacterSkill,
    get_db,
)
from backend.level_5_entities.characters import (
    clamp_level,
    default_attributes,
    default_resources,
    default_skills,
    schemas,
)


router = APIRouter(
    prefix="/characters",
    tags=["characters"],
)


@router.post(
    "",
    response_model=schemas.CharacterRead,
)
def create_character(
    character: schemas.CharacterCreate,
    db: Session = Depends(get_db),
):
    level = clamp_level(
        character.level
    )

    new_character = Character(
        name=character.name,
        role=character.role,
        level=level,
    )

    db.add(new_character)
    db.flush()

    for name, skill_level in default_skills().items():
        db.add(
            CharacterSkill(
                character_id=new_character.id,
                name=name,
                level=skill_level,
            )
        )

    for name, value in default_attributes().items():
        db.add(
            CharacterAttribute(
                character_id=new_character.id,
                name=name,
                value=value,
            )
        )

    for name, values in default_resources().items():
        db.add(
            CharacterResource(
                character_id=new_character.id,
                name=name,
                current=values["current"],
                maximum=values["maximum"],
            )
        )

    db.commit()
    db.refresh(new_character)

    return new_character


@router.get(
    "",
    response_model=list[schemas.CharacterRead],
)
def get_characters(
    db: Session = Depends(get_db),
):
    return db.query(
        Character
    ).all()


@router.patch(
    "/{character_id}",
    response_model=schemas.CharacterRead,
)
def update_character(
    character_id: int,
    character_update: schemas.CharacterUpdate,
    db: Session = Depends(get_db),
):
    character = (
        db.query(Character)
        .filter(
            Character.id == character_id
        )
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
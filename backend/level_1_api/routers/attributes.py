from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.level_4_systems.data import (
    Character,
    CharacterAttribute,
    get_db,
)
from backend.level_5_entities.characters import (
    clamp_attribute,
    schemas,
)


router = APIRouter(
    prefix="/characters/{character_id}/attributes",
    tags=["attributes"],
)


@router.post(
    "",
    response_model=schemas.CharacterAttributeRead,
)
def create_attribute(
    character_id: int,
    attribute: schemas.CharacterAttributeCreate,
    db: Session = Depends(get_db),
):
    character = (
        db.query(Character)
        .filter(Character.id == character_id)
        .first()
    )

    if character is None:
        raise HTTPException(
            status_code=404,
            detail="Character not found",
        )

    existing_attribute = (
        db.query(CharacterAttribute)
        .filter(
            CharacterAttribute.character_id == character_id,
            CharacterAttribute.name == attribute.name,
        )
        .first()
    )

    if existing_attribute is not None:
        raise HTTPException(
            status_code=409,
            detail="Character already has this attribute",
        )

    attribute_value = clamp_attribute(
        attribute.value
    )

    new_attribute = CharacterAttribute(
        character_id=character_id,
        name=attribute.name,
        value=attribute_value,
    )

    db.add(new_attribute)
    db.commit()
    db.refresh(new_attribute)

    return new_attribute


@router.get(
    "",
    response_model=list[schemas.CharacterAttributeRead],
)
def get_attributes(
    character_id: int,
    db: Session = Depends(get_db),
):
    return (
        db.query(CharacterAttribute)
        .filter(
            CharacterAttribute.character_id
            == character_id
        )
        .all()
    )


@router.patch(
    "/{attribute_name}",
    response_model=schemas.CharacterAttributeRead,
)
def update_attribute(
    character_id: int,
    attribute_name: str,
    attribute_update: schemas.CharacterAttributeUpdate,
    db: Session = Depends(get_db),
):
    attribute = (
        db.query(CharacterAttribute)
        .filter(
            CharacterAttribute.character_id == character_id,
            CharacterAttribute.name == attribute_name,
        )
        .first()
    )

    if attribute is None:
        raise HTTPException(
            status_code=404,
            detail="Attribute not found",
        )

    attribute.value = clamp_attribute(
        attribute_update.value
    )

    db.commit()
    db.refresh(attribute)

    return attribute
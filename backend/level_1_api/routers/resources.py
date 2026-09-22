from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.level_2_services.game import change_resource
from backend.level_4_systems.data import (
    Character,
    CharacterResource,
    get_db,
)
from backend.level_5_entities.characters import (
    clamp_resource,
    schemas,
)


router = APIRouter(
    prefix="/characters/{character_id}/resources",
    tags=["resources"],
)


@router.post(
    "",
    response_model=schemas.CharacterResourceRead,
)
def create_resource(
    character_id: int,
    resource: schemas.CharacterResourceCreate,
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

    existing_resource = (
        db.query(CharacterResource)
        .filter(
            CharacterResource.character_id == character_id,
            CharacterResource.name == resource.name,
        )
        .first()
    )

    if existing_resource is not None:
        raise HTTPException(
            status_code=409,
            detail="Character already has this resource",
        )

    maximum = max(
        1,
        resource.maximum,
    )

    current = clamp_resource(
        resource.current,
        maximum,
    )

    new_resource = CharacterResource(
        character_id=character_id,
        name=resource.name,
        current=current,
        maximum=maximum,
    )

    db.add(new_resource)
    db.commit()
    db.refresh(new_resource)

    return new_resource


@router.get(
    "",
    response_model=list[schemas.CharacterResourceRead],
)
def get_resources(
    character_id: int,
    db: Session = Depends(get_db),
):
    return (
        db.query(CharacterResource)
        .filter(
            CharacterResource.character_id == character_id
        )
        .all()
    )


@router.patch(
    "/{resource_name}",
    response_model=schemas.CharacterResourceRead,
)
def update_resource(
    character_id: int,
    resource_name: str,
    resource_update: schemas.CharacterResourceUpdate,
    db: Session = Depends(get_db),
):
    resource = (
        db.query(CharacterResource)
        .filter(
            CharacterResource.character_id == character_id,
            CharacterResource.name == resource_name,
        )
        .first()
    )

    if resource is None:
        raise HTTPException(
            status_code=404,
            detail="Resource not found",
        )

    amount = (
        resource_update.current
        - resource.current
    )

    resource = change_resource(
        db=db,
        character_id=character_id,
        resource_name=resource_name,
        amount=amount,
    )

    db.commit()
    db.refresh(resource)

    return resource
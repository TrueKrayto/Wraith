from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend import models, schemas
from backend.database import get_db
from backend.game.resources import clamp_resource
from backend.services.resources import change_resource


router = APIRouter(
    prefix="/characters/{character_id}/resources",
    tags=["resources"],
)


@router.post("", response_model=schemas.CharacterResourceRead)
def create_resource(
    character_id: int,
    resource: schemas.CharacterResourceCreate,
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

    existing_resource = (
        db.query(models.CharacterResource)
        .filter(
            models.CharacterResource.character_id == character_id,
            models.CharacterResource.name == resource.name,
        )
        .first()
    )

    if existing_resource is not None:
        raise HTTPException(
            status_code=409,
            detail="Character already has this resource",
        )

    maximum = max(1, resource.maximum)
    current = clamp_resource(
        resource.current,
        maximum,
    )

    new_resource = models.CharacterResource(
        character_id=character_id,
        name=resource.name,
        current=current,
        maximum=maximum,
    )

    db.add(new_resource)
    db.commit()
    db.refresh(new_resource)

    return new_resource


@router.get("", response_model=list[schemas.CharacterResourceRead])
def get_resources(
    character_id: int,
    db: Session = Depends(get_db),
):
    return (
        db.query(models.CharacterResource)
        .filter(models.CharacterResource.character_id == character_id)
        .all()
    )


@router.patch("/{resource_name}", response_model=schemas.CharacterResourceRead)
def update_resource(
    character_id: int,
    resource_name: str,
    resource_update: schemas.CharacterResourceUpdate,
    db: Session = Depends(get_db),
):
    resource = (
        db.query(models.CharacterResource)
        .filter(
            models.CharacterResource.character_id == character_id,
            models.CharacterResource.name == resource_name,
        )
        .first()
    )

    if resource is None:
        raise HTTPException(
            status_code=404,
            detail="Resource not found",
        )

    amount = resource_update.current - resource.current

    resource = change_resource(
        db=db,
        character_id=character_id,
        resource_name=resource_name,
        amount=amount,
    )

    db.commit()
    db.refresh(resource)

    return resource
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend import models, schemas
from backend.database import get_db


router = APIRouter(
    prefix="/characters",
    tags=["characters"],
)


@router.post("", response_model=schemas.CharacterRead)
def create_character(
    character: schemas.CharacterCreate,
    db: Session = Depends(get_db),
):
    new_character = models.Character(
        name=character.name,
        role=character.role,
        level=character.level,
    )

    db.add(new_character)
    db.commit()
    db.refresh(new_character)

    return new_character


@router.get("", response_model=list[schemas.CharacterRead])
def get_characters(
    db: Session = Depends(get_db),
):
    return db.query(models.Character).all()
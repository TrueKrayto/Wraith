from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend import models, schemas
from backend.database import get_db
from backend.game.skills import clamp_skill


router = APIRouter(
    prefix="/characters/{character_id}/skills",
    tags=["skills"],
)


@router.post("", response_model=schemas.CharacterSkillRead)
def create_skill(
    character_id: int,
    skill: schemas.CharacterSkillCreate,
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

    existing_skill = (
        db.query(models.CharacterSkill)
        .filter(
            models.CharacterSkill.character_id == character_id,
            models.CharacterSkill.name == skill.name,
        )
        .first()
    )

    if existing_skill is not None:
        raise HTTPException(
            status_code=409,
            detail="Character already has this skill",
        )

    skill_level = clamp_skill(
        skill_level=skill.level,
        character_level=character.level,
    )

    new_skill = models.CharacterSkill(
        character_id=character_id,
        name=skill.name,
        level=skill_level,
    )

    db.add(new_skill)
    db.commit()
    db.refresh(new_skill)

    return new_skill


@router.get("", response_model=list[schemas.CharacterSkillRead])
def get_skills(
    character_id: int,
    db: Session = Depends(get_db),
):
    return (
        db.query(models.CharacterSkill)
        .filter(models.CharacterSkill.character_id == character_id)
        .all()
    )


@router.patch("/{skill_name}", response_model=schemas.CharacterSkillRead)
def update_skill(
    character_id: int,
    skill_name: str,
    skill_update: schemas.CharacterSkillUpdate,
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

    skill = (
        db.query(models.CharacterSkill)
        .filter(
            models.CharacterSkill.character_id == character_id,
            models.CharacterSkill.name == skill_name,
        )
        .first()
    )

    if skill is None:
        raise HTTPException(
            status_code=404,
            detail="Skill not found",
        )

    skill.level = clamp_skill(
        skill_level=skill_update.level,
        character_level=character.level,
    )

    db.commit()
    db.refresh(skill)

    return skill
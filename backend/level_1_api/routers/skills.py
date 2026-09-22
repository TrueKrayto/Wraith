from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.level_4_systems.data import (
    Character,
    CharacterSkill,
    get_db,
)
from backend.level_5_entities.characters import (
    clamp_skill,
    schemas,
)


router = APIRouter(
    prefix="/characters/{character_id}/skills",
    tags=["skills"],
)


@router.post(
    "",
    response_model=schemas.CharacterSkillRead,
)
def create_skill(
    character_id: int,
    skill: schemas.CharacterSkillCreate,
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

    existing_skill = (
        db.query(CharacterSkill)
        .filter(
            CharacterSkill.character_id == character_id,
            CharacterSkill.name == skill.name,
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

    new_skill = CharacterSkill(
        character_id=character_id,
        name=skill.name,
        level=skill_level,
    )

    db.add(new_skill)
    db.commit()
    db.refresh(new_skill)

    return new_skill


@router.get(
    "",
    response_model=list[schemas.CharacterSkillRead],
)
def get_skills(
    character_id: int,
    db: Session = Depends(get_db),
):
    return (
        db.query(CharacterSkill)
        .filter(
            CharacterSkill.character_id == character_id
        )
        .all()
    )


@router.patch(
    "/{skill_name}",
    response_model=schemas.CharacterSkillRead,
)
def update_skill(
    character_id: int,
    skill_name: str,
    skill_update: schemas.CharacterSkillUpdate,
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

    skill = (
        db.query(CharacterSkill)
        .filter(
            CharacterSkill.character_id == character_id,
            CharacterSkill.name == skill_name,
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
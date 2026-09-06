from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend import schemas
from backend.database import get_db
from backend.services.checks import (
    resolve_character_check,
    resolve_opposed_character_check,
)


router = APIRouter(
    prefix="/checks",
    tags=["checks"],
)


@router.post("/character")
def character_check(
    check_request: schemas.CharacterCheckRequest,
    db: Session = Depends(get_db),
):
    try:
        result = resolve_character_check(
            db=db,
            character_id=check_request.character_id,
            attribute_name=check_request.attribute_name,
            core_skill_name=check_request.core_skill_name,
            specialization_name=check_request.specialization_name,
            difficulty=check_request.difficulty,
            gear_bonus=check_request.gear_bonus,
            situational_bonus=check_request.situational_bonus,
            resource_name=check_request.resource_name,
            resource_cost=check_request.resource_cost,
        )

        db.commit()

        return result

    except ValueError as error:
        db.rollback()

        raise HTTPException(
            status_code=400,
            detail=str(error),
        )


@router.post("/opposed")
def opposed_character_check(
    check_request: schemas.OpposedCharacterCheckRequest,
    db: Session = Depends(get_db),
):
    try:
        return resolve_opposed_character_check(
            db=db,
            attacker_character_id=check_request.attacker_character_id,
            defender_character_id=check_request.defender_character_id,
            attacker_attribute=check_request.attacker_attribute,
            attacker_core_skill=check_request.attacker_core_skill,
            attacker_specialization=check_request.attacker_specialization,
            defender_attribute=check_request.defender_attribute,
            defender_core_skill=check_request.defender_core_skill,
            defender_specialization=check_request.defender_specialization,
            attacker_gear_bonus=check_request.attacker_gear_bonus,
            defender_gear_bonus=check_request.defender_gear_bonus,
            attacker_situational_bonus=check_request.attacker_situational_bonus,
            defender_situational_bonus=check_request.defender_situational_bonus,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )
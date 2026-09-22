from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend import schemas
from backend.level_2_services.game import resolve_and_apply_attack
from backend.level_4_systems.data import get_db


router = APIRouter(
    prefix="/combat",
    tags=["combat"],
)


@router.post("/attack")
def attack(
    attack_request: schemas.AttackRequest,
    db: Session = Depends(get_db),
):
    try:
        result = resolve_and_apply_attack(
            db=db,
            attacker_character_id=attack_request.attacker_character_id,
            defender_character_id=attack_request.defender_character_id,
            attacker_attribute=attack_request.attacker_attribute,
            attacker_core_skill=attack_request.attacker_core_skill,
            attacker_specialization=attack_request.attacker_specialization,
            defender_attribute=attack_request.defender_attribute,
            defender_core_skill=attack_request.defender_core_skill,
            defender_specialization=attack_request.defender_specialization,
            base_damage=attack_request.base_damage,
            power_multiplier=attack_request.power_multiplier,
            gear_bonus=attack_request.gear_bonus,
            resource_name=attack_request.resource_name,
            resource_cost=attack_request.resource_cost,
        )

        db.commit()

        return result

    except ValueError as error:
        db.rollback()

        raise HTTPException(
            status_code=400,
            detail=str(error),
        )
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.level_2_services.game import (
    execute_action,
    validate_action_proposal,
)

from backend.level_4_systems.data import get_db
from backend.level_4_systems.llm.game import ActionProposal


router = APIRouter(
    prefix="/actions",
    tags=["actions"],
)


@router.post("/validate", response_model=ActionProposal)
def validate_action(
    proposal: ActionProposal,
):
    try:
        return validate_action_proposal(proposal)

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )


@router.post("/execute")
def execute_proposed_action(
    proposal: ActionProposal,
    db: Session = Depends(get_db),
):
    try:
        result = execute_action(
            db=db,
            proposal=proposal,
        )

        db.commit()

        return result

    except ValueError as error:
        db.rollback()

        raise HTTPException(
            status_code=400,
            detail=str(error),
        )
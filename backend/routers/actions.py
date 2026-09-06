from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend import schemas
from backend.database import get_db
from backend.services.action_executor import execute_action
from backend.services.actions import validate_action_proposal


router = APIRouter(
    prefix="/actions",
    tags=["actions"],
)


@router.post("/validate", response_model=schemas.ActionProposal)
def validate_action(
    proposal: schemas.ActionProposal,
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
    proposal: schemas.ActionProposal,
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
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend import schemas
from backend.database import get_db
from backend.llm.interpreter import interpret_player_action
from backend.llm.narrator import narrate_action
from backend.services.action_executor import execute_action


router = APIRouter(
    prefix="/play",
    tags=["play"],
)


@router.post("")
def play_action(
    request: schemas.PlayerActionRequest,
    db: Session = Depends(get_db),
):
    try:
        proposal = interpret_player_action(
            db=db,
            request=request,
        )

        result = execute_action(
            db=db,
            proposal=proposal,
        )

        db.commit()

        narration = narrate_action(
            player_action=request.action_text,
            proposal=proposal,
            result=result,
        )

        return {
            "narration": narration,
            "proposal": proposal,
            "result": result,
        }

    except Exception as error:
        db.rollback()

        raise HTTPException(
            status_code=400,
            detail=str(error),
        )
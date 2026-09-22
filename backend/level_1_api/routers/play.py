from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend import schemas
from backend.database import get_db
from backend.llm.interpreter import interpret_player_action
from backend.llm.narrator import narrate_action
from backend.llm.npc_agent import decide_npc_action
from backend.services.action_executor import execute_action


router = APIRouter(
    prefix="/play",
    tags=["play"],
)


def get_responding_npc_id(
    proposal: schemas.ActionProposal,
) -> int | None:
    actor_id = proposal.actor_character_id

    if (
        proposal.target_character_id is not None
        and proposal.target_character_id != actor_id
    ):
        return proposal.target_character_id

    for check in proposal.checks:
        if (
            check.target_character_id is not None
            and check.target_character_id != actor_id
        ):
            return check.target_character_id

    return None


@router.post("")
def play_action(
    request: schemas.PlayerActionRequest,
    db: Session = Depends(get_db),
):
    try:
        # ---------------------------------
        # Player action
        # ---------------------------------

        player_proposal = interpret_player_action(
            db=db,
            request=request,
        )

        player_result = execute_action(
            db=db,
            proposal=player_proposal,
        )

        # ---------------------------------
        # NPC response
        # ---------------------------------

        npc_proposal = None
        npc_result = None

        responding_npc_id = get_responding_npc_id(
            player_proposal
        )

        if responding_npc_id is not None:
            npc_proposal = decide_npc_action(
                db=db,
                npc_character_id=responding_npc_id,
                player_action=request.action_text,
                player_result=player_result,
            )

            npc_result = execute_action(
                db=db,
                proposal=npc_proposal,
            )

        # ---------------------------------
        # Persist resolved mechanics
        # ---------------------------------

        db.commit()

        # ---------------------------------
        # Narrate complete exchange
        # ---------------------------------

        narration = narrate_action(
            player_action=request.action_text,
            proposal=player_proposal,
            result=player_result,
            npc_proposal=npc_proposal,
            npc_result=npc_result,
        )

        return {
            "narration": narration,
            "proposal": player_proposal,
            "result": player_result,
            "npc_proposal": npc_proposal,
            "npc_result": npc_result,
        }

    except Exception as error:
        db.rollback()

        raise HTTPException(
            status_code=400,
            detail=str(error),
        )
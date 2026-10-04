from dataclasses import asdict

from fastapi import APIRouter, HTTPException

from backend.level_2_services.npc import (
    create_npc_from_prompt,
    mutate_npc_from_prompt,
)
from backend.level_5_entities.characters import schemas


router = APIRouter(
    prefix="/npc",
    tags=["npc"],
)


@router.post("/create")
def create_npc_route(
    request: schemas.NPCCreateRequest,
):
    try:
        npc = create_npc_from_prompt(
            request.prompt
        )

        return asdict(npc)

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error),
        )


@router.post("/mutate")
def mutate_npc_route(
    request: schemas.NPCMutationRequest,
):
    try:
        npc = mutate_npc_from_prompt(
            request.prompt
        )

        if npc is None:
            raise HTTPException(
                status_code=404,
                detail="NPC not found.",
            )

        return asdict(npc)

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error),
        )
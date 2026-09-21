from dataclasses import asdict

from fastapi import APIRouter, HTTPException

from backend.entities.characters import schemas
from backend.llm.npc_creator import generate_npc


router = APIRouter(
    prefix="/npc",
    tags=["npc"],
)


@router.post("/create")
def create_npc_from_prompt(
    request: schemas.NPCCreateRequest,
):
    try:
        npc = generate_npc(request.prompt)

        return asdict(npc)

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error),
        )
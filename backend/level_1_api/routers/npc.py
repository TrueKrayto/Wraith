from dataclasses import asdict

from fastapi import APIRouter, HTTPException

from backend.entities.characters import (
    apply_npc_mutation,
    schemas,
)
from backend.entities.characters.temp_store import (
    load_npcs,
    save_npcs,
)
from backend.llm.npc_creator import generate_npc
from backend.llm.temp_npc_mutator import generate_npc_mutation


router = APIRouter(
    prefix="/npc",
    tags=["npc"],
)


@router.post("/create")
def create_npc_from_prompt(
    request: schemas.NPCCreateRequest,
):
    try:
        npc = generate_npc(
            request.prompt,
        )

        return asdict(npc)

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error),
        )


@router.post("/mutate")
def mutate_npc_from_prompt(
    request: schemas.NPCMutationRequest,
):
    try:
        # LLM interprets the natural-language instruction.
        mutation = generate_npc_mutation(
            request.prompt,
        )

        # TEMPORARY:
        # Load NPCs from JSON store.
        npcs = load_npcs()

        npc = npcs.get(
            mutation.npc_id
        )

        if npc is None:
            raise HTTPException(
                status_code=404,
                detail="NPC not found.",
            )

        # Apply the structured mutation.
        apply_npc_mutation(
            npc=npc,
            mutation=mutation,
        )

        # TEMPORARY:
        # Persist updated NPC state.
        save_npcs(npcs)

        return asdict(npc)

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error),
        )
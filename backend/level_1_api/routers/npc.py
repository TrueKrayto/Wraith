from dataclasses import asdict

from fastapi import APIRouter, HTTPException

from backend.level_4_systems.data import get_npc_repository
from backend.level_4_systems.llm.clients import (
    get_llm_client,
    get_llm_model,
)
from backend.level_4_systems.llm.npc import (
    generate_npc_data,
    generate_npc_mutation,
)
from backend.level_5_entities.characters import (
    apply_npc_mutation,
    create_npc,
    schemas,
)


router = APIRouter(
    prefix="/npc",
    tags=["npc"],
)


@router.post("/create")
def create_npc_from_prompt(
    request: schemas.NPCCreateRequest,
):
    try:
        client = get_llm_client()
        model = get_llm_model()

        # LLM produces structured creation data.
        payload = generate_npc_data(
            client=client,
            model=model,
            npc_prompt=request.prompt,
        )

        # Character system constructs the actual NPC.
        npc = create_npc(
            payload=payload,
        )

        # Persist through the repository abstraction.
        repository = get_npc_repository()
        repository.save(npc)

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
        client = get_llm_client()
        model = get_llm_model()

        repository = get_npc_repository()

        # Supply existing NPC state to the LLM interpreter.
        npcs = repository.get_all()

        mutation = generate_npc_mutation(
            client=client,
            model=model,
            mutation_prompt=request.prompt,
            npcs=npcs,
        )

        npc = repository.get(
            mutation.npc_id
        )

        if npc is None:
            raise HTTPException(
                status_code=404,
                detail="NPC not found.",
            )

        # Character system applies the validated mutation.
        apply_npc_mutation(
            npc=npc,
            mutation=mutation,
        )

        repository.save(npc)

        return asdict(npc)

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error),
        )
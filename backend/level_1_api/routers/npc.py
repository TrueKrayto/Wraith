from dataclasses import asdict

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
)

from backend.level_2_workers import WorkerManager
from backend.level_3_services import (
    create_npc_from_prompt,
    enrich_npc,
    mutate_npc_from_prompt,
)
from backend.level_5_entities.characters import schemas


router = APIRouter(
    prefix="/npc",
    tags=["npc"],
)


# ------------------------------------------------------------------
# DEPENDENCIES
# ------------------------------------------------------------------

def get_worker_manager(
    request: Request,
) -> WorkerManager:
    return request.app.state.worker_manager


# ------------------------------------------------------------------
# CREATION
# ------------------------------------------------------------------

@router.post("/create")
def create_npc_route(
    request: schemas.NPCCreateRequest,
    worker_manager: WorkerManager = Depends(
        get_worker_manager
    ),
):
    try:
        npc = create_npc_from_prompt(
            request.prompt
        )

        worker_manager.enqueue_npc_enrichment(
            npc.npc_id
        )

        return asdict(npc)

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error),
        )


# ------------------------------------------------------------------
# MUTATION
# ------------------------------------------------------------------

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


# ------------------------------------------------------------------
# DIRECT ENRICHMENT
#
# Forced/testing path.
# Bypasses the worker and performs enrichment immediately.
# ------------------------------------------------------------------

@router.post("/enrich/{npc_id}")
def enrich_npc_route(
    npc_id: str,
):
    try:
        npc = enrich_npc(
            npc_id
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


# ------------------------------------------------------------------
# QUEUE ONE NPC FOR ENRICHMENT
# ------------------------------------------------------------------

@router.post("/enrichment/queue/{npc_id}")
def queue_npc_enrichment_route(
    npc_id: str,
    worker_manager: WorkerManager = Depends(
        get_worker_manager
    ),
):
    try:
        worker_manager.enqueue_npc_enrichment(
            npc_id
        )

        return {
            "status": "queued",
            "npc_id": npc_id,
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error),
        )


# ------------------------------------------------------------------
# QUEUE ALL UNENRICHED NPCS
# ------------------------------------------------------------------

@router.post("/enrichment/queue-pending")
def queue_pending_npc_enrichment_route(
    worker_manager: WorkerManager = Depends(
        get_worker_manager
    ),
):
    try:
        queued = (
            worker_manager
            .enqueue_pending_npc_enrichment()
        )

        return {
            "status": "queued",
            "jobs_queued": queued,
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error),
        )
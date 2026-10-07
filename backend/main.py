from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.level_1_api import npc_router
from backend.level_2_workers import WorkerManager


@asynccontextmanager
async def lifespan(app: FastAPI):
    worker_manager = WorkerManager()

    app.state.worker_manager = worker_manager

    worker_manager.start()

    try:
        yield

    finally:
        worker_manager.stop()


app = FastAPI(
    title="Wraith API",
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(npc_router)


@app.get("/health")
def health():
    return {
        "status": "ok",
    }
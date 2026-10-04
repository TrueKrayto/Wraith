from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.level_1_api import npc_router


app = FastAPI(
    title="Wraith API",
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
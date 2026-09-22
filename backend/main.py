from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.level_1_api import (
    actions_router,
    attributes_router,
    characters_router,
    checks_router,
    combat_router,
    npc_router,
    play_router,
    resources_router,
    skills_router,
)


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(characters_router)
app.include_router(skills_router)
app.include_router(attributes_router)
app.include_router(resources_router)
app.include_router(combat_router)
app.include_router(checks_router)
app.include_router(actions_router)
app.include_router(play_router)
app.include_router(npc_router)


@app.get("/health")
def health():
    return {
        "status": "ok",
    }
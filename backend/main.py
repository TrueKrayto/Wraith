from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routers.actions import router as actions_router
from backend.routers.attributes import router as attributes_router
from backend.routers.characters import router as characters_router
from backend.routers.checks import router as checks_router
from backend.routers.combat import router as combat_router
from backend.routers.play import router as play_router
from backend.routers.resources import router as resources_router
from backend.routers.skills import router as skills_router


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


@app.get("/health")
def health():
    return {"status": "ok"}
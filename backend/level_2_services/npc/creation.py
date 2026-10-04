from backend.level_4_systems.data import get_npc_repository
from backend.level_4_systems.llm.clients import (
    get_llm_client,
    get_llm_model,
)
from backend.level_4_systems.llm.npc import generate_npc_data
from backend.level_5_entities.characters import create_npc


def create_npc_from_prompt(prompt: str):
    client = get_llm_client()
    model = get_llm_model()

    payload = generate_npc_data(
        client=client,
        model=model,
        npc_prompt=prompt,
    )

    npc = create_npc(payload=payload)

    repository = get_npc_repository()
    repository.save(npc)

    return npc
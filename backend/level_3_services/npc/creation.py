from backend.level_4_systems import (
    LLMRole,
    generate_npc_data,
    get_llm_client_manager,
    get_npc_repository,
)
from backend.level_5_entities.characters import create_npc


def create_npc_from_prompt(prompt: str):
    llm_manager = get_llm_client_manager()

    creation_llm = llm_manager.get(
        LLMRole.NPC_CREATION
    )

    payload = generate_npc_data(
        client=creation_llm.client,
        model=creation_llm.model,
        npc_prompt=prompt,
    )

    npc = create_npc(
        payload=payload
    )

    repository = get_npc_repository()
    repository.save(npc)

    return npc
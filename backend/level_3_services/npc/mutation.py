from backend.level_4_systems.data import get_npc_repository
from backend.level_4_systems.llm.clients import (
    get_llm_client,
    get_llm_model,
)
from backend.level_4_systems.llm.npc import generate_npc_mutation
from backend.level_5_entities.characters import apply_npc_mutation


def mutate_npc_from_prompt(prompt: str):
    client = get_llm_client()
    model = get_llm_model()

    repository = get_npc_repository()

    # Supply existing NPC state to the LLM interpreter.
    npcs = repository.get_all()

    mutation = generate_npc_mutation(
        client=client,
        model=model,
        mutation_prompt=prompt,
        npcs=npcs,
    )

    npc = repository.get(mutation.npc_id)

    if npc is None:
        return None

    apply_npc_mutation(
        npc=npc,
        mutation=mutation,
    )

    repository.save(npc)

    return npc
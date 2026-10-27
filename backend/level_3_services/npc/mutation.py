from backend.level_4_systems import (
    LLMRole,
    generate_npc_mutation,
    get_llm_client_manager,
    get_npc_repository,
)

from backend.level_5_entities import (
    apply_npc_mutation,
)


def mutate_npc_from_prompt(
    prompt: str,
    npc_id: str | None = None,
):
    """
    Interpret and persist an NPC mutation.

    When npc_id is supplied, only that NPC is provided
    to the LLM mutation interpreter.

    Without npc_id, retain the existing name-based
    selection behaviour for compatibility.
    """

    repository = get_npc_repository()

    # --------------------------------------------------------------
    # TARGET SELECTION
    # --------------------------------------------------------------

    if npc_id is not None:

        npc = repository.get(npc_id)

        if npc is None:
            return None

        npcs = [npc]

    else:

        # Legacy name-based selection.
        # Later we can replace this with a lightweight
        # NPC lookup before invoking the mutation model.

        npcs = repository.get_all()

    # --------------------------------------------------------------
    # LLM ROUTING
    # --------------------------------------------------------------

    llm_manager = get_llm_client_manager()

    mutation_llm = llm_manager.get(
        LLMRole.NPC_MUTATION
    )

    # --------------------------------------------------------------
    # MUTATION GENERATION
    # --------------------------------------------------------------

    mutation = generate_npc_mutation(
        client=mutation_llm.client,
        model=mutation_llm.model,
        mutation_prompt=prompt,
        npcs=npcs,
    )

    # --------------------------------------------------------------
    # LOAD TARGET NPC
    # --------------------------------------------------------------

    npc = repository.get(
        mutation.npc_id
    )

    if npc is None:
        return None

    # --------------------------------------------------------------
    # APPLY + SAVE
    # --------------------------------------------------------------

    apply_npc_mutation(
        npc=npc,
        mutation=mutation,
    )

    repository.save(npc)

    return npc
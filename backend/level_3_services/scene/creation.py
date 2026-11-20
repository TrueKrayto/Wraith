from backend.level_4_systems import (
    LLMRole,
    SceneManager,
    generate_action_proposal,
    get_llm_client_manager,
    get_location_repository,
    get_npc_repository,
)


def create_scene_manager() -> SceneManager:
    """
    Create a configured SceneManager.

    Level 3 connects the Level 4 systems without
    requiring them to import one another.

    The SceneManager receives:
    - Action proposer
    - Location repository
    - NPC repository

    The Action Proposer's LLM is selected by role.
    """

    # --------------------------------------------------------------
    # SHARED LLM MANAGER
    # --------------------------------------------------------------

    llm_manager = get_llm_client_manager()

    # --------------------------------------------------------------
    # CONFIGURED ACTION PROPOSER
    # --------------------------------------------------------------

    def action_proposer(
        *,
        player_input,
        location,
        npcs,
    ):
        """
        Generate an action proposal using the model
        currently assigned to ACTION_PROPOSAL.
        """

        selection = llm_manager.get(
            LLMRole.ACTION_PROPOSAL
        )

        return generate_action_proposal(
            client=selection.client,
            model=selection.model,
            player_input=player_input,
            location=location,
            npcs=npcs,
        )

    # --------------------------------------------------------------
    # CREATE SCENE MANAGER
    # --------------------------------------------------------------

    return SceneManager(
        action_proposer=action_proposer,
        location_repository=get_location_repository(),
        npc_repository=get_npc_repository(),
    )
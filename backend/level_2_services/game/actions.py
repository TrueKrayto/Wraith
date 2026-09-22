from backend.level_4_systems.llm.game import ActionProposal


CALLED_SHOT_DIFFICULTY_BONUS = 10


def validate_action_proposal(
    proposal: ActionProposal,
) -> ActionProposal:
    """
    Validate the mechanical pieces of a freeform action proposal.

    Validation does not apply resolution modifiers. Those belong
    to the executor so validating the same proposal more than once
    does not change it.
    """

    proposal.resource_cost = max(
        0,
        proposal.resource_cost,
    )

    check_ids = [
        check.check_id
        for check in proposal.checks
    ]

    if len(check_ids) != len(set(check_ids)):
        raise ValueError(
            "Each action check must have a unique check_id."
        )

    seen_check_ids: set[str] = set()

    for check in proposal.checks:
        check.proposed_base_damage = max(
            0,
            check.proposed_base_damage,
        )

        if check.difficulty is not None:
            check.difficulty = max(
                0,
                check.difficulty,
            )

        if check.called_shot and check.target_area is None:
            raise ValueError(
                "Called shots require a target area."
            )

        for required_check_id in check.requires_success_of:
            if required_check_id not in seen_check_ids:
                raise ValueError(
                    f"Check '{check.check_id}' can only depend on "
                    f"an earlier check. Unknown or forward dependency: "
                    f"'{required_check_id}'."
                )

        seen_check_ids.add(check.check_id)

    for effect in proposal.ongoing_effects:
        if effect.duration_turns is not None:
            effect.duration_turns = max(
                1,
                effect.duration_turns,
            )

        effect.tick_interval = max(
            1,
            effect.tick_interval,
        )

    return proposal
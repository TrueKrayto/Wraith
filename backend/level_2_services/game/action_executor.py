from sqlalchemy.orm import Session

from backend.level_4_systems.game import calculate_damage
from backend.level_4_systems.llm.game import ActionProposal

from .actions import (
    CALLED_SHOT_DIFFICULTY_BONUS,
    validate_action_proposal,
)
from .checks import (
    resolve_character_check,
    resolve_opposed_character_check,
)
from .resources import (
    change_resource,
    get_resource,
    spend_resource,
)
from .stats import (
    get_character,
    get_skill_level,
)


def execute_action(
    db: Session,
    proposal: ActionProposal,
) -> dict:
    """
    Validate and execute a structured freeform action proposal.

    Checks are resolved in order. A check is skipped when one of
    its required earlier checks failed.
    """

    proposal = validate_action_proposal(proposal)

    actor = get_character(
        db=db,
        character_id=proposal.actor_character_id,
    )

    resource_remaining = None

    if proposal.resource_name is not None and proposal.resource_cost > 0:
        resource = spend_resource(
            db=db,
            character_id=proposal.actor_character_id,
            resource_name=proposal.resource_name,
            amount=proposal.resource_cost,
        )

        resource_remaining = resource.current

    results_by_id: dict[str, dict] = {}
    check_results: list[dict] = []

    for check in proposal.checks:
        target = None

        if check.target_character_id is not None:
            target = get_character(
                db=db,
                character_id=check.target_character_id,
            )

        dependencies_succeeded = all(
            results_by_id[required_id]["success"]
            for required_id in check.requires_success_of
        )

        if not dependencies_succeeded:
            result = {
                "check_id": check.check_id,
                "description": check.description,
                "skipped": True,
                "success": False,
                "reason": "Required earlier check failed.",
                "damage": 0,
                "resource_effects": [],
            }

            if target is not None:
                result["target_character_id"] = target.id
                result["target_name"] = target.name
                result["target_role"] = target.role

            results_by_id[check.check_id] = result
            check_results.append(result)

            continue

        is_opposed = (
            check.target_character_id is not None
            and check.target_attribute_name is not None
            and check.target_core_skill_name is not None
        )

        if is_opposed:
            defender_situational_bonus = 0

            if check.called_shot:
                defender_situational_bonus += (
                    CALLED_SHOT_DIFFICULTY_BONUS
                )

            mechanical_result = resolve_opposed_character_check(
                db=db,
                attacker_character_id=proposal.actor_character_id,
                defender_character_id=check.target_character_id,
                attacker_attribute=check.attribute_name,
                attacker_core_skill=check.core_skill_name,
                attacker_specialization=check.specialization_name,
                defender_attribute=check.target_attribute_name,
                defender_core_skill=check.target_core_skill_name,
                defender_specialization=check.target_specialization_name,
                defender_situational_bonus=defender_situational_bonus,
            )

        elif check.difficulty is not None:
            effective_difficulty = check.difficulty

            if check.called_shot:
                effective_difficulty += (
                    CALLED_SHOT_DIFFICULTY_BONUS
                )

            mechanical_result = resolve_character_check(
                db=db,
                character_id=proposal.actor_character_id,
                attribute_name=check.attribute_name,
                core_skill_name=check.core_skill_name,
                specialization_name=check.specialization_name,
                difficulty=effective_difficulty,
            )

        else:
            raise ValueError(
                f"Check '{check.check_id}' has neither a difficulty "
                f"nor enough information for an opposed check."
            )

        damage = 0
        target_health = None
        resource_effect_results = []

        if mechanical_result["success"]:
            if check.proposed_base_damage > 0:
                if target is None:
                    raise ValueError(
                        f"Check '{check.check_id}' proposes damage "
                        f"but has no target character."
                    )

                core_skill = get_skill_level(
                    db=db,
                    character_id=proposal.actor_character_id,
                    skill_name=check.core_skill_name,
                )

                specialization = 0

                if check.specialization_name is not None:
                    specialization = get_skill_level(
                        db=db,
                        character_id=proposal.actor_character_id,
                        skill_name=check.specialization_name,
                    )

                damage = calculate_damage(
                    base_damage=check.proposed_base_damage,
                    character_level=actor.level,
                    core_skill=core_skill,
                    specialization=specialization,
                )

                health = change_resource(
                    db=db,
                    character_id=target.id,
                    resource_name="health",
                    amount=-damage,
                )

                target_health = health.current

            for effect in check.immediate_resource_effects:
                effect_target = get_character(
                    db=db,
                    character_id=effect.target_character_id,
                )

                resource = get_resource(
                    db=db,
                    character_id=effect.target_character_id,
                    resource_name=effect.resource_name,
                )

                before = resource.current

                updated_resource = change_resource(
                    db=db,
                    character_id=effect.target_character_id,
                    resource_name=effect.resource_name,
                    amount=effect.amount,
                )

                resource_effect_results.append(
                    {
                        "target_character_id": effect_target.id,
                        "target_name": effect_target.name,
                        "target_role": effect_target.role,
                        "resource_name": effect.resource_name,
                        "amount": effect.amount,
                        "before": before,
                        "after": updated_resource.current,
                    }
                )

        result = {
            "check_id": check.check_id,
            "description": check.description,
            "skipped": False,
            **mechanical_result,
            "damage": damage,
            "resource_effects": resource_effect_results,
        }

        if target is not None:
            result["target_character_id"] = target.id
            result["target_name"] = target.name
            result["target_role"] = target.role

        if target_health is not None:
            result["target_health"] = target_health

        results_by_id[check.check_id] = result
        check_results.append(result)

    return {
        "description": proposal.description,
        "actor_character_id": actor.id,
        "actor_name": actor.name,
        "actor_role": actor.role,
        "resource_name": proposal.resource_name,
        "resource_cost": proposal.resource_cost,
        "resource_remaining": resource_remaining,
        "checks": check_results,
    }
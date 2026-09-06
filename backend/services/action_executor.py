from sqlalchemy.orm import Session

from backend import schemas
from backend.game.damage import calculate_damage
from backend.services.actions import (
    CALLED_SHOT_DIFFICULTY_BONUS,
    validate_action_proposal,
)
from backend.services.checks import (
    resolve_character_check,
    resolve_opposed_character_check,
)
from backend.services.resources import (
    change_resource,
    spend_resource,
)
from backend.services.stats import (
    get_character,
    get_skill_level,
)


def execute_action(
    db: Session,
    proposal: schemas.ActionProposal,
) -> dict:
    """
    Validate and execute a structured freeform action proposal.

    Checks are resolved in order. A check is skipped when one of
    its required earlier checks failed.
    """

    proposal = validate_action_proposal(proposal)

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
            }

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

        if (
            mechanical_result["success"]
            and check.proposed_base_damage > 0
        ):
            if check.target_character_id is None:
                raise ValueError(
                    f"Check '{check.check_id}' proposes damage "
                    f"but has no target character."
                )

            actor = get_character(
                db=db,
                character_id=proposal.actor_character_id,
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
                character_id=check.target_character_id,
                resource_name="health",
                amount=-damage,
            )

            target_health = health.current

        result = {
            "check_id": check.check_id,
            "description": check.description,
            "skipped": False,
            **mechanical_result,
            "damage": damage,
        }

        if target_health is not None:
            result["target_health"] = target_health

        results_by_id[check.check_id] = result
        check_results.append(result)

    return {
        "description": proposal.description,
        "actor_character_id": proposal.actor_character_id,
        "resource_name": proposal.resource_name,
        "resource_cost": proposal.resource_cost,
        "resource_remaining": resource_remaining,
        "checks": check_results,
    }
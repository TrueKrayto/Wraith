from backend import schemas
from backend.database import SessionLocal
from backend.services.action_executor import execute_action
from backend.services.resources import get_resource


db = SessionLocal()

try:
    actor_character_id = 5
    target_character_id = 5

    starting_mana = get_resource(
        db=db,
        character_id=actor_character_id,
        resource_name="mana",
    ).current

    starting_health = get_resource(
        db=db,
        character_id=target_character_id,
        resource_name="health",
    ).current

    proposal = schemas.ActionProposal(
        actor_character_id=actor_character_id,
        target_character_id=target_character_id,
        description=(
            "I pull an object free with telekinesis "
            "and throw it into the target's chest."
        ),
        resource_name="mana",
        resource_cost=20,
        checks=[
            schemas.ActionCheckProposal(
                check_id="pull_free",
                description="Pull the object free",
                attribute_name="attunement",
                core_skill_name="magic",
                specialization_name="telekinesis",
                difficulty=0,
                target_character_id=target_character_id,
                proposed_base_damage=0,
                requires_success_of=[],
            ),
            schemas.ActionCheckProposal(
                check_id="throw_object",
                description="Throw the object into the chest",
                attribute_name="attunement",
                core_skill_name="magic",
                specialization_name="telekinesis",
                difficulty=0,
                target_character_id=target_character_id,
                target_area="chest",
                called_shot=True,
                proposed_base_damage=15,
                requires_success_of=["pull_free"],
            ),
        ],
        ongoing_effects=[],
    )

    result = execute_action(
        db=db,
        proposal=proposal,
    )

    print("Starting mana:", starting_mana)
    print("Starting health:", starting_health)
    print("Action result:", result)

finally:
    # Test only — preserve the real database state.
    db.rollback()
    db.close()
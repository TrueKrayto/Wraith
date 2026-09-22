from backend import schemas
from backend.services.actions import validate_action_proposal


proposal = schemas.ActionProposal(
    actor_character_id=5,
    target_character_id=1,
    description="I curse his strength.",
    attribute_name="attunement",
    core_skill_name="magic",
    specialization_name="curses",
    proposed_base_damage=-10,
    proposed_difficulty=-5,
    resource_name="mana",
    resource_cost=-20,
    ongoing_effects=[
        schemas.OngoingEffectProposal(
            name="Weakening Curse",
            effect_type="debuff",
            target_stat="strength",
            magnitude=-3,
            duration_turns=5,
        )
    ],
)

validated = validate_action_proposal(proposal)

print("Base damage:", validated.proposed_base_damage)
print("Difficulty:", validated.proposed_difficulty)
print("Resource cost:", validated.resource_cost)
print("Effect magnitude:", validated.ongoing_effects[0].magnitude)
print("Duration:", validated.ongoing_effects[0].duration_turns)
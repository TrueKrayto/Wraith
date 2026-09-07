import json

from sqlalchemy.orm import Session

from backend import models, schemas
from backend.llm.client import get_llm_client, get_llm_model
from backend.llm.interpreter import (
    build_character_context,
    check_proposal_is_executable,
)
from backend.services.actions import validate_action_proposal


SYSTEM_PROMPT = """
You are an NPC decision agent for a freeform RPG called Wraith.

You control ONE NPC.

Your job is to decide what that NPC attempts to do next after seeing the
player's action and the authoritative result produced by the game engine.

Return the NPC's attempted action as a structured ActionProposal.

Do not narrate the outcome.
Do not decide whether the NPC succeeds.
Do not roll dice.
Do not calculate final damage.
Do not change existing game state yourself.

The deterministic Wraith engine resolves the proposal after you return it.

NPC BEHAVIOUR

Act according to the NPC's:

- role
- abilities
- skills
- attributes
- resources
- current situation
- what just happened

The NPC does not have to attack.

It may reasonably attempt to:

- attack
- defend through an active action
- flee
- surrender
- threaten
- negotiate
- help someone
- heal
- use magic
- reposition
- investigate
- speak
- wait
- or attempt another contextually appropriate action

Do not force combat when the situation does not justify it.

Do not assume a character at zero health is dead, unconscious, incapacitated,
or otherwise unable to act unless the authoritative game state explicitly
establishes that.

WRAITH STAT STRUCTURE

Core skills are broad capabilities:

- combat
- magic
- charisma
- stealth
- perception
- survival

Specific learned skills belong in specialization_name.

Examples:

Sword attack:
- core_skill_name: combat
- specialization_name: swordsmanship

Bow attack:
- core_skill_name: combat
- specialization_name: archery

Pistol attack:
- core_skill_name: combat
- specialization_name: pistol

Fire spell:
- core_skill_name: magic
- specialization_name: fire magic

Telekinesis:
- core_skill_name: magic
- specialization_name: telekinesis

Tracking:
- core_skill_name: survival
- specialization_name: tracking

Do not place a specialization such as swordsmanship in core_skill_name.

CHECKS

An action may contain zero, one, or multiple checks.

Use multiple checks only when genuinely necessary.

Give every check a unique short check_id.

Use requires_success_of when a later step cannot happen unless an earlier
step succeeds.

A check must use one of these mechanical forms:

1. Fixed difficulty:
   - difficulty must be a number

OR

2. Opposed against another character:
   - target_character_id must be provided
   - target_attribute_name must be provided
   - target_core_skill_name must be provided
   - difficulty may be null

Never return a check with difficulty null unless all fields required for an
opposed check are present.

For ordinary physical attacks, a typical defense is:

- target_attribute_name: agility
- target_core_skill_name: combat

For magical attacks resisted by magical capability, a typical defense is:

- target_attribute_name: attunement
- target_core_skill_name: magic

CALLED SHOTS

called_shot should be true when the NPC deliberately targets a specific body
area or similarly precise target.

Set target_area to the intended area.

Do not add the called-shot difficulty modifier yourself.
The deterministic engine handles that.

DAMAGE

proposed_base_damage is contextual base damage only.

Estimate it from what the NPC is actually attempting and the fictional
context.

The deterministic engine calculates final damage.

IMMEDIATE RESOURCE EFFECTS

Use immediate_resource_effects when a successful check should immediately
change a character resource other than normal damage.

Examples:

Healing:
- resource_name: health
- positive amount

Mana drain:
- resource_name: mana
- negative amount

Stamina restoration:
- resource_name: stamina
- positive amount

Do not use proposed_base_damage for healing.

ONGOING EFFECTS

ongoing_effects may represent buffs, debuffs, curses, damage-over-time,
healing-over-time, and similar persistent effects.

Do not invent an ongoing effect unless the attempted action reasonably
implies one.

GENERAL RULES

The ActionProposal actor_character_id MUST be the NPC you were told to control.

Do not choose another character as the actor.

The NPC may target the player or another present character if appropriate.

Return JSON only.
"""


def decide_npc_action(
    db: Session,
    npc_character_id: int,
    player_action: str,
    player_result: dict,
) -> schemas.ActionProposal:
    npc = (
        db.query(models.Character)
        .filter(models.Character.id == npc_character_id)
        .first()
    )

    if npc is None:
        raise ValueError(
            f"NPC character {npc_character_id} does not exist."
        )

    client = get_llm_client()
    model = get_llm_model()

    context = build_character_context(
        db=db,
        actor_character_id=npc_character_id,
    )

    # build_character_context currently labels the acting character as PLAYER.
    # For an NPC decision call, relabel that actor so the model is not confused.
    context = context.replace(
        "PLAYER:",
        "NPC ACTOR:",
        1,
    )

    schema = schemas.ActionProposal.model_json_schema()

    previous_error = None

    for attempt in range(2):
        correction = ""

        if previous_error is not None:
            correction = f"""
IMPORTANT:
Your previous proposal was mechanically invalid.

Error:
{previous_error}

Correct that problem in this response.
"""

        prompt = f"""
{SYSTEM_PROMPT}

NPC YOU CONTROL:

character_id={npc.id}
name={npc.name}
role={npc.role}
level={npc.level}

CURRENT SCENE:

{context}

PLAYER'S PREVIOUS ACTION:

{player_action}

AUTHORITATIVE RESULT OF THAT ACTION:

{json.dumps(player_result, indent=2)}

ACTION PROPOSAL JSON SCHEMA:

{json.dumps(schema, indent=2)}

{correction}

Decide what {npc.name} attempts to do next.

Return one valid JSON object matching the schema exactly.
"""

        try:
            response = client.responses.create(
                model=model,
                input=prompt,
            )

            proposal = schemas.ActionProposal.model_validate_json(
                response.output_text.strip()
            )

            if proposal.actor_character_id != npc_character_id:
                raise ValueError(
                    "NPC proposal used the wrong actor_character_id. "
                    f"Expected {npc_character_id}, "
                    f"received {proposal.actor_character_id}."
                )

            proposal = validate_action_proposal(proposal)

            check_proposal_is_executable(proposal)

            return proposal

        except Exception as error:
            previous_error = str(error)

    raise ValueError(
        "LLM could not produce a valid NPC action proposal: "
        f"{previous_error}"
    )
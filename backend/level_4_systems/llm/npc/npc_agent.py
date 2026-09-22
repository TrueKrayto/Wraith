import json
from typing import TypeVar

from pydantic import BaseModel


ProposalT = TypeVar(
    "ProposalT",
    bound=BaseModel,
)


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


def _check_proposal_is_executable(
    proposal: BaseModel,
) -> None:
    """
    Check the minimum structural requirements needed for a
    proposed action to be mechanically resolvable.

    Full game validation remains outside the NPC subsystem.
    """

    checks = getattr(
        proposal,
        "checks",
        [],
    )

    for check in checks:
        is_fixed = (
            getattr(
                check,
                "difficulty",
                None,
            )
            is not None
        )

        is_opposed = (
            getattr(
                check,
                "target_character_id",
                None,
            )
            is not None
            and getattr(
                check,
                "target_attribute_name",
                None,
            )
            is not None
            and getattr(
                check,
                "target_core_skill_name",
                None,
            )
            is not None
        )

        if not is_fixed and not is_opposed:
            check_id = getattr(
                check,
                "check_id",
                "unknown",
            )

            raise ValueError(
                f"Check '{check_id}' must either have "
                "a difficulty or complete opposed-check "
                "target stats."
            )


def decide_npc_action(
    *,
    client,
    model: str,
    npc_character_id: int | str,
    npc_context: dict,
    scene_context: str,
    player_action: str,
    player_result: dict,
    proposal_schema: type[ProposalT],
) -> ProposalT:
    """
    Generate an attempted NPC action.

    The caller supplies:

    - the LLM client
    - the model
    - NPC identity/context
    - scene context
    - the previous player action/result
    - the proposal schema to use

    This subsystem does not access persistence, select a provider,
    execute mechanics, or import another LLM sibling.
    """

    schema = proposal_schema.model_json_schema()

    npc_name = str(
        npc_context.get(
            "name",
            "NPC",
        )
    )

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

{json.dumps(npc_context, indent=2)}

CURRENT SCENE:

{scene_context}

PLAYER'S PREVIOUS ACTION:

{player_action}

AUTHORITATIVE RESULT OF THAT ACTION:

{json.dumps(player_result, indent=2)}

ACTION PROPOSAL JSON SCHEMA:

{json.dumps(schema, indent=2)}

{correction}

Decide what {npc_name} attempts to do next.

Return one valid JSON object matching the schema exactly.
"""

        try:
            response = client.responses.create(
                model=model,
                input=prompt,
            )

            proposal = proposal_schema.model_validate_json(
                response.output_text.strip()
            )

            actor_character_id = getattr(
                proposal,
                "actor_character_id",
                None,
            )

            if actor_character_id != npc_character_id:
                raise ValueError(
                    "NPC proposal used the wrong actor_character_id. "
                    f"Expected {npc_character_id}, "
                    f"received {actor_character_id}."
                )

            _check_proposal_is_executable(
                proposal
            )

            return proposal

        except Exception as error:
            previous_error = str(error)

    raise ValueError(
        "LLM could not produce a valid NPC action proposal: "
        f"{previous_error}"
    )
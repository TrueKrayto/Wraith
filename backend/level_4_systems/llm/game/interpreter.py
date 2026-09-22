import json

from .schemas import ActionProposal


SYSTEM_PROMPT = """
You are the action interpreter for a freeform RPG called Wraith.

Your job is to translate the player's natural-language action into a
structured ActionProposal.

Do not narrate the outcome.
Do not decide whether the action succeeds.
Do not roll dice.
Do not calculate final damage.

Interpret what the player is attempting and propose the mechanical pieces.

WRAITH STAT STRUCTURE

Core skills are broad capabilities:

- combat
- magic
- charisma
- stealth
- perception
- survival

More specific learned skills belong in specialization_name.

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

A check must be one of these mechanical forms:

1. Fixed difficulty:
   - difficulty must be a number

OR

2. Opposed against another character:
   - target_character_id must be provided
   - target_attribute_name must be provided
   - target_core_skill_name must be provided
   - difficulty may be null

Never return a check with difficulty null unless all fields required for
an opposed check are present.

For ordinary physical attacks, a typical defense is:
- target_attribute_name: agility
- target_core_skill_name: combat

For magical attacks resisted by magical capability, a typical defense is:
- target_attribute_name: attunement
- target_core_skill_name: magic

CALLED SHOTS

called_shot should be true when the player deliberately targets a specific
body area or similarly precise target.

Examples:
- through the chest
- in the eye
- at his hand
- across the throat

Set target_area to the intended area.

Do not add the called-shot difficulty modifier yourself.
The deterministic engine handles that.

DAMAGE

proposed_base_damage is contextual base damage only.

Estimate it from what the player is actually attempting and the fictional
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

For example, if the player attempts:
"Heal Clara to full health"

the successful healing check should include an immediate_resource_effect
targeting Clara's health.

Use the character's current and maximum resource values from the scene
context to estimate the required amount.

Do not use proposed_base_damage for healing.

Do not apply immediate_resource_effects unless the associated check succeeds.
The deterministic engine handles that.

ONGOING EFFECTS

ongoing_effects may represent buffs, debuffs, curses, damage-over-time,
healing-over-time, and similar persistent effects.

Do not invent an ongoing effect unless the attempted action reasonably
implies one.

GENERAL RULES

Keep player actions freeform.
Do not restrict the player to a predefined action list.

Return JSON only.
"""


def check_proposal_is_executable(
    proposal: ActionProposal,
) -> None:
    """
    Ensure every proposed check has enough information for the
    deterministic engine to resolve it.

    This only validates the structural requirements of the LLM output.
    Broader mechanical validation belongs outside the LLM subsystem.
    """

    for check in proposal.checks:
        is_fixed = check.difficulty is not None

        is_opposed = (
            check.target_character_id is not None
            and check.target_attribute_name is not None
            and check.target_core_skill_name is not None
        )

        if not is_fixed and not is_opposed:
            raise ValueError(
                f"Check '{check.check_id}' must either have "
                f"a difficulty or complete opposed-check target stats."
            )


def interpret_player_action(
    *,
    client,
    model: str,
    actor_character_id: int,
    action_text: str,
    scene_context: str,
) -> ActionProposal:
    """
    Interpret a player's natural-language action into an ActionProposal.

    The caller supplies:

    - the LLM client
    - the model to use
    - the actor character ID
    - the player's action text
    - the already-built scene context

    This subsystem does not access persistence, choose an LLM provider,
    or execute game mechanics.
    """

    schema = ActionProposal.model_json_schema()

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

CURRENT SCENE:
{scene_context}

ACTOR CHARACTER ID:
{actor_character_id}

ACTION PROPOSAL JSON SCHEMA:
{json.dumps(schema, indent=2)}

PLAYER ACTION:
{action_text}

{correction}

Return one valid JSON object matching the schema exactly.
"""

        try:
            response = client.responses.create(
                model=model,
                input=prompt,
            )

            proposal = ActionProposal.model_validate_json(
                response.output_text.strip()
            )

            check_proposal_is_executable(proposal)

            return proposal

        except Exception as error:
            previous_error = str(error)

    raise ValueError(
        "LLM could not produce a valid action proposal: "
        f"{previous_error}"
    )
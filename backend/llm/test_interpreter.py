import json

from backend import schemas
from backend.llm.client import get_llm_client, get_llm_model


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

Core skills are broad capabilities. The core skills are:

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

Use multiple checks only when the action genuinely contains multiple
mechanical steps.

Give every check a unique short check_id.

Use requires_success_of when a later step cannot happen unless an earlier
step succeeds.

For an opposed check, provide BOTH:
- target_attribute_name
- target_core_skill_name

For ordinary physical attacks, a typical defense is:
- target_attribute_name: agility
- target_core_skill_name: combat

For magical attacks resisted by magical capability, a typical defense is:
- target_attribute_name: attunement
- target_core_skill_name: magic

If the check is opposed, difficulty may be null.

If there is no opposing character and the task is against the environment,
use a fixed difficulty instead.

CALLED SHOTS

called_shot should be true when the player deliberately targets a specific
body area or similarly precise target, such as:

- through the chest
- in the eye
- at his hand
- across the throat

Set target_area to the intended area.

Do not add the called-shot difficulty modifier yourself. The deterministic
engine handles that.

DAMAGE

proposed_base_damage is contextual base damage only.

Estimate it from what the player is actually attempting and the relevant
fictional context.

The deterministic engine calculates final damage using character level,
skills, specializations, and other mechanics.

ONGOING EFFECTS

ongoing_effects may represent buffs, debuffs, curses, damage-over-time,
healing-over-time, and similar persistent effects.

Do not invent an ongoing effect unless the player's attempted action
reasonably implies one.

GENERAL RULES

Keep player actions freeform.
Do not restrict the player to a predefined action list.
Translate the action into whatever combination of checks and effects is
actually required.

Return JSON only.
"""


def main():
    client = get_llm_client()
    model = get_llm_model()

    schema = schemas.ActionProposal.model_json_schema()

    print(f"Using model: {model}")
    print("Type 'exit' to quit.")

    while True:
        user_input = input("\nAction: ").strip()

        if user_input.lower() == "exit":
            break

        if not user_input:
            continue

        context = """
Actor:
- character_id: 5
- name: Defaults Test
- level: 10
- strength: 12
- agility: 5
- attunement: 5
- combat: 30
- magic: 0
- swordsmanship: 10
- mana: 65
- stamina: 80

Other character present:
- character_id: 1
- name: Test Character
- level: 10
"""

        prompt = f"""
{SYSTEM_PROMPT}

CURRENT SCENE:
{context}

ACTION PROPOSAL JSON SCHEMA:
{json.dumps(schema, indent=2)}

PLAYER ACTION:
{user_input}

Return one valid JSON object matching the schema exactly.
"""

        response = client.responses.create(
            model=model,
            input=prompt,
        )

        raw_output = response.output_text.strip()

        print("\nRaw LLM output:")
        print(raw_output)

        try:
            proposal = schemas.ActionProposal.model_validate_json(
                raw_output
            )

            print("\nParsed ActionProposal:")
            print(
                json.dumps(
                    proposal.model_dump(),
                    indent=2,
                )
            )

        except Exception as error:
            print("\nFAILED TO PARSE:")
            print(error)


if __name__ == "__main__":
    main()
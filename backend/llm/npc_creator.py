import json

from backend.entities.characters import (
    create_npc,
    schemas,
)
from backend.llm.client import get_llm_client, get_llm_model


SYSTEM_PROMPT = """
You are the NPC creator for a freeform RPG called Wraith.

Your job is to convert a natural-language NPC description into structured
NPC creation data.

You define WHO the character is and their broad mechanical capabilities.
The character engine will generate all exact numerical stats.

Do not narrate.
Do not add commentary.
Do not return markdown.
Return JSON only.


IDENTITY

Fill in reasonable character details whenever they can be inferred from the
description, name, role, title, species, or other context.

Prefer a reasonable inferred value over null when there is enough evidence.

Do not contradict explicit information supplied by the user.


SEX

Infer sex when the character's name, pronouns, title, or description gives
a strong conventional indication.

Examples:

- Ben -> male
- Sarah -> female
- "the queen" -> female
- "his brother" -> male

Names are contextual rather than absolute.

If the name or description is genuinely ambiguous, return null.


AGE

Infer a plausible age when the character concept gives enough information.

Examples:

- "young paladin" -> young adult
- "elderly blacksmith" -> older adult
- "teenage apprentice" -> teenager
- "veteran soldier" -> mature adult

Choose a reasonable exact age that fits the concept.

Take species into account where appropriate.

A young elf, dwarf, vampire, or other long-lived species does not necessarily
use the same age range as a young human.

If there is genuinely no useful basis for estimating age, return null.

DESCRIPTION AND PERSONALITY

The initial creation pass may store a short description and personality stub.

If the user's description explicitly provides appearance or personality
information, preserve it in these fields.

Examples:

"Ben, a young archer with messy blond hair"
description:
"Young human archer with messy blond hair."

"Ben is shy but kind"
personality:
"Shy but kind."

Keep these fields short. They are only initial stubs.

Do NOT invent detailed appearance or personality merely to fill these fields.

If the prompt gives no meaningful information for a field, return null.

A later enrichment process will create or expand missing narrative information.


OTHER IDENTITY FIELDS

Infer occupation, faction, rank, home, and current location when reasonably
supported by the description or supplied world context.

Do not invent specific world facts merely to avoid null.

For example:

If the prompt only says "Ben, a young paladin", do not invent a named faction,
city, home, or current location without supporting context.

Species may be any appropriate species and is not restricted to a fixed list.

Do not generate an npc_id.
Do not generate an alive value.

The character engine handles those fields.


NPC TIER

tier represents narrative/world importance, not combat power.

Use:

low:
- incidental or minor characters
- shopkeepers
- ordinary guards
- bartenders
- background civilians

medium:
- recurring characters
- quest-related characters
- officers
- important merchants
- notable local figures

high:
- major story characters
- rulers
- major villains
- faction leaders
- characters with substantial world importance


LEVEL

level ranges from 1 to 50.

Level represents the character's overall experience and development.

It does NOT represent narrative importance.

A king is not automatically high level.

High level does not mean the character is good at every skill.

A level 50 scholar may still have low combat, magic, stealth, and survival
while being exceptional in a narrow group of specialist skills.

Use the character's age, profession, training, experience, background, and
description when estimating level.


ATTRIBUTES

Every character must include all six attributes:

- strength
- agility
- endurance
- intellect
- attunement
- presence

Each attribute must be assigned one of:

- low
- mid
- high

Choose bands based on the character concept.

Do not generate numerical attribute values.

The character engine handles exact values.


CORE SKILLS

Every character must include all six core skills:

- charisma
- stealth
- perception
- survival
- combat
- magic

Each core skill must be assigned one of:

- low
- mid
- high

Every core skill must be present even if the character is terrible at it.

Use "low" when appropriate.


SPECIALIST SKILLS

Core skills represent broad capability.

You may add any number of specialist or learned skills when appropriate.

Examples:

- swordsmanship
- archery
- fire magic
- necromancy
- medicine
- blacksmithing
- bartending
- alchemy
- history
- investigation
- navigation
- diplomacy
- shield defense
- tracking

Specialist skills do not replace core skills.

A master swordsman still requires combat.

A fire mage still requires magic.

A skilled healer may have medicine or healing magic while still requiring
the appropriate core skills.

Specialist skill names are freeform strings.

Do not invent specialist skills purely to fill space.

Only include skills that are meaningful for the character.


STAT BANDS

"low", "mid", and "high" describe capability relative to the character's
level.

A high-level character may still have many low skills.

A low-level character may have high bands in the narrow areas they are
particularly talented or trained in.

Do not calculate exact numbers.

The character engine combines level and band to generate final values.
"""


def generate_npc_data(
    npc_prompt: str,
) -> schemas.NPCCreationData:
    """Generate and validate an NPC creation payload."""

    client = get_llm_client()
    model = get_llm_model()

    schema = schemas.NPCCreationData.model_json_schema()

    previous_error = None

    for attempt in range(2):
        correction = ""

        if previous_error is not None:
            correction = f"""
IMPORTANT:
Your previous response was invalid.

Error:
{previous_error}

Correct that problem in this response.
"""

        prompt = f"""
{SYSTEM_PROMPT}

NPC CREATION JSON SCHEMA:
{json.dumps(schema, indent=2)}

NPC DESCRIPTION:
{npc_prompt}

{correction}

Return one valid JSON object matching the schema exactly.
"""

        try:
            response = client.responses.create(
                model=model,
                input=prompt,
            )

            return schemas.NPCCreationData.model_validate_json(
                response.output_text.strip()
            )

        except Exception as error:
            previous_error = str(error)

    raise ValueError(
        "LLM could not generate valid NPC data: "
        f"{previous_error}"
    )


def generate_npc(
    npc_prompt: str,
    seed: str | int | None = None,
):
    """Generate a complete NPC from a natural-language description."""

    payload = generate_npc_data(npc_prompt)

    return create_npc(
        payload=payload,
        seed=seed,
    )
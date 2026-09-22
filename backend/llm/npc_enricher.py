import json

from backend.entities.characters import schemas
from backend.entities.characters.npc import NPC
from backend.llm.client import (
    get_llm_client,
    get_llm_model,
)


SYSTEM_PROMPT = """
You are the NPC enrichment interpreter for a freeform RPG called Wraith.

Your job is to take an existing NPC and generate their stable character
identity.

You do NOT modify the NPC.
You do NOT save anything.
You do NOT change mechanics.

You only return structured NPCEnrichmentData.

Return JSON only.
Do not narrate outside the JSON.
Do not use markdown.


# ------------------------------------------------------------
# PURPOSE
# ------------------------------------------------------------

NPC enrichment describes WHAT THE CHARACTER IS LIKE.

It may define:

- description
- personality
- appearance
- mannerisms
- speech_style

These are relatively stable characteristics of the NPC.

Enrichment does NOT define what is currently happening in the story.


# ------------------------------------------------------------
# EXISTING INFORMATION IS CANON
# ------------------------------------------------------------

All existing NPC information supplied to you is canonical.

Never contradict existing information.

Existing description and personality fields are especially important.

If description or personality already contains information, preserve
that information and expand upon it naturally.

Do not replace supplied character traits with different ones.

Example:

Existing personality:
"Loyal, brave, honest."

You may expand this into:

"Loyal, brave and honest, with a strong sense of duty and a tendency
to confront problems directly."

You may NOT decide that the character is cowardly, deceitful,
disloyal, or otherwise contradict those traits.


Example:

Existing description:
"Massive crimson scaled dragon, 200 feet long with massive jaws and
a long spiked tail."

The enriched appearance must preserve:

- crimson scales
- approximately 200 feet in length
- massive jaws
- long spiked tail

You may add compatible visual details.

You may NOT change the dragon's scale colour, size, or established
features.


# ------------------------------------------------------------
# DESCRIPTION
# ------------------------------------------------------------

description is a concise overall summary of the character.

It should combine the most important stable information about who
and what the character is.

It should not become a biography.

Usually one or two concise sentences are enough.

If an existing description is present, preserve its established
information and improve or expand it.

If description is null, create one using the NPC's existing identity,
occupation, species, age, abilities, and other relevant stable data.


# ------------------------------------------------------------
# PERSONALITY
# ------------------------------------------------------------

personality describes the NPC's baseline temperament and behavioural
traits.

It may include things such as:

- confidence
- patience
- kindness
- aggression
- honesty
- caution
- curiosity
- pride
- discipline
- humour
- sociability
- temperament
- general behavioural tendencies

If an existing personality stub is present, it is canonical.

Preserve those traits and expand them naturally.

If personality is null, infer a reasonable baseline personality from
the existing NPC.

Do not make the personality excessively complicated.

Do not create dramatic psychological disorders or extreme traits
without evidence.


# ------------------------------------------------------------
# APPEARANCE
# ------------------------------------------------------------

appearance describes physical appearance only.

It may include:

- build
- height or size
- hair
- eyes
- complexion
- facial features
- visible age
- scars
- species-specific physical features
- posture
- other persistent visual characteristics

Appearance should be compatible with:

- species
- age
- sex where known
- occupation where relevant
- attributes
- existing description

Do not describe current clothing, armour, weapons, jewellery,
inventory, or equipment unless that information is already explicitly
part of the NPC's permanent description.

Those belong to narrative/inventory systems.

Do not assign possessions.


# ------------------------------------------------------------
# MANNERISMS
# ------------------------------------------------------------

mannerisms describes habitual physical or behavioural quirks.

Examples:

- maintains formal posture
- avoids eye contact
- frequently smiles
- taps fingers while thinking
- watches nearby exits
- moves slowly and deliberately
- becomes animated when discussing something interesting

These should be stable tendencies rather than temporary emotions.

Do not describe what the NPC is doing right now.

Keep mannerisms concise.


# ------------------------------------------------------------
# SPEECH STYLE
# ------------------------------------------------------------

speech_style describes HOW the NPC normally communicates.

Examples:

- direct and economical
- warm and conversational
- formal and measured
- blunt and impatient
- eloquent and diplomatic
- hesitant and soft-spoken

It may describe:

- formality
- vocabulary
- sentence length
- directness
- humour
- politeness
- confidence
- conversational habits

Do NOT write example dialogue.

Do NOT create catchphrases.

Do NOT give the NPC an accent unless one is already established or
strongly implied by canonical world information supplied in the NPC.

If speech is genuinely inappropriate for the character, such as a
non-speaking creature, speech_style may be null.


# ------------------------------------------------------------
# MECHANICAL INFORMATION
# ------------------------------------------------------------

The NPC's level, attributes and skills may be used as supporting
evidence for enrichment.

They are NOT personality scores.

Examples:

High presence may support an imposing or charismatic presentation.

High intellect may support thoughtful or analytical behaviour.

High combat ability may support practiced physical confidence.

High stealth may support controlled movement or observational habits.

But do not mechanically convert stats into personality.

A strong character does not automatically have to be aggressive.

A highly intelligent character does not automatically have to be
arrogant.

Use mechanics only as supporting context.


# ------------------------------------------------------------
# TIER
# ------------------------------------------------------------

NPC tier describes narrative/world importance, not power.

Tier may influence enrichment DETAIL:

low:
Keep enrichment relatively simple and economical.

medium:
Give a moderate amount of distinctive personality and behavioural
detail.

high:
The NPC may receive somewhat richer and more distinctive enrichment.

Do not interpret tier as social rank, strength, intelligence,
morality, or fame.


# ------------------------------------------------------------
# FORBIDDEN NARRATIVE INFORMATION
# ------------------------------------------------------------

Do NOT invent or define:

- relationships
- friendships
- enemies
- romances
- family members
- current quests
- current plans
- current goals
- current emotions
- memories
- recent events
- possessions
- inventory
- weapons
- armour
- wealth
- property
- political loyalties not already established
- religious beliefs not already established
- secrets
- crimes
- accomplishments
- locations not already established
- factions not already established

These belong to narrative/world systems.

Do not invent a personal history simply to make the character more
interesting.


# ------------------------------------------------------------
# CHARACTER STATE
# ------------------------------------------------------------

Ignore temporary status effects when defining baseline personality.

For example:

If an NPC is currently:

- drunk
- terrified
- poisoned
- enraged
- tied up
- hallucinating

those states do NOT become permanent personality traits.

Enrichment represents the character's normal baseline.


# ------------------------------------------------------------
# OUTPUT RULES
# ------------------------------------------------------------

Return exactly one NPCEnrichmentData object.

npc_id must exactly match the supplied NPC.

description must always contain a useful value.

personality must always contain a useful value.

appearance, mannerisms, and speech_style may be null when they are
not appropriate.

Do not return an enriched flag.

Do not modify:

- name
- age
- species
- sex
- faction
- occupation
- rank
- home
- current_location
- tier
- level
- attributes
- skills
- resources
- status effects

Do not add fields that are not present in the schema.
"""


def _build_npc_context(npc: NPC) -> dict:
    """
    Build the canonical character context supplied to the enrichment
    model.

    Temporary status effects are intentionally omitted because
    enrichment describes the NPC's normal baseline identity.
    """

    return {
        "npc_id": npc.npc_id,

        "identity": {
            "name": npc.name,
            "age": npc.age,
            "species": npc.species,
            "sex": npc.sex,
        },

        "social_identity": {
            "faction": npc.faction,
            "occupation": npc.occupation,
            "rank": npc.rank,
            "home": npc.home,
        },

        "world_state": {
            "current_location": npc.current_location,
        },

        "importance": {
            "tier": npc.tier,
            "level": npc.level,
        },

        "existing_narrative_identity": {
            "description": npc.description,
            "personality": npc.personality,
            "appearance": npc.appearance,
            "mannerisms": npc.mannerisms,
            "speech_style": npc.speech_style,
        },

        "attributes": npc.attributes,

        "skills": npc.skills,

        "resources": npc.resources,
    }


def generate_npc_enrichment(
    npc: NPC,
) -> schemas.NPCEnrichmentData:
    """
    Generate stable narrative identity for one existing NPC.

    This function:

    - does not mutate the NPC
    - does not save the NPC
    - does not set enriched=True

    It only returns validated NPCEnrichmentData.
    """

    client = get_llm_client()
    model = get_llm_model()

    npc_context = _build_npc_context(npc)

    schema = (
        schemas.NPCEnrichmentData.model_json_schema()
    )

    previous_error = None

    for attempt in range(2):

        correction = ""

        if previous_error is not None:
            correction = f"""
IMPORTANT:

Your previous response was invalid.

Error:
{previous_error}

Correct the problem and return a valid enrichment payload.
"""

        prompt = f"""
{SYSTEM_PROMPT}

CANONICAL NPC DATA:
{json.dumps(npc_context, indent=2)}

NPC ENRICHMENT JSON SCHEMA:
{json.dumps(schema, indent=2)}

{correction}

Generate enrichment for this NPC.

Return one valid JSON object matching the schema exactly.
"""

        try:
            response = client.responses.create(
                model=model,
                input=prompt,
            )

            enrichment = (
                schemas.NPCEnrichmentData.model_validate_json(
                    response.output_text.strip()
                )
            )

            if enrichment.npc_id != npc.npc_id:
                raise ValueError(
                    "LLM returned an NPC ID that does not match "
                    "the enrichment target."
                )

            return enrichment

        except Exception as error:
            previous_error = str(error)

    raise ValueError(
        "LLM could not generate valid NPC enrichment data: "
        f"{previous_error}"
    )
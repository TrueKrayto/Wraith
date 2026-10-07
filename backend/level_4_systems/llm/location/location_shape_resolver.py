from typing import Literal

from pydantic import BaseModel, ConfigDict


LocationCreationShape = Literal[
    "city",
    "town",
    "village",
    "complex",
    "building",
    "simple",
    "dungeon",
]


class LocationShapeDecision(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )

    creation_shape: LocationCreationShape


SYSTEM_PROMPT = """
You classify location creation requests for the Wraith RPG engine.

Choose exactly one creation shape based on the STRUCTURE the requested
location needs.

Available shapes:

city
- cities, capitals, metropolises
- large urban settlements
- generates districts and streets / areas

town
- towns and smaller urban settlements
- generates streets / areas

village
- villages, hamlets, small settlements
- generates local areas and buildings

complex
- castles
- palaces
- forts and fortresses
- large temples or monasteries
- estates
- universities
- other large locations containing multiple major internal areas

building
- taverns
- inns
- houses
- shops
- guild halls
- small temples
- standalone towers
- other individual buildings with internal rooms

simple
- streets
- squares
- plazas
- parks
- fields
- forest clearings
- bridges
- crossroads
- docks
- other locations that do not initially require an internal hierarchy

dungeon
- dungeons
- dungeon-like ruins
- deliberately structured encounter locations

Dungeons are handled by a separate game system. Return "dungeon" when
the request is genuinely for a dungeon so the caller can reject or
reroute it.

Important rules:

- Classify by required structure, not merely by the exact noun used.
- A castle should normally be "complex", not "building".
- A tavern should normally be "building", not "simple".
- A capital city should be "city".
- A hamlet should normally be "village".
- Do not invent location content.
- Do not generate the location.
- Only decide which creation shape should be used.
"""


def resolve_location_creation_shape(
    *,
    client,
    model: str,
    location_prompt: str,
    location_type: str | None = None,
) -> str:
    """
    Decide which bounded location creation schema should handle
    a location request.
    """

    context = location_prompt

    if location_type is not None:
        context = f"""
Known canonical location type:
{location_type}

Location request:
{location_prompt}
"""

    last_error: Exception | None = None

    for attempt in range(2):

        response = client.responses.create(
            model=model,
            input=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": context,
                },
            ],
            text={
                "format": {
                    "type": "json_schema",
                    "name": "location_shape_decision",
                    "schema": LocationShapeDecision.model_json_schema(),
                    "strict": True,
                }
            },
        )

        try:
            decision = LocationShapeDecision.model_validate_json(
                response.output_text
            )

            return decision.creation_shape

        except Exception as exc:
            last_error = exc

            context = f"""
{context}

The previous response failed validation.

Validation error:
{exc}

Return only valid data matching the required schema.
"""

    raise ValueError(
        "Failed to resolve location creation shape."
    ) from last_error
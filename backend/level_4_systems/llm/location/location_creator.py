import json

from backend.level_5_entities import location_schemas


LocationCreationPayload = (
    location_schemas.CityCreationData
    | location_schemas.TownCreationData
    | location_schemas.VillageCreationData
    | location_schemas.ComplexLocationCreationData
    | location_schemas.BuildingCreationData
    | location_schemas.SimpleLocationCreationData
)


CREATION_SCHEMAS = {
    "city": location_schemas.CityCreationData,
    "town": location_schemas.TownCreationData,
    "village": location_schemas.VillageCreationData,
    "complex": location_schemas.ComplexLocationCreationData,
    "building": location_schemas.BuildingCreationData,
    "simple": location_schemas.SimpleLocationCreationData,
}


SYSTEM_PROMPT = """
You are the location skeleton creator for a freeform RPG called Wraith.

Your job is to convert a natural-language location description into a
bounded structural skeleton.

You define WHAT EXISTS.

You do NOT fully enrich locations.
You do NOT save anything.
You do NOT create game entities.
You do NOT create dungeons.

Return JSON only.
Do not narrate outside the JSON.
Do not use markdown.


# ------------------------------------------------------------
# PURPOSE
# ------------------------------------------------------------

Location creation establishes canonical world structure.

The returned structure should contain enough information for the game to know:

- what the root location is
- what its immediate structural children are
- the next useful structural layer where required by the supplied schema
- a small number of important NPC skeletons

Descriptions at this stage are brief.

Full narrative detail is handled later by location enrichment.


# ------------------------------------------------------------
# CANONICAL STRUCTURE
# ------------------------------------------------------------

Everything returned becomes canonical world data.

Do not create duplicate locations within the same structure.

Names should be distinct and appropriate to the supplied setting.

Children must logically belong to their parent.

Examples:

A city may contain:
- districts
- wards
- quarters
- major areas

Those districts may contain:
- streets
- squares
- docks
- markets
- other equivalent areas

A village may contain:
- roads
- lanes
- village areas

Those areas may contain:
- inns
- smithies
- houses
- temples
- farms
- shops

A castle or other large complex may contain:
- wings
- courtyards
- towers
- halls
- major internal areas

Buildings may contain:
- rooms
- internal areas


# ------------------------------------------------------------
# GENERATION DEPTH
# ------------------------------------------------------------

Generate ONLY the structure requested by the supplied JSON schema.

Do not recursively continue beyond it.

For example:

If a city schema requests:

city
→ districts
→ streets

STOP at streets.

Do not invent buildings beneath those streets.

If a village schema requests:

village
→ areas
→ buildings

STOP at buildings.

Do not create rooms inside those buildings.

The schema limits are hard maximums.

Do not exceed them.


# ------------------------------------------------------------
# BRIEF DESCRIPTIONS
# ------------------------------------------------------------

brief_description should normally be one or two concise sentences.

It should establish enough identity for the location to be referenced before
full enrichment.

It may describe:

- purpose
- broad character
- architectural style
- social role
- general atmosphere
- notable structural identity

Do not turn brief_description into a detailed scene description.

Do not describe temporary events or current activity unless explicitly
provided by the creation request.


# ------------------------------------------------------------
# KEY NPC SKELETONS
# ------------------------------------------------------------

Key NPCs represent people important enough to establish during creation.

Examples:

- ruler
- mayor
- magistrate
- guard captain
- guild leader
- important priest
- estate owner
- innkeeper where genuinely important

Only create NPC skeletons that are useful to the root location.

Do not fill the maximum merely because capacity exists.

Do not generate ordinary crowds, generic guards, servants, residents, or
background civilians as key NPCs.

NPC skeletons should remain minimal.

The character pipeline will create and enrich the actual NPC later.


# ------------------------------------------------------------
# LOCKS AND LIMITS
# ------------------------------------------------------------

children_locked means the existing child set is exhaustive.

Set children_locked=true ONLY when the creation request explicitly establishes
that no additional children may exist.

Otherwise use false.

child_limit is a hard lifetime maximum for that location's direct children.

Use a specific child_limit only when the supplied creation request establishes
one.

Otherwise return null and allow later generation policy to decide expansion.


# ------------------------------------------------------------
# EXISTING / AUTHORED FACTS
# ------------------------------------------------------------

Anything explicitly supplied by the caller is canonical.

Preserve:

- names
- location types
- cultural details
- structural requirements
- naming conventions
- required children
- explicit locks
- explicit limits

You may fill unspecified details within the bounds of the schema.

Do not contradict authored information.


# ------------------------------------------------------------
# LOCATION TYPES
# ------------------------------------------------------------

location_type describes what the specific location actually is.

Examples:

- city
- town
- village
- district
- ward
- street
- market_square
- docks
- castle
- palace
- fortress
- temple
- inn
- smithy
- house
- room
- forest
- bridge
- clearing

For the "complex" creation shape, the root location_type should describe the
actual complex, such as "castle" or "palace", not simply "complex".

For the "simple" creation shape, use the actual type such as "bridge",
"clearing", or "monument".


# ------------------------------------------------------------
# DUNGEONS
# ------------------------------------------------------------

Do not create dungeon structures.

Dungeons use a separate gameplay system with their own rules for encounters,
loot, progression, puzzles, bosses, completion state, and persistent room
state.

If supplied context mentions a dungeon as part of the wider world, it may be
referenced only as an external concept. Do not generate its internal structure.


# ------------------------------------------------------------
# OUTPUT
# ------------------------------------------------------------

Return exactly one JSON object matching the supplied schema.

Do not add fields that are not present in the schema.
"""


def _get_creation_schema(
    creation_shape: str,
):
    """
    Resolve a location creation shape to its validated schema.
    """

    key = (
        creation_shape
        .strip()
        .lower()
    )

    schema = CREATION_SCHEMAS.get(key)

    if schema is None:
        raise ValueError(
            "Unsupported location creation shape: "
            f"'{creation_shape}'. "
            f"Expected one of: {', '.join(CREATION_SCHEMAS)}."
        )

    return schema


def generate_location_data(
    *,
    client,
    model: str,
    creation_shape: str,
    location_prompt: str,
) -> LocationCreationPayload:
    """
    Convert a natural-language location description into validated
    location creation data.

    creation_shape determines the structural schema used:

    - city
    - town
    - village
    - complex
    - building
    - simple

    This function does not:

    - choose an LLM provider
    - create Location entities
    - persist locations
    - enrich locations
    - create NPC entities
    - queue background work
    """

    schema_class = _get_creation_schema(
        creation_shape
    )

    schema = schema_class.model_json_schema()

    previous_error = None

    for attempt in range(2):
        correction = ""

        if previous_error is not None:
            correction = f"""
IMPORTANT:

Your previous response was invalid.

Error:
{previous_error}

Correct the problem and return a valid location creation payload.
"""

        prompt = f"""
{SYSTEM_PROMPT}

CREATION SHAPE:
{creation_shape}

LOCATION CREATION JSON SCHEMA:
{json.dumps(schema, indent=2)}

LOCATION REQUEST:
{location_prompt}

{correction}

Generate the bounded location skeleton.

Return one valid JSON object matching the schema exactly.
"""

        try:
            response = client.responses.create(
                model=model,
                input=prompt,
            )

            return schema_class.model_validate_json(
                response.output_text.strip()
            )

        except Exception as error:
            previous_error = str(error)

    raise ValueError(
        "LLM could not generate valid location creation data: "
        f"{previous_error}"
    )
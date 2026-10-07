from backend.level_5_entities import (
    Location,
    location_schemas,
)


SYSTEM_PROMPT = """
You enrich an existing canonical location for the Wraith RPG.

The location already exists.

Your job is to add useful narrative detail to that location without
changing its identity, hierarchy, or canonical facts.

Rules:

- Preserve the supplied location name and type.
- Preserve all supplied canonical facts.
- Do not create new locations.
- Do not create NPCs.
- Do not change parent or child relationships.
- Do not invent major history unless clearly implied by the supplied context.
- Use the parent and child locations as context when provided.
- The description should make the location useful for scene narration.
- Describe physical layout, atmosphere, visible features, and immediately
  relevant environmental details.
- Avoid excessive purple prose.
- Do not mention game mechanics.
- Return only data matching the required schema.
"""


def generate_location_enrichment(
    *,
    client,
    model: str,
    location: Location,
    parent: Location | None = None,
    children: list[Location] | None = None,
) -> location_schemas.LocationEnrichmentData:
    """
    Generate narrative enrichment for an existing canonical Location.
    """

    children = children or []

    child_context = "\n".join(
        (
            f"- {child.name} [{child.location_type}]: "
            f"{child.brief_description}"
        )
        for child in children
    )

    if not child_context:
        child_context = "None"

    if parent is None:
        parent_context = "None"
    else:
        parent_context = (
            f"{parent.name} [{parent.location_type}]: "
            f"{parent.brief_description}"
        )

    prompt = f"""
LOCATION ID:
{location.location_id}

LOCATION NAME:
{location.name}

LOCATION TYPE:
{location.location_type}

BRIEF DESCRIPTION:
{location.brief_description}

PARENT LOCATION:
{parent_context}

KNOWN CHILD LOCATIONS:
{child_context}

Write the full narrative description for this location.
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
                    "content": prompt,
                },
            ],
            text={
                "format": {
                    "type": "json_schema",
                    "name": "location_enrichment",
                    "schema": (
                        location_schemas
                        .LocationEnrichmentData
                        .model_json_schema()
                    ),
                    "strict": True,
                }
            },
        )

        try:
            return (
                location_schemas
                .LocationEnrichmentData
                .model_validate_json(
                    response.output_text
                )
            )

        except Exception as exc:
            last_error = exc

            prompt = f"""
{prompt}

The previous response failed validation.

Validation error:
{exc}

Return only valid data matching the required schema.
"""

    raise ValueError(
        "Failed to generate location enrichment."
    ) from last_error
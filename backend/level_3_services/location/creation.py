from dataclasses import dataclass

from backend.level_4_systems import (
    generate_location_data,
    get_llm_client,
    get_llm_model,
    get_location_repository,
    resolve_location_creation_shape,
)

from backend.level_5_entities import (
    Location,
    create_building_locations,
    create_city_locations,
    create_complex_locations,
    create_simple_location,
    create_town_locations,
    create_village_locations,
    location_schemas,
)


# ------------------------------------------------------------------
# CREATION RESULT
# ------------------------------------------------------------------

@dataclass
class LocationCreationResult:
    """
    Result of one location creation / structure-generation pass.
    """

    locations: list[Location]

    key_npcs: list[
        location_schemas.KeyNPCSkeletonData
    ]

    creation_shape: str | None = None
    already_generated: bool = False


# ------------------------------------------------------------------
# CREATION FUNCTIONS
# ------------------------------------------------------------------

CREATION_FUNCTIONS = {
    "city": create_city_locations,
    "town": create_town_locations,
    "village": create_village_locations,
    "complex": create_complex_locations,
    "building": create_building_locations,
    "simple": create_simple_location,
}


# ------------------------------------------------------------------
# LOCATION CREATION
# ------------------------------------------------------------------

def create_location_from_prompt(
    *,
    location_prompt: str,
    creation_shape: str | None = None,
    root_id: str | None = None,
) -> LocationCreationResult:
    """
    Create or expand one location structure.

    If creation_shape is omitted:
        The location shape is selected automatically.

    If creation_shape is supplied:
        The explicit shape is used.

    If root_id is supplied:
        The existing canonical root is preserved while its internal
        structure is generated.

    This service does not:

    - enrich locations
    - create NPC entities
    - queue workers
    """

    repository = get_location_repository()

    # --------------------------------------------------------------
    # EXISTING ROOT
    # --------------------------------------------------------------

    root = None

    if root_id is not None:

        root = repository.get(
            root_id
        )

        if root is None:
            raise ValueError(
                f"Location not found: {root_id}"
            )

        if root.structure_generated:
            return LocationCreationResult(
                locations=[root],
                key_npcs=[],
                creation_shape=creation_shape,
                already_generated=True,
            )

    # --------------------------------------------------------------
    # LLM
    # --------------------------------------------------------------

    client = get_llm_client()
    model = get_llm_model()

    # --------------------------------------------------------------
    # CREATION SHAPE
    # --------------------------------------------------------------

    if creation_shape is None:

        shape = resolve_location_creation_shape(
            client=client,
            model=model,
            location_prompt=location_prompt,
            location_type=(
                root.location_type
                if root is not None
                else None
            ),
        )

    else:

        shape = (
            creation_shape
            .strip()
            .lower()
        )

    # --------------------------------------------------------------
    # DUNGEON GUARD
    # --------------------------------------------------------------

    if shape == "dungeon":
        raise ValueError(
            "Dungeon generation is handled by the dedicated "
            "dungeon system."
        )

    # --------------------------------------------------------------
    # CREATION FUNCTION
    # --------------------------------------------------------------

    create_locations = CREATION_FUNCTIONS.get(
        shape
    )

    if create_locations is None:
        raise ValueError(
            "Unsupported location creation shape: "
            f"'{shape}'. "
            f"Expected one of: "
            f"{', '.join(CREATION_FUNCTIONS)}."
        )

    # --------------------------------------------------------------
    # GENERATION PROMPT
    # --------------------------------------------------------------

    prompt = location_prompt

    if root is not None:

        prompt = f"""
CANONICAL EXISTING ROOT LOCATION:

Name: {root.name}
Type: {root.location_type}
Brief description: {root.brief_description}
Children locked: {root.children_locked}
Child limit: {root.child_limit}

The returned root location must preserve this canonical name and type.

LOCATION CREATION REQUEST:

{location_prompt}
"""

    # --------------------------------------------------------------
    # LOCATION GENERATION
    # --------------------------------------------------------------

    payload = generate_location_data(
        client=client,
        model=model,
        creation_shape=shape,
        location_prompt=prompt,
    )

    # --------------------------------------------------------------
    # ENTITY CREATION
    # --------------------------------------------------------------

    locations = create_locations(
        payload=payload,
        root=root,
    )

    # --------------------------------------------------------------
    # PERSISTENCE
    # --------------------------------------------------------------

    repository.save_all(
        locations
    )

    # --------------------------------------------------------------
    # KEY NPC SKELETONS
    # --------------------------------------------------------------

    key_npcs = list(
        getattr(
            payload,
            "key_npcs",
            [],
        )
    )

    return LocationCreationResult(
        locations=locations,
        key_npcs=key_npcs,
        creation_shape=shape,
    )
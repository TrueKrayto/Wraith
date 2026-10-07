from pydantic import BaseModel, Field, ConfigDict


# ------------------------------------------------------------------
# SHARED SKELETONS
# ------------------------------------------------------------------

class LocationSkeletonData(BaseModel):
    """
    Minimal canonical data required to create a location skeleton.

    A skeleton establishes that a location exists without requiring
    full enrichment.
    """

    name: str
    location_type: str

    brief_description: str

    children_locked: bool = False
    child_limit: int | None = None


class KeyNPCSkeletonData(BaseModel):
    """
    Minimal identity for an important NPC discovered during
    location creation.

    The NPC pipeline is responsible for creating and enriching
    the actual character.
    """

    name: str

    occupation: str | None = None
    rank: str | None = None

    brief_description: str | None = None


# ------------------------------------------------------------------
# CITY
# ------------------------------------------------------------------

class DistrictSkeletonData(BaseModel):
    """
    City district skeleton.

    Cities generate districts and their immediate streets/areas,
    but no buildings during the initial creation pass.
    """

    name: str
    brief_description: str

    children_locked: bool = False
    child_limit: int | None = None

    streets: list[LocationSkeletonData] = Field(
        min_length=1,
        max_length=3,
    )


class CityCreationData(BaseModel):
    """
    Bounded initial skeleton for a city.

    Maximum initial structure:

    - 1 city
    - 5 districts
    - 3 streets/areas per district
    - 5 key NPCs
    """

    city: LocationSkeletonData

    districts: list[DistrictSkeletonData] = Field(
        min_length=1,
        max_length=5,
    )

    key_npcs: list[KeyNPCSkeletonData] = Field(
        default_factory=list,
        max_length=5,
    )


# ------------------------------------------------------------------
# TOWN
# ------------------------------------------------------------------

class TownCreationData(BaseModel):
    """
    Bounded initial skeleton for a town.

    Towns do not require a district layer.
    Their immediate children are streets or equivalent areas.
    """

    town: LocationSkeletonData

    streets: list[LocationSkeletonData] = Field(
        min_length=2,
        max_length=6,
    )

    key_npcs: list[KeyNPCSkeletonData] = Field(
        default_factory=list,
        max_length=5,
    )


# ------------------------------------------------------------------
# VILLAGE
# ------------------------------------------------------------------

class VillageAreaSkeletonData(BaseModel):
    """
    Village street/area skeleton.

    Villages are small enough that their initial creation pass may
    also establish building skeletons.
    """

    name: str
    location_type: str

    brief_description: str

    children_locked: bool = False
    child_limit: int | None = None

    buildings: list[LocationSkeletonData] = Field(
        min_length=1,
        max_length=6,
    )


class VillageCreationData(BaseModel):
    """
    Bounded initial skeleton for a village.

    Villages generate more deeply than cities or towns because
    their total structure is much smaller.
    """

    village: LocationSkeletonData

    areas: list[VillageAreaSkeletonData] = Field(
        min_length=1,
        max_length=3,
    )

    key_npcs: list[KeyNPCSkeletonData] = Field(
        default_factory=list,
        max_length=5,
    )


# ------------------------------------------------------------------
# LARGE COMPLEX
# ------------------------------------------------------------------

class ComplexAreaSkeletonData(BaseModel):
    """
    Major area within a large non-dungeon complex.

    Examples:

    - castle wing
    - palace wing
    - fortress courtyard
    - temple complex
    - university building
    """

    name: str
    location_type: str

    brief_description: str

    children_locked: bool = False
    child_limit: int | None = None

    sublocations: list[LocationSkeletonData] = Field(
        default_factory=list,
        max_length=5,
    )


class ComplexLocationCreationData(BaseModel):
    """
    Initial skeleton for a large structured location.

    Suitable for locations such as:

    - castles
    - palaces
    - forts
    - large temples
    - estates
    - universities

    Dungeons are intentionally excluded.
    """

    location: LocationSkeletonData

    areas: list[ComplexAreaSkeletonData] = Field(
        min_length=1,
        max_length=6,
    )

    key_npcs: list[KeyNPCSkeletonData] = Field(
        default_factory=list,
        max_length=5,
    )


# ------------------------------------------------------------------
# BUILDING
# ------------------------------------------------------------------

class BuildingCreationData(BaseModel):
    """
    Initial skeleton for an ordinary building.

    Examples:

    - inn
    - smithy
    - shop
    - house
    - guild hall
    - small temple

    Rooms remain skeleton locations until gameplay requires them.
    """

    building: LocationSkeletonData

    rooms: list[LocationSkeletonData] = Field(
        default_factory=list,
        max_length=8,
    )

    key_npcs: list[KeyNPCSkeletonData] = Field(
        default_factory=list,
        max_length=3,
    )


# ------------------------------------------------------------------
# SIMPLE LOCATION
# ------------------------------------------------------------------

class SimpleLocationCreationData(BaseModel):
    """
    Creation shape for locations that do not need an initial
    internal hierarchy.

    Examples:

    - crossroads
    - clearing
    - bridge
    - monument
    - isolated ruin
    - campsite
    """

    location: LocationSkeletonData

    key_npcs: list[KeyNPCSkeletonData] = Field(
        default_factory=list,
        max_length=3,
    )

# ------------------------------------------------------------------
# Enrichment
# ------------------------------------------------------------------

class LocationEnrichmentData(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )

    location_id: str
    description: str
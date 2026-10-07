from .location import Location
from .schemas import (
    BuildingCreationData,
    CityCreationData,
    ComplexLocationCreationData,
    SimpleLocationCreationData,
    TownCreationData,
    VillageCreationData,
)


# ------------------------------------------------------------------
# ROOT PREPARATION
# ------------------------------------------------------------------

def _prepare_root_location(
    skeleton,
    root: Location | None = None,
) -> Location:
    """
    Create a new root location or reuse an existing canonical root.

    Existing roots preserve:

    - location_id
    - parent_id
    - name
    - location_type
    - authored structural rules
    - existing enrichment state

    Generation may fill missing brief information and mark the
    root's child structure as generated.
    """

    if root is None:
        return Location(
            name=skeleton.name,
            location_type=skeleton.location_type,
            brief_description=skeleton.brief_description,
            children_locked=skeleton.children_locked,
            child_limit=skeleton.child_limit,
            structure_generated=True,
        )

    # --------------------------------------------------------------
    # EXISTING ROOT VALIDATION
    # --------------------------------------------------------------

    if root.name != skeleton.name:
        raise ValueError(
            "Generated location name does not match existing root."
        )

    if root.location_type != skeleton.location_type:
        raise ValueError(
            "Generated location type does not match existing root."
        )

    # --------------------------------------------------------------
    # FILL MISSING SKELETON DATA
    # --------------------------------------------------------------

    if root.brief_description is None:
        root.brief_description = skeleton.brief_description

    # Existing structural rules remain canonical.
    #
    # We intentionally do not overwrite:
    #
    # - children_locked
    # - child_limit
    # - parent_id
    # - enriched
    #
    # These may have been defined by authored world data.

    root.structure_generated = True

    return root


# ------------------------------------------------------------------
# CITY
# ------------------------------------------------------------------

def create_city_locations(
    payload: CityCreationData,
    root: Location | None = None,
) -> list[Location]:
    """
    Convert validated city creation data into Location entities.

    Creates:

    - city
    - districts
    - streets / areas

    If root is supplied, that existing city skeleton is expanded
    rather than creating a replacement city.

    Key NPC skeletons are handled by higher layers.
    Persistence is handled elsewhere.
    """

    locations: list[Location] = []

    city = _prepare_root_location(
        skeleton=payload.city,
        root=root,
    )

    locations.append(city)

    for district_data in payload.districts:

        district = Location(
            name=district_data.name,
            location_type="district",
            parent_id=city.location_id,
            brief_description=district_data.brief_description,
            children_locked=district_data.children_locked,
            child_limit=district_data.child_limit,
            structure_generated=True,
        )

        locations.append(district)

        for street_data in district_data.streets:

            street = Location(
                name=street_data.name,
                location_type=street_data.location_type,
                parent_id=district.location_id,
                brief_description=street_data.brief_description,
                children_locked=street_data.children_locked,
                child_limit=street_data.child_limit,
                structure_generated=False,
            )

            locations.append(street)

    return locations


# ------------------------------------------------------------------
# TOWN
# ------------------------------------------------------------------

def create_town_locations(
    payload: TownCreationData,
    root: Location | None = None,
) -> list[Location]:
    """
    Convert validated town creation data into Location entities.

    Creates:

    - town
    - streets / areas

    If root is supplied, that existing town skeleton is expanded
    rather than creating a replacement town.

    Key NPC skeletons are handled by higher layers.
    """

    locations: list[Location] = []

    town = _prepare_root_location(
        skeleton=payload.town,
        root=root,
    )

    locations.append(town)

    for street_data in payload.streets:

        street = Location(
            name=street_data.name,
            location_type=street_data.location_type,
            parent_id=town.location_id,
            brief_description=street_data.brief_description,
            children_locked=street_data.children_locked,
            child_limit=street_data.child_limit,
            structure_generated=False,
        )

        locations.append(street)

    return locations


# ------------------------------------------------------------------
# VILLAGE
# ------------------------------------------------------------------

def create_village_locations(
    payload: VillageCreationData,
    root: Location | None = None,
) -> list[Location]:
    """
    Convert validated village creation data into Location entities.

    Creates:

    - village
    - streets / areas
    - buildings

    If root is supplied, that existing village skeleton is expanded
    rather than creating a replacement village.

    Key NPC skeletons are handled by higher layers.
    """

    locations: list[Location] = []

    village = _prepare_root_location(
        skeleton=payload.village,
        root=root,
    )

    locations.append(village)

    for area_data in payload.areas:

        area = Location(
            name=area_data.name,
            location_type=area_data.location_type,
            parent_id=village.location_id,
            brief_description=area_data.brief_description,
            children_locked=area_data.children_locked,
            child_limit=area_data.child_limit,
            structure_generated=True,
        )

        locations.append(area)

        for building_data in area_data.buildings:

            building = Location(
                name=building_data.name,
                location_type=building_data.location_type,
                parent_id=area.location_id,
                brief_description=building_data.brief_description,
                children_locked=building_data.children_locked,
                child_limit=building_data.child_limit,
                structure_generated=False,
            )

            locations.append(building)

    return locations


# ------------------------------------------------------------------
# LARGE COMPLEX
# ------------------------------------------------------------------

def create_complex_locations(
    payload: ComplexLocationCreationData,
    root: Location | None = None,
) -> list[Location]:
    """
    Convert validated complex-location creation data into
    Location entities.

    Suitable for:

    - castles
    - palaces
    - forts
    - large temples
    - estates
    - universities

    If root is supplied, that existing complex skeleton is expanded
    rather than creating a replacement root.

    Dungeons are intentionally excluded.
    """

    locations: list[Location] = []

    complex_root = _prepare_root_location(
        skeleton=payload.location,
        root=root,
    )

    locations.append(complex_root)

    for area_data in payload.areas:

        area = Location(
            name=area_data.name,
            location_type=area_data.location_type,
            parent_id=complex_root.location_id,
            brief_description=area_data.brief_description,
            children_locked=area_data.children_locked,
            child_limit=area_data.child_limit,
            structure_generated=True,
        )

        locations.append(area)

        for sublocation_data in area_data.sublocations:

            sublocation = Location(
                name=sublocation_data.name,
                location_type=sublocation_data.location_type,
                parent_id=area.location_id,
                brief_description=sublocation_data.brief_description,
                children_locked=sublocation_data.children_locked,
                child_limit=sublocation_data.child_limit,
                structure_generated=False,
            )

            locations.append(sublocation)

    return locations


# ------------------------------------------------------------------
# BUILDING
# ------------------------------------------------------------------

def create_building_locations(
    payload: BuildingCreationData,
    root: Location | None = None,
) -> list[Location]:
    """
    Convert validated building creation data into Location entities.

    Creates:

    - building
    - room / internal-area skeletons

    If root is supplied, that existing building skeleton is expanded
    rather than creating a replacement building.

    Key NPC skeletons are handled by higher layers.
    """

    locations: list[Location] = []

    building = _prepare_root_location(
        skeleton=payload.building,
        root=root,
    )

    locations.append(building)

    for room_data in payload.rooms:

        room = Location(
            name=room_data.name,
            location_type=room_data.location_type,
            parent_id=building.location_id,
            brief_description=room_data.brief_description,
            children_locked=room_data.children_locked,
            child_limit=room_data.child_limit,
            structure_generated=False,
        )

        locations.append(room)

    return locations


# ------------------------------------------------------------------
# SIMPLE LOCATION
# ------------------------------------------------------------------

def create_simple_location(
    payload: SimpleLocationCreationData,
    root: Location | None = None,
) -> list[Location]:
    """
    Convert simple location creation data into a Location entity.

    Simple locations have no initial internal hierarchy.

    If root is supplied, the existing canonical location is reused.
    """

    location = _prepare_root_location(
        skeleton=payload.location,
        root=root,
    )

    return [location]
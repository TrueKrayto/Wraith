from threading import Lock
from typing import Protocol

from backend.level_5_entities import Location

from .temp_location_store import (
    load_locations,
    save_locations,
)


class LocationRepository(Protocol):
    """
    Persistence interface for location storage.

    Callers should depend on this interface rather than caring
    whether locations are stored in JSON, a database, memory,
    or somewhere else.
    """

    def get(
        self,
        location_id: str,
    ) -> Location | None:
        ...

    def save(
        self,
        location: Location,
    ) -> Location:
        ...

    def save_all(
        self,
        locations: list[Location],
    ) -> list[Location]:
        ...

    def get_all(
        self,
    ) -> list[Location]:
        ...

    def get_children(
        self,
        parent_id: str,
    ) -> list[Location]:
        ...

    def get_root_locations(
        self,
    ) -> list[Location]:
        ...

    def get_unenriched_ids(
        self,
    ) -> list[str]:
        ...

    def get_unstructured_ids(
        self,
    ) -> list[str]:
        ...

    def delete(
        self,
        location_id: str,
    ) -> bool:
        ...


class TempJSONLocationRepository:
    """
    Temporary JSON-backed location repository.

    This implementation exists only for development.

    Location relationships are derived from parent_id rather than
    storing duplicate child lists.
    """

    def __init__(self):
        self._lock = Lock()

    def get(
        self,
        location_id: str,
    ) -> Location | None:
        """
        Load one location by ID.
        """

        locations = load_locations()

        return locations.get(location_id)

    def save(
        self,
        location: Location,
    ) -> Location:
        """
        Insert or update one location.
        """

        with self._lock:
            locations = load_locations()

            locations[location.location_id] = location

            save_locations(locations)

        return location

    def save_all(
        self,
        new_locations: list[Location],
    ) -> list[Location]:
        """
        Insert or update multiple locations in one write.

        Useful when one creation pass produces an entire
        location skeleton tree.
        """

        with self._lock:
            locations = load_locations()

            for location in new_locations:
                locations[location.location_id] = location

            save_locations(locations)

        return new_locations

    def get_all(
        self,
    ) -> list[Location]:
        """
        Return every stored location.
        """

        locations = load_locations()

        return list(locations.values())

    def get_children(
        self,
        parent_id: str,
    ) -> list[Location]:
        """
        Return the direct children of one location.
        """

        locations = load_locations()

        return [
            location
            for location in locations.values()
            if location.parent_id == parent_id
        ]

    def get_root_locations(
        self,
    ) -> list[Location]:
        """
        Return locations with no parent.

        These represent top-level roots in the current
        location tree.
        """

        locations = load_locations()

        return [
            location
            for location in locations.values()
            if location.parent_id is None
        ]

    def get_unenriched_ids(
        self,
    ) -> list[str]:
        """
        Return IDs of locations still waiting for enrichment.
        """

        locations = load_locations()

        return [
            location.location_id
            for location in locations.values()
            if not location.enriched
        ]

    def get_unstructured_ids(
        self,
    ) -> list[str]:
        """
        Return IDs of locations whose child structure has
        not yet been generated.
        """

        locations = load_locations()

        return [
            location.location_id
            for location in locations.values()
            if not location.structure_generated
        ]

    def delete(
        self,
        location_id: str,
    ) -> bool:
        """
        Delete one location.

        This does not recursively delete children.
        Higher-level services are responsible for deciding
        what should happen to descendants.
        """

        with self._lock:
            locations = load_locations()

            if location_id not in locations:
                return False

            del locations[location_id]

            save_locations(locations)

        return True


# ------------------------------------------------------------------
# ACTIVE REPOSITORY
# ------------------------------------------------------------------

_repository: LocationRepository = TempJSONLocationRepository()


def get_location_repository() -> LocationRepository:
    """
    Return the currently configured location repository.
    """

    return _repository


def set_location_repository(
    repository: LocationRepository,
) -> None:
    """
    Replace the active location repository implementation.

    Useful later for:

    - database repositories
    - tests
    - in-memory repositories
    - alternate persistence backends
    """

    global _repository

    _repository = repository
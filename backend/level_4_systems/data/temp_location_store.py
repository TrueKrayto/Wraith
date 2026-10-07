import json
from dataclasses import asdict
from pathlib import Path

from backend.level_5_entities import Location


STORE_PATH = (
    Path(__file__).resolve().parent
    / "temp_locations.json"
)


def save_locations(
    locations: dict[str, Location],
) -> None:
    """
    Save the current temporary location store to disk.
    """

    STORE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    data = {
        location_id: asdict(location)
        for location_id, location in locations.items()
    }

    STORE_PATH.write_text(
        json.dumps(
            data,
            indent=2,
        ),
        encoding="utf-8",
    )


def load_locations() -> dict[str, Location]:
    """
    Load locations from the temporary JSON store.
    """

    if not STORE_PATH.exists():
        return {}

    raw_data = json.loads(
        STORE_PATH.read_text(
            encoding="utf-8",
        )
    )

    locations: dict[str, Location] = {}

    for location_id, location_data in raw_data.items():

        location = Location(
            **location_data
        )

        locations[location_id] = location

    return locations
import random

from .stat_bands import (
    StatBand,
    get_attribute_range,
    get_skill_range,
)
from .attributes import ATTRIBUTE_NAMES


def roll_value(
    minimum: int,
    maximum: int,
    rng: random.Random,
) -> int:
    """Roll an integer inside the supplied range."""

    return rng.randint(minimum, maximum)


def generate_attributes(
    level: int,
    bands: dict[str, StatBand | str],
    rng: random.Random,
) -> dict[str, int]:
    """
    Generate exact attribute values from attribute bands.

    Attributes are fixed by the game's ATTRIBUTE_NAMES list.
    """

    attributes = {}

    for attribute in ATTRIBUTE_NAMES:
        band = StatBand(bands[attribute])

        minimum, maximum = get_attribute_range(
            band=band,
            level=level,
        )

        attributes[attribute] = roll_value(
            minimum,
            maximum,
            rng,
        )

    return attributes


def generate_skills(
    level: int,
    bands: dict[str, StatBand | str],
    rng: random.Random,
) -> dict[str, int]:
    """
    Generate exact skill values from supplied skill bands.

    Skills are dynamic and are not restricted to CORE_SKILLS.
    Any skill name supplied in the payload can be generated.
    """

    skills = {}

    for skill, band_value in bands.items():
        band = StatBand(band_value)

        minimum, maximum = get_skill_range(
            band=band,
            level=level,
        )

        skills[skill] = roll_value(
            minimum,
            maximum,
            rng,
        )

    return skills


def generate_stat_block(
    level: int,
    attribute_bands: dict[str, StatBand | str],
    skill_bands: dict[str, StatBand | str],
    seed: str | int | None = None,
) -> dict:
    """
    Generate a complete attribute and skill stat block.

    A seed may be supplied for reproducible character generation.
    """

    rng = random.Random(seed)

    attributes = generate_attributes(
        level=level,
        bands=attribute_bands,
        rng=rng,
    )

    skills = generate_skills(
        level=level,
        bands=skill_bands,
        rng=rng,
    )

    return {
        "level": level,
        "attributes": attributes,
        "skills": skills,
    }
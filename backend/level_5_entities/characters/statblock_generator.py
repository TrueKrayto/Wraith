from .resource_generator import generate_resources
from .stat_generator import generate_stat_block


def generate_character_statblock(
    payload: dict,
) -> dict:
    """Generate attributes, skills, and resources from one payload."""

    level = payload["level"]

    stats = generate_stat_block(
        level=level,
        attribute_bands=payload["attributes"],
        skill_bands=payload["skills"],
        seed=payload.get("seed"),
    )

    resources = generate_resources(
        level=level,
        attributes=stats["attributes"],
    )

    return {
        "level": level,
        "attributes": stats["attributes"],
        "skills": stats["skills"],
        "resources": resources,
    }
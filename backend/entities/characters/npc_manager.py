from .npc import NPC
from .schemas import NPCCreationData
from .statblock_generator import generate_character_statblock


def create_npc(
    payload: NPCCreationData,
    seed: str | int | None = None,
) -> NPC:
    """
    Create a complete NPC from a validated creation payload.

    This function only constructs character state.
    Persistence is handled outside the character package.
    """

    statblock = generate_character_statblock(
        {
            "level": payload.level,
            "attributes": payload.attributes.model_dump(),
            "skills": payload.skills,
            "seed": seed,
        }
    )

    npc = NPC(
        name=payload.name,
        age=payload.age,
        species=payload.species,
        sex=payload.sex,

        faction=payload.faction,
        occupation=payload.occupation,
        rank=payload.rank,
        home=payload.home,

        current_location=payload.current_location,

        tier=payload.tier,
        level=payload.level,

        description=payload.description,
        personality=payload.personality,

        enriched=False,

        attributes=statblock["attributes"],
        skills=statblock["skills"],
        resources=statblock["resources"],
    )

    return npc
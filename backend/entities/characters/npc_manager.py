from .npc import NPC
from .schemas import NPCCreationData
from .statblock_generator import generate_character_statblock


npcs: dict[str, NPC] = {}


def create_npc(
    payload: NPCCreationData,
    seed: str | int | None = None,
) -> NPC:
    """
    Create a complete NPC from a validated creation payload.

    Generates exact attributes, skills, and resources,
    stores the NPC, and returns it.
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
        attributes=statblock["attributes"],
        skills=statblock["skills"],
        resources=statblock["resources"],
    )

    npcs[npc.npc_id] = npc

    return npc
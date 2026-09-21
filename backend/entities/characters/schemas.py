from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    model_validator,
)

from .skills import CORE_SKILLS
from .stat_bands import StatBand


CharacterRole = Literal["player", "npc"]
NPCTier = Literal["low", "medium", "high"]


class CharacterCreate(BaseModel):
    name: str
    role: CharacterRole
    level: int = 1


class CharacterUpdate(BaseModel):
    name: str | None = None
    role: CharacterRole | None = None


class CharacterRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str

    # Keep legacy occupation-style roles readable
    # until they are reassigned.
    role: str
    level: int


class CharacterSkillCreate(BaseModel):
    name: str
    level: int = 0


class CharacterSkillUpdate(BaseModel):
    level: int


class CharacterSkillRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    character_id: int
    name: str
    level: int


class CharacterAttributeCreate(BaseModel):
    name: str
    value: int = 5


class CharacterAttributeUpdate(BaseModel):
    value: int


class CharacterAttributeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    character_id: int
    name: str
    value: int


class CharacterResourceCreate(BaseModel):
    name: str
    current: int = 100
    maximum: int = 100


class CharacterResourceUpdate(BaseModel):
    current: int


class CharacterResourceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    character_id: int
    name: str
    current: int
    maximum: int


class AttributeBandPayload(BaseModel):
    strength: StatBand
    agility: StatBand
    endurance: StatBand
    intellect: StatBand
    attunement: StatBand
    presence: StatBand


class NPCCreationData(BaseModel):
    # Identity
    name: str
    age: int | None = None
    species: str = "Human"
    sex: str | None = None

    # Social / world identity
    faction: str | None = None
    occupation: str | None = None
    rank: str | None = None
    home: str | None = None

    # Current world state
    current_location: str | None = None

    # Importance / progression
    tier: NPCTier = "low"
    level: int = 1

    # Mechanical intent
    attributes: AttributeBandPayload
    skills: dict[str, StatBand]

    @model_validator(mode="after")
    def require_core_skills(self):
        missing = [
            skill
            for skill in CORE_SKILLS
            if skill not in self.skills
        ]

        if missing:
            raise ValueError(
                "Missing required core skills: "
                + ", ".join(missing)
            )

        return self


class NPCCreateRequest(BaseModel):
    prompt: str
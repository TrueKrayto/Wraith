from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)

from .skills import CORE_SKILLS
from .stat_bands import StatBand


CharacterRole = Literal["player", "npc"]
NPCTier = Literal["low", "medium", "high"]


# ------------------------------------------------------------------
# CHARACTER
# ------------------------------------------------------------------

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


# ------------------------------------------------------------------
# SKILLS
# ------------------------------------------------------------------

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


# ------------------------------------------------------------------
# ATTRIBUTES
# ------------------------------------------------------------------

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


# ------------------------------------------------------------------
# RESOURCES
# ------------------------------------------------------------------

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


# ------------------------------------------------------------------
# NPC CREATION
# ------------------------------------------------------------------

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
    description: str | None = None
    personality: str | None = None

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

# ------------------------------------------------------------------
# NPC ENRICHMENT
# ------------------------------------------------------------------

class NPCEnrichmentData(BaseModel):
    """
    Stable narrative identity generated during NPC enrichment.

    This describes what the character is like, not their current
    narrative circumstances.
    """

    npc_id: str

    # Concise overall character summary.
    description: str

    # Baseline temperament, traits, and behavioural tendencies.
    personality: str

    # Physical appearance only.
    appearance: str | None = None

    # Habitual gestures, behaviours, posture, and quirks.
    mannerisms: str | None = None

    # Normal communication style.
    speech_style: str | None = None
    
# ------------------------------------------------------------------
# NPC MUTATION
# ------------------------------------------------------------------

class SkillBandMutation(BaseModel):
    """
    Used when the AI introduces a new character skill.

    The AI chooses the skill name and capability band.
    The character engine generates the exact numerical value.
    """

    name: str
    band: StatBand


class ResourceMutation(BaseModel):
    """
    Update an existing character resource.

    Either current, maximum, or both may be supplied.
    """

    current: int | None = None
    maximum: int | None = None

    @model_validator(mode="after")
    def require_resource_value(self):
        if self.current is None and self.maximum is None:
            raise ValueError(
                "Resource mutation must specify current, maximum, or both."
            )

        return self


class StatusEffectMutation(BaseModel):
    """
    Freeform status effect proposed by the AI.
    """

    name: str
    source: str | None = None

    effect: str = "none"

    resource: str | None = None
    amount: int | None = None

    duration: int | None = None

    # Optional active status this effect depends upon.
    parent_effect: str | None = None


class NPCMutationData(BaseModel):
    """
    Structured mutation instructions for one NPC.
    """

    npc_id: str

    # Ordinary profile/world-state changes.
    field_updates: dict[
        str,
        str | int | bool | None,
    ] = Field(
        default_factory=dict
    )

    # Exact changes to existing attributes.
    #
    # Example:
    # {"strength": 10}
    attribute_updates: dict[str, int] = Field(
        default_factory=dict
    )

    # Exact changes to existing skills.
    #
    # Example:
    # {"combat": 20}
    skill_updates: dict[str, int] = Field(
        default_factory=dict
    )

    # Updates to character resources.
    #
    # Example:
    # {
    #     "health": {
    #         "current": 50
    #     }
    # }
    resource_updates: dict[
        str,
        ResourceMutation,
    ] = Field(
        default_factory=dict
    )

    # New dynamically inferred skills.
    add_skills: list[SkillBandMutation] = Field(
        default_factory=list
    )

    # Specialist skills to remove.
    remove_skills: list[str] = Field(
        default_factory=list
    )

    # New or reapplied status effects.
    add_status_effects: list[
        StatusEffectMutation
    ] = Field(
        default_factory=list
    )

    # Status effects that should cease to apply.
    remove_status_effects: list[str] = Field(
        default_factory=list
    )


class NPCMutationRequest(BaseModel):
    """
    Natural-language mutation request supplied to the AI layer.
    """

    prompt: str
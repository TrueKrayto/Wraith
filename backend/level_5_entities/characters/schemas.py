from typing import Literal

from pydantic import (
    BaseModel,
    Field,
    model_validator,
)

from .skills import CORE_SKILLS
from .stat_bands import StatBand


NPCTier = Literal["low", "medium", "high"]


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
    attribute_updates: dict[str, int] = Field(
        default_factory=dict
    )

    # Exact changes to existing skills.
    skill_updates: dict[str, int] = Field(
        default_factory=dict
    )

    # Updates to character resources.
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
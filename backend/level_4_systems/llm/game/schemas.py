from pydantic import BaseModel, Field


class OngoingEffectProposal(BaseModel):
    name: str
    effect_type: str

    target_stat: str | None = None

    magnitude: int = 0
    duration_turns: int | None = None

    resource_name: str | None = None
    tick_interval: int = 1


class ImmediateResourceEffectProposal(BaseModel):
    target_character_id: int
    resource_name: str
    amount: int


class ActionCheckProposal(BaseModel):
    check_id: str
    description: str

    attribute_name: str
    core_skill_name: str
    specialization_name: str | None = None

    difficulty: int | None = None

    target_character_id: int | None = None
    target_attribute_name: str | None = None
    target_core_skill_name: str | None = None
    target_specialization_name: str | None = None

    target_area: str | None = None
    called_shot: bool = False

    proposed_base_damage: int = 0

    immediate_resource_effects: list[
        ImmediateResourceEffectProposal
    ] = Field(default_factory=list)

    requires_success_of: list[str] = Field(
        default_factory=list
    )


class ActionProposal(BaseModel):
    actor_character_id: int
    target_character_id: int | None = None

    description: str

    resource_name: str | None = None
    resource_cost: int = 0

    checks: list[ActionCheckProposal] = Field(
        default_factory=list
    )

    ongoing_effects: list[OngoingEffectProposal] = Field(
        default_factory=list
    )
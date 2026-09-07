from pydantic import BaseModel, ConfigDict, Field


class CharacterCreate(BaseModel):
    name: str
    role: str
    level: int = 1

class CharacterUpdate(BaseModel):
    name: str | None = None
    role: str | None = None

class CharacterRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
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

class AttackRequest(BaseModel):
    attacker_character_id: int
    defender_character_id: int

    attacker_attribute: str
    attacker_core_skill: str
    attacker_specialization: str | None = None

    defender_attribute: str
    defender_core_skill: str
    defender_specialization: str | None = None

    base_damage: int
    power_multiplier: float = 1.0
    gear_bonus: int = 0

    resource_name: str | None = None
    resource_cost: int = 0

class CharacterCheckRequest(BaseModel):
    character_id: int

    attribute_name: str
    core_skill_name: str
    specialization_name: str | None = None

    difficulty: int

    gear_bonus: int = 0
    situational_bonus: int = 0

    resource_name: str | None = None
    resource_cost: int = 0

class OpposedCharacterCheckRequest(BaseModel):
    attacker_character_id: int
    defender_character_id: int

    attacker_attribute: str
    attacker_core_skill: str
    attacker_specialization: str | None = None

    defender_attribute: str
    defender_core_skill: str
    defender_specialization: str | None = None

    attacker_gear_bonus: int = 0
    defender_gear_bonus: int = 0

    attacker_situational_bonus: int = 0
    defender_situational_bonus: int = 0

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
    ] = Field(
        default_factory=list
    )

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

class PlayerActionRequest(BaseModel):
    actor_character_id: int
    action_text: str
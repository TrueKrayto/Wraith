from pydantic import BaseModel, ConfigDict


class CharacterCreate(BaseModel):
    name: str
    role: str
    level: int = 1


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
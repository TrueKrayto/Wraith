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
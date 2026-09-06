from sqlalchemy import Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class Character(Base):
    __tablename__ = "characters"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )
    name: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )
    role: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )
    level: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
    )


class CharacterSkill(Base):
    __tablename__ = "character_skills"

    __table_args__ = (
        UniqueConstraint(
            "character_id",
            "name",
            name="uq_character_skill_name",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )
    character_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )
    level: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )


class CharacterAttribute(Base):
    __tablename__ = "character_attributes"

    __table_args__ = (
        UniqueConstraint(
            "character_id",
            "name",
            name="uq_character_attribute_name",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )
    character_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )
    value: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=5,
    )


class CharacterResource(Base):
    __tablename__ = "character_resources"

    __table_args__ = (
        UniqueConstraint(
            "character_id",
            "name",
            name="uq_character_resource_name",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )
    character_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )
    current: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=100,
    )
    maximum: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=100,
    )


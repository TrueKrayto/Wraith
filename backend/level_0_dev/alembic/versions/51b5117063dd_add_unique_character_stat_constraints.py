"""add unique character stat constraints

Revision ID: 51b5117063dd
Revises: fd9935f9bd48
Create Date: 2026-09-06 23:24:41.994171

"""

from typing import Sequence, Union

from alembic import op


revision: str = "51b5117063dd"
down_revision: Union[str, Sequence[str], None] = "fd9935f9bd48"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("character_attributes") as batch_op:
        batch_op.create_unique_constraint(
            "uq_character_attribute_name",
            ["character_id", "name"],
        )

    with op.batch_alter_table("character_resources") as batch_op:
        batch_op.create_unique_constraint(
            "uq_character_resource_name",
            ["character_id", "name"],
        )

    with op.batch_alter_table("character_skills") as batch_op:
        batch_op.create_unique_constraint(
            "uq_character_skill_name",
            ["character_id", "name"],
        )


def downgrade() -> None:
    with op.batch_alter_table("character_skills") as batch_op:
        batch_op.drop_constraint(
            "uq_character_skill_name",
            type_="unique",
        )

    with op.batch_alter_table("character_resources") as batch_op:
        batch_op.drop_constraint(
            "uq_character_resource_name",
            type_="unique",
        )

    with op.batch_alter_table("character_attributes") as batch_op:
        batch_op.drop_constraint(
            "uq_character_attribute_name",
            type_="unique",
        )
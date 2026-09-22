from alembic import op
import sqlalchemy as sa


revision = "b2bfa03107ee"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "characters",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("role", sa.String(), nullable=False),
        sa.Column("level", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_characters_id",
        "characters",
        ["id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_characters_id", table_name="characters")
    op.drop_table("characters")
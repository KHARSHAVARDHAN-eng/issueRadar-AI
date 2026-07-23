"""create repositories table

Revision ID: 002_create_repositories_table
Revises: 001_create_users_table
Create Date: 2026-07-23 23:44:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "002_create_repositories_table"
down_revision: str | None = "001_create_users_table"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "repositories",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("github_id", sa.BigInteger(), nullable=False),
        sa.Column("owner", sa.String(length=255), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=512), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("language", sa.String(length=100), nullable=True),
        sa.Column("default_branch", sa.String(length=100), nullable=False, server_default="main"),
        sa.Column("stars", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("forks", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("private", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("added_by_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["added_by_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("added_by_id", "github_id", name="uq_user_github_repo"),
    )
    op.create_index(
        op.f("ix_repositories_added_by_id"), "repositories", ["added_by_id"], unique=False
    )
    op.create_index(op.f("ix_repositories_full_name"), "repositories", ["full_name"], unique=False)
    op.create_index(op.f("ix_repositories_github_id"), "repositories", ["github_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_repositories_github_id"), table_name="repositories")
    op.drop_index(op.f("ix_repositories_full_name"), table_name="repositories")
    op.drop_index(op.f("ix_repositories_added_by_id"), table_name="repositories")
    op.drop_table("repositories")

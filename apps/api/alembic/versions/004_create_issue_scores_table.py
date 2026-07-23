"""create issue scores table

Revision ID: 004_create_issue_scores_table
Revises: 003_create_sync_tables
Create Date: 2026-07-23 23:56:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "004_create_issue_scores_table"
down_revision: str | None = "003_create_sync_tables"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "issue_scores",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("issue_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("score", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column(
            "recommendation",
            sa.String(length=50),
            nullable=False,
            server_default="Investigate",
        ),
        sa.Column("rule_breakdown", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["issue_id"], ["issues.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("issue_id"),
    )
    op.create_index(op.f("ix_issue_scores_issue_id"), "issue_scores", ["issue_id"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_issue_scores_issue_id"), table_name="issue_scores")
    op.drop_table("issue_scores")

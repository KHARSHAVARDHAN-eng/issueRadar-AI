"""create issue analyses table

Revision ID: 005_create_issue_analyses_table
Revises: 004_create_issue_scores_table
Create Date: 2026-07-24 00:01:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "005_create_issue_analyses_table"
down_revision: str | None = "004_create_issue_scores_table"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "issue_analyses",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("issue_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column(
            "difficulty",
            sa.String(length=50),
            nullable=False,
            server_default="intermediate",
        ),
        sa.Column(
            "estimated_time_minutes",
            sa.Integer(),
            nullable=False,
            server_default="60",
        ),
        sa.Column(
            "risk",
            sa.String(length=50),
            nullable=False,
            server_default="medium",
        ),
        sa.Column(
            "component",
            sa.String(length=255),
            nullable=False,
            server_default="Core Logic",
        ),
        sa.Column("languages", sa.JSON(), nullable=False),
        sa.Column("likely_files", sa.JSON(), nullable=False),
        sa.Column(
            "merge_probability",
            sa.Float(),
            nullable=False,
            server_default="0.8",
        ),
        sa.Column(
            "ai_confidence",
            sa.Float(),
            nullable=False,
            server_default="0.85",
        ),
        sa.Column(
            "model_name",
            sa.String(length=100),
            nullable=False,
            server_default="mock-llm-v1",
        ),
        sa.Column(
            "analysis_version",
            sa.String(length=50),
            nullable=False,
            server_default="1.0",
        ),
        sa.Column("analyzed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["issue_id"], ["issues.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("issue_id"),
    )
    op.create_index(
        op.f("ix_issue_analyses_issue_id"),
        "issue_analyses",
        ["issue_id"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_issue_analyses_issue_id"),
        table_name="issue_analyses",
    )
    op.drop_table("issue_analyses")

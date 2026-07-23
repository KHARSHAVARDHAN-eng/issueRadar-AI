"""extend issue analysis table for AI coach

Revision ID: 006_extend_issue_analysis_table
Revises: 005_create_issue_analyses_table
Create Date: 2026-07-24 00:48:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "006_extend_issue_analysis_table"
down_revision: str | None = "005_create_issue_analyses_table"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "issue_analyses",
        sa.Column(
            "problem_explanation",
            sa.Text(),
            nullable=False,
            server_default="Summary of the issue problem.",
        ),
    )
    op.add_column(
        "issue_analyses",
        sa.Column("implementation_plan", sa.JSON(), nullable=False, server_default="[]"),
    )
    op.add_column(
        "issue_analyses",
        sa.Column("required_knowledge", sa.JSON(), nullable=False, server_default="[]"),
    )
    op.add_column(
        "issue_analyses",
        sa.Column("prerequisites", sa.JSON(), nullable=False, server_default="[]"),
    )
    op.add_column(
        "issue_analyses",
        sa.Column("acceptance_criteria", sa.JSON(), nullable=False, server_default="[]"),
    )
    op.add_column(
        "issue_analyses",
        sa.Column(
            "testing_strategy",
            sa.Text(),
            nullable=False,
            server_default="Run existing unit tests.",
        ),
    )
    op.add_column(
        "issue_analyses",
        sa.Column("possible_challenges", sa.JSON(), nullable=False, server_default="[]"),
    )
    op.add_column(
        "issue_analyses",
        sa.Column(
            "estimated_learning_time",
            sa.Integer(),
            nullable=False,
            server_default="15",
        ),
    )
    op.add_column(
        "issue_analyses",
        sa.Column(
            "confidence_reasoning",
            sa.Text(),
            nullable=False,
            server_default="High confidence based on issue title and labels.",
        ),
    )


def downgrade() -> None:
    op.drop_column("issue_analyses", "confidence_reasoning")
    op.drop_column("issue_analyses", "estimated_learning_time")
    op.drop_column("issue_analyses", "possible_challenges")
    op.drop_column("issue_analyses", "testing_strategy")
    op.drop_column("issue_analyses", "acceptance_criteria")
    op.drop_column("issue_analyses", "prerequisites")
    op.drop_column("issue_analyses", "required_knowledge")
    op.drop_column("issue_analyses", "implementation_plan")
    op.drop_column("issue_analyses", "problem_explanation")

"""create sync tables and columns

Revision ID: 003_create_sync_tables
Revises: 002_create_repositories_table
Create Date: 2026-07-23 23:49:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "003_create_sync_tables"
down_revision: str | None = "002_create_repositories_table"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. Add sync tracking columns to repositories
    op.add_column(
        "repositories",
        sa.Column("last_sync_started_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "repositories",
        sa.Column("last_sync_completed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "repositories",
        sa.Column(
            "sync_status",
            sa.String(length=50),
            nullable=False,
            server_default="idle",
        ),
    )
    op.add_column("repositories", sa.Column("sync_error", sa.Text(), nullable=True))
    op.add_column(
        "repositories",
        sa.Column("open_issues_count", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column(
        "repositories",
        sa.Column(
            "closed_issues_count",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
    )
    op.add_column(
        "repositories",
        sa.Column(
            "total_issues_count",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
    )

    # 2. Create labels table
    op.create_table(
        "labels",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("github_id", sa.BigInteger(), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("color", sa.String(length=50), nullable=False, server_default="888888"),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("repository_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(["repository_id"], ["repositories.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("repository_id", "name", name="uq_repo_label_name"),
    )
    op.create_index(op.f("ix_labels_github_id"), "labels", ["github_id"], unique=False)
    op.create_index(op.f("ix_labels_name"), "labels", ["name"], unique=False)
    op.create_index(op.f("ix_labels_repository_id"), "labels", ["repository_id"], unique=False)

    # 3. Create issues table
    op.create_table(
        "issues",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("github_id", sa.BigInteger(), nullable=False),
        sa.Column("number", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=1024), nullable=False),
        sa.Column("body", sa.Text(), nullable=True),
        sa.Column("state", sa.String(length=50), nullable=False, server_default="open"),
        sa.Column("author_username", sa.String(length=255), nullable=True),
        sa.Column("author_avatar_url", sa.String(length=1024), nullable=True),
        sa.Column("html_url", sa.String(length=1024), nullable=False),
        sa.Column("comments_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_pull_request", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("repository_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("github_created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("github_updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("github_closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["repository_id"], ["repositories.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("repository_id", "github_id", name="uq_repo_github_issue"),
    )
    op.create_index(op.f("ix_issues_github_id"), "issues", ["github_id"], unique=False)
    op.create_index(op.f("ix_issues_number"), "issues", ["number"], unique=False)
    op.create_index(op.f("ix_issues_repository_id"), "issues", ["repository_id"], unique=False)
    op.create_index(op.f("ix_issues_state"), "issues", ["state"], unique=False)

    # 4. Create issue_labels association table
    op.create_table(
        "issue_labels",
        sa.Column("issue_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("label_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(["issue_id"], ["issues.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["label_id"], ["labels.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("issue_id", "label_id"),
    )

    # 5. Create comments table
    op.create_table(
        "comments",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("github_id", sa.BigInteger(), nullable=False),
        sa.Column("issue_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("author_username", sa.String(length=255), nullable=True),
        sa.Column("author_avatar_url", sa.String(length=1024), nullable=True),
        sa.Column("github_created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["issue_id"], ["issues.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("github_id"),
    )
    op.create_index(op.f("ix_comments_github_id"), "comments", ["github_id"], unique=True)
    op.create_index(op.f("ix_comments_issue_id"), "comments", ["issue_id"], unique=False)


def downgrade() -> None:
    op.drop_table("comments")
    op.drop_table("issue_labels")
    op.drop_table("issues")
    op.drop_table("labels")
    op.drop_column("repositories", "total_issues_count")
    op.drop_column("repositories", "closed_issues_count")
    op.drop_column("repositories", "open_issues_count")
    op.drop_column("repositories", "sync_error")
    op.drop_column("repositories", "sync_status")
    op.drop_column("repositories", "last_sync_completed_at")
    op.drop_column("repositories", "last_sync_started_at")

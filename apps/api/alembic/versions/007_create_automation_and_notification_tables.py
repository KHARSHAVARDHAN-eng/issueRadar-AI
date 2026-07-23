"""create automation and notification tables

Revision ID: 007_create_automation_and_notification_tables
Revises: 006_extend_issue_analysis_table
Create Date: 2026-07-24 00:52:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "007_create_automation_and_notification_tables"
down_revision: str | None = "006_extend_issue_analysis_table"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. saved_searches table
    op.create_table(
        "saved_searches",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("search_query", sa.String(length=500), nullable=True),
        sa.Column("filters_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_saved_searches_user_id"),
        "saved_searches",
        ["user_id"],
        unique=False,
    )

    # 2. bookmarks table
    op.create_table(
        "bookmarks",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("issue_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["issue_id"], ["issues.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "issue_id", name="uq_user_issue_bookmark"),
    )
    op.create_index(op.f("ix_bookmarks_issue_id"), "bookmarks", ["issue_id"], unique=False)
    op.create_index(op.f("ix_bookmarks_user_id"), "bookmarks", ["user_id"], unique=False)

    # 3. notifications table
    op.create_table(
        "notifications",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("issue_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("saved_search_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "type",
            sa.String(length=50),
            nullable=False,
            server_default="new_matching_issue",
        ),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("is_read", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["issue_id"], ["issues.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["saved_search_id"], ["saved_searches.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_notifications_user_id"), "notifications", ["user_id"], unique=False)

    # 4. sync_jobs table
    op.create_table(
        "sync_jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("repository_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="queued"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("issues_processed", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("errors", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["repository_id"], ["repositories.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_sync_jobs_repository_id"), "sync_jobs", ["repository_id"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_sync_jobs_repository_id"), table_name="sync_jobs")
    op.drop_table("sync_jobs")
    op.drop_index(op.f("ix_notifications_user_id"), table_name="notifications")
    op.drop_table("notifications")
    op.drop_index(op.f("ix_bookmarks_user_id"), table_name="bookmarks")
    op.drop_index(op.f("ix_bookmarks_issue_id"), table_name="bookmarks")
    op.drop_table("bookmarks")
    op.drop_index(op.f("ix_saved_searches_user_id"), table_name="saved_searches")
    op.drop_table("saved_searches")

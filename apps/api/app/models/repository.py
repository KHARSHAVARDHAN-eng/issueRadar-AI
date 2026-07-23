import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class Repository(Base):
    __tablename__ = "repositories"
    __table_args__ = (UniqueConstraint("added_by_id", "github_id", name="uq_user_github_repo"),)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    github_id: Mapped[int] = mapped_column(
        BigInteger,
        index=True,
        nullable=False,
    )
    owner: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    full_name: Mapped[str] = mapped_column(
        String(512),
        index=True,
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    language: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    default_branch: Mapped[str] = mapped_column(
        String(100),
        default="main",
        nullable=False,
    )
    stars: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    forks: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    private: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    added_by_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    # Sync Tracking Fields
    last_sync_started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    last_sync_completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    sync_status: Mapped[str] = mapped_column(
        String(50),
        default="idle",
        nullable=False,
    )  # idle | pending | syncing | completed | failed
    sync_error: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    open_issues_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    closed_issues_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    total_issues_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    added_by = relationship("User", backref="repositories", lazy="selectin")
    issues = relationship("Issue", back_populates="repository", cascade="all, delete-orphan")
    labels = relationship("Label", back_populates="repository", cascade="all, delete-orphan")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<Repository id={self.id} full_name={self.full_name} status={self.sync_status}>"

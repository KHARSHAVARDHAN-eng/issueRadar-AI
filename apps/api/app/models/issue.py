import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base

issue_labels = Table(
    "issue_labels",
    Base.metadata,
    Column(
        "issue_id",
        UUID(as_uuid=True),
        ForeignKey("issues.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "label_id",
        UUID(as_uuid=True),
        ForeignKey("labels.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Label(Base):
    __tablename__ = "labels"
    __table_args__ = (UniqueConstraint("repository_id", "name", name="uq_repo_label_name"),)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    github_id: Mapped[int | None] = mapped_column(
        BigInteger,
        index=True,
        nullable=True,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        index=True,
        nullable=False,
    )
    color: Mapped[str] = mapped_column(
        String(50),
        default="888888",
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    repository_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("repositories.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    repository = relationship("Repository", back_populates="labels")

    def __repr__(self) -> str:
        return f"<Label id={self.id} name={self.name}>"


class Issue(Base):
    __tablename__ = "issues"
    __table_args__ = (UniqueConstraint("repository_id", "github_id", name="uq_repo_github_issue"),)

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
    number: Mapped[int] = mapped_column(
        Integer,
        index=True,
        nullable=False,
    )
    title: Mapped[str] = mapped_column(
        String(1024),
        nullable=False,
    )
    body: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    state: Mapped[str] = mapped_column(
        String(50),
        default="open",
        index=True,
        nullable=False,
    )  # open | closed
    author_username: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    author_avatar_url: Mapped[str | None] = mapped_column(
        String(1024),
        nullable=True,
    )
    html_url: Mapped[str] = mapped_column(
        String(1024),
        nullable=False,
    )
    comments_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    is_pull_request: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    repository_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("repositories.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    github_created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    github_updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    github_closed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

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

    repository = relationship("Repository", back_populates="issues", lazy="selectin")
    labels = relationship("Label", secondary=issue_labels, backref="issues", lazy="selectin")
    comments = relationship(
        "Comment",
        back_populates="issue",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    score = relationship(
        "IssueScore",
        back_populates="issue",
        uselist=False,
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    analysis = relationship(
        "IssueAnalysis",
        back_populates="issue",
        uselist=False,
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Issue id={self.id} number=#{self.number} title={self.title[:20]}>"


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    github_id: Mapped[int] = mapped_column(
        BigInteger,
        index=True,
        unique=True,
        nullable=False,
    )
    issue_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("issues.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    body: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    author_username: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    author_avatar_url: Mapped[str | None] = mapped_column(
        String(1024),
        nullable=True,
    )
    github_created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    issue = relationship("Issue", back_populates="comments")

    def __repr__(self) -> str:
        return f"<Comment id={self.id} github_id={self.github_id}>"

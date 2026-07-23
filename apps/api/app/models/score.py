import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class IssueScore(Base):
    __tablename__ = "issue_scores"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    issue_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("issues.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
    )
    score: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )
    recommendation: Mapped[str] = mapped_column(
        String(50),
        default="Investigate",
        nullable=False,
    )  # Implement | Investigate | Skip
    rule_breakdown: Mapped[dict] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
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

    issue = relationship("Issue", back_populates="score")

    def __repr__(self) -> str:
        return f"<IssueScore issue_id={self.issue_id} score={self.score} rec={self.recommendation}>"

import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class IssueAnalysis(Base):
    __tablename__ = "issue_analyses"

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
    summary: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    difficulty: Mapped[str] = mapped_column(
        String(50),
        default="intermediate",
        nullable=False,
    )  # beginner | intermediate | advanced
    estimated_time_minutes: Mapped[int] = mapped_column(
        Integer,
        default=60,
        nullable=False,
    )
    risk: Mapped[str] = mapped_column(
        String(50),
        default="medium",
        nullable=False,
    )  # low | medium | high
    component: Mapped[str] = mapped_column(
        String(255),
        default="Core Logic",
        nullable=False,
    )
    languages: Mapped[list] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )
    likely_files: Mapped[list] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )
    merge_probability: Mapped[float] = mapped_column(
        Float,
        default=0.8,
        nullable=False,
    )
    ai_confidence: Mapped[float] = mapped_column(
        Float,
        default=0.85,
        nullable=False,
    )
    model_name: Mapped[str] = mapped_column(
        String(100),
        default="mock-llm-v1",
        nullable=False,
    )
    analysis_version: Mapped[str] = mapped_column(
        String(50),
        default="1.0",
        nullable=False,
    )
    analyzed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # --- Milestone 8: AI Issue Coach Extensions ---
    problem_explanation: Mapped[str] = mapped_column(
        Text,
        default="Summary of the issue problem.",
        nullable=False,
    )
    implementation_plan: Mapped[list] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )
    required_knowledge: Mapped[list] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )
    prerequisites: Mapped[list] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )
    acceptance_criteria: Mapped[list] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )
    testing_strategy: Mapped[str] = mapped_column(
        Text,
        default="Run existing pytest and unit tests.",
        nullable=False,
    )
    possible_challenges: Mapped[list] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )
    estimated_learning_time: Mapped[int] = mapped_column(
        Integer,
        default=15,
        nullable=False,
    )
    confidence_reasoning: Mapped[str] = mapped_column(
        Text,
        default="High confidence based on issue title and labels.",
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

    issue = relationship("Issue", back_populates="analysis")

    def __repr__(self) -> str:
        return (
            f"<IssueAnalysis issue_id={self.issue_id} "
            f"difficulty={self.difficulty} risk={self.risk}>"
        )

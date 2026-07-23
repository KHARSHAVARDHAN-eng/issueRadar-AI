import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class IssueAnalysisRead(BaseModel):
    id: uuid.UUID
    issue_id: uuid.UUID
    summary: str
    difficulty: str
    estimated_time_minutes: int
    risk: str
    component: str
    languages: list[str]
    likely_files: list[str]
    merge_probability: float
    ai_confidence: float
    model_name: str
    analysis_version: str
    analyzed_at: datetime

    # AI Coach Extensions
    problem_explanation: str
    implementation_plan: list[str]
    required_knowledge: list[str]
    prerequisites: list[str]
    acceptance_criteria: list[str]
    testing_strategy: str
    possible_challenges: list[str]
    estimated_learning_time: int
    confidence_reasoning: str

    model_config = ConfigDict(from_attributes=True)

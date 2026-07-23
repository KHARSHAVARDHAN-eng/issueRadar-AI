import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.analysis import IssueAnalysis


class IssueAnalysisRepository:
    """Persistence layer for IssueAnalysis entity."""

    async def upsert_analysis(
        self,
        db: AsyncSession,
        issue_id: uuid.UUID,
        summary: str,
        difficulty: str,
        estimated_time_minutes: int,
        risk: str,
        component: str,
        languages: list[str],
        likely_files: list[str],
        merge_probability: float,
        ai_confidence: float,
        model_name: str,
        analysis_version: str,
        problem_explanation: str = "Summary of the issue problem.",
        implementation_plan: list[str] | None = None,
        required_knowledge: list[str] | None = None,
        prerequisites: list[str] | None = None,
        acceptance_criteria: list[str] | None = None,
        testing_strategy: str = "Run existing unit tests.",
        possible_challenges: list[str] | None = None,
        estimated_learning_time: int = 15,
        confidence_reasoning: str = "High confidence based on issue title and labels.",
    ) -> IssueAnalysis:
        """Upsert single issue AI analysis record with AI Coach extensions."""
        result = await db.execute(select(IssueAnalysis).where(IssueAnalysis.issue_id == issue_id))
        obj = result.scalar_one_or_none()

        now = datetime.now(timezone.utc)
        plan = implementation_plan or []
        knowledge = required_knowledge or []
        prereqs = prerequisites or []
        criteria = acceptance_criteria or []
        challenges = possible_challenges or []

        if not obj:
            obj = IssueAnalysis(
                issue_id=issue_id,
                summary=summary,
                difficulty=difficulty,
                estimated_time_minutes=estimated_time_minutes,
                risk=risk,
                component=component,
                languages=languages,
                likely_files=likely_files,
                merge_probability=merge_probability,
                ai_confidence=ai_confidence,
                model_name=model_name,
                analysis_version=analysis_version,
                analyzed_at=now,
                problem_explanation=problem_explanation,
                implementation_plan=plan,
                required_knowledge=knowledge,
                prerequisites=prereqs,
                acceptance_criteria=criteria,
                testing_strategy=testing_strategy,
                possible_challenges=challenges,
                estimated_learning_time=estimated_learning_time,
                confidence_reasoning=confidence_reasoning,
            )
            db.add(obj)
        else:
            obj.summary = summary
            obj.difficulty = difficulty
            obj.estimated_time_minutes = estimated_time_minutes
            obj.risk = risk
            obj.component = component
            obj.languages = languages
            obj.likely_files = likely_files
            obj.merge_probability = merge_probability
            obj.ai_confidence = ai_confidence
            obj.model_name = model_name
            obj.analysis_version = analysis_version
            obj.analyzed_at = now
            obj.problem_explanation = problem_explanation
            obj.implementation_plan = plan
            obj.required_knowledge = knowledge
            obj.prerequisites = prereqs
            obj.acceptance_criteria = criteria
            obj.testing_strategy = testing_strategy
            obj.possible_challenges = challenges
            obj.estimated_learning_time = estimated_learning_time
            obj.confidence_reasoning = confidence_reasoning
            obj.updated_at = now

        await db.flush()
        return obj

    async def get_by_issue_id(self, db: AsyncSession, issue_id: uuid.UUID) -> IssueAnalysis | None:
        """Fetch AI analysis record by issue ID."""
        result = await db.execute(select(IssueAnalysis).where(IssueAnalysis.issue_id == issue_id))
        return result.scalar_one_or_none()


issue_analysis_repo = IssueAnalysisRepository()

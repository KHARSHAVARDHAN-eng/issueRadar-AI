import logging
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.analysis import IssueAnalysis
from app.models.issue import Issue
from app.repositories.analysis import issue_analysis_repo
from app.repositories.issue import issue_repo
from app.services.ai.base import BaseLLMProvider
from app.services.ai.factory import AIProviderFactory

logger = logging.getLogger(__name__)


class AIAnalysisService:
    """Service orchestrating AI Analysis & AI Issue Coach using pluggable AI Providers."""

    def __init__(self, provider: BaseLLMProvider | None = None):
        self.provider = provider

    def _get_active_provider(self) -> BaseLLMProvider:
        return self.provider or AIProviderFactory.get_provider()

    async def analyze_issue(
        self, db: AsyncSession, issue: Issue, retries: int = 2
    ) -> IssueAnalysis:
        """Run LLM analysis on issue context with retry support and persist result."""
        provider = self._get_active_provider()
        labels = [lbl.name for lbl in issue.labels] if issue.labels else []
        comments = [c.body for c in issue.comments] if issue.comments else []

        attempt = 0
        last_error = None
        while attempt <= retries:
            try:
                raw_data = await provider.analyze_issue(
                    title=issue.title,
                    body=issue.body or "",
                    labels=labels,
                    comments=comments,
                )

                # Validate and parse structured JSON fields
                summary = str(raw_data.get("summary", issue.title))
                difficulty = str(raw_data.get("difficulty", "intermediate"))
                estimated_time = int(raw_data.get("estimated_time_minutes", 60))
                risk = str(raw_data.get("risk", "medium"))
                component = str(raw_data.get("component", "Core Engine"))
                languages = list(raw_data.get("languages", ["Python"]))
                likely_files = list(raw_data.get("likely_files", []))
                merge_prob = float(raw_data.get("merge_probability", 0.8))
                confidence = float(raw_data.get("ai_confidence", 0.85))
                model_name = str(raw_data.get("model_name", "mock-llm-v1"))
                version = str(raw_data.get("analysis_version", "1.0"))

                # AI Coach Extensions
                problem_exp = str(
                    raw_data.get("problem_explanation", f"Fix issue '{issue.title}' in codebase.")
                )
                plan = list(
                    raw_data.get("implementation_plan", ["Inspect code", "Apply fix", "Run tests"])
                )
                knowledge = list(raw_data.get("required_knowledge", ["Python", "Git"]))
                prereqs = list(raw_data.get("prerequisites", ["Understand issue requirement"]))
                criteria = list(raw_data.get("acceptance_criteria", ["Issue resolved cleanly"]))
                testing = str(raw_data.get("testing_strategy", "Run pytest test suite."))
                challenges = list(raw_data.get("possible_challenges", ["Avoid regressions"]))
                learning_time = int(raw_data.get("estimated_learning_time", 15))
                confidence_reasoning = str(
                    raw_data.get("confidence_reasoning", "Confidence based on issue metadata.")
                )

                # Persist to database
                return await issue_analysis_repo.upsert_analysis(
                    db=db,
                    issue_id=issue.id,
                    summary=summary,
                    difficulty=difficulty,
                    estimated_time_minutes=estimated_time,
                    risk=risk,
                    component=component,
                    languages=languages,
                    likely_files=likely_files,
                    merge_probability=merge_prob,
                    ai_confidence=confidence,
                    model_name=model_name,
                    analysis_version=version,
                    problem_explanation=problem_exp,
                    implementation_plan=plan,
                    required_knowledge=knowledge,
                    prerequisites=prereqs,
                    acceptance_criteria=criteria,
                    testing_strategy=testing,
                    possible_challenges=challenges,
                    estimated_learning_time=learning_time,
                    confidence_reasoning=confidence_reasoning,
                )
            except Exception as e:
                attempt += 1
                last_error = e
                logger.warning(f"AI analysis attempt {attempt} failed for issue {issue.id}: {e}")

        raise RuntimeError(f"AI Analysis failed after {retries + 1} attempts: {last_error}")

    async def analyze_repository_issues(self, db: AsyncSession, repo_id: uuid.UUID) -> int:
        """Batch analyze all issues for a repository."""
        issues = await issue_repo.get_by_repository(db, repo_id, state="all")
        count = 0
        for issue in issues:
            await self.analyze_issue(db, issue)
            count += 1
        await db.commit()
        logger.info(f"Analyzed {count} issues with AI Coach for repository {repo_id}.")
        return count


ai_analysis_service = AIAnalysisService()

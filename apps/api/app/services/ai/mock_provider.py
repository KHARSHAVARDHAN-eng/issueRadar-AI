from typing import Any

from app.models.issue import Issue
from app.services.ai.base_provider import BaseLLMProvider


class MockLLMProvider(BaseLLMProvider):
    """Deterministic Mock LLM Provider for local development and testing."""

    @property
    def model_name(self) -> str:
        return "mock-gemini-pro-v1"

    async def analyze_issue(
        self,
        issue: Issue | None = None,
        title: str | None = None,
        body: str | None = None,
        labels: list[str] | None = None,
        comments: list[str] | None = None,
    ) -> dict[str, Any]:
        issue_title = issue.title if issue else (title or "Sample Issue")
        issue_body = issue.body if issue else (body or "")
        issue_number = issue.number if issue else 1

        title_lower = issue_title.lower()
        body_lower = (issue_body or "").lower()

        # Check labels from issue ORM or passed list
        label_names = []
        if issue and issue.labels:
            label_names = [lbl.name.lower() for lbl in issue.labels]
        elif labels:
            label_names = [str(lbl_item).lower() for lbl_item in labels]

        # Deterministic analysis calculation
        is_bug = any(
            kw in title_lower or kw in body_lower
            for kw in ["bug", "fix", "error", "fail", "crash", "timeout", "exception", "leak"]
        )

        has_beginner_label = any(
            lbl_item in label_names
            for lbl_item in ["good first issue", "easy", "beginner", "help wanted"]
        )

        if has_beginner_label or "beginner" in title_lower:
            difficulty = "beginner"
            est_minutes = 30
            risk = "low"
            comp = "Authentication Module"
            prob = 0.90
            knowledge = ["Python Asyncio", "SQLAlchemy ORM"]
            prereqs = ["Understand session timeout"]
            challenges = ["Maintaining token security"]
        elif is_bug:
            difficulty = "intermediate"
            est_minutes = 90
            risk = "medium"
            comp = "Core Backend"
            prob = 0.85
            knowledge = ["Python Asyncio", "SQLAlchemy ORM"]
            prereqs = ["Understand bug traceback", "Locate failing handler"]
            challenges = ["Edge cases in error propagation", "Race conditions in async tasks"]
        else:
            difficulty = "advanced"
            est_minutes = 120
            risk = "medium"
            comp = "Documentation & UI"
            prob = 0.75
            knowledge = ["Architecture Design"]
            prereqs = ["Check repository guidelines"]
            challenges = ["Maintaining clean code formatting"]

        return {
            "summary": f"Issue #{issue_number} involves {issue_title.strip()}.",
            "difficulty": difficulty,
            "estimated_time_minutes": est_minutes,
            "risk": risk,
            "component": comp,
            "languages": ["Python", "TypeScript"],
            "likely_files": [f"app/services/{comp.lower().replace(' ', '_')}.py"],
            "merge_probability": prob,
            "ai_confidence": 0.90,
            "model_name": self.model_name,
            "analysis_version": "1.0",
            # AI Coach fields
            "problem_explanation": (
                f"The issue reports '{issue_title}'. "
                "Resolving this requires reviewing recent changes."
            ),
            "implementation_plan": [
                f"Step 1: Reproduce issue #{issue_number} locally with tests.",
                "Step 2: Apply code modifications to address the root cause.",
                "Step 3: Run full pytest and lint suite before creating a pull request.",
            ],
            "required_knowledge": knowledge,
            "prerequisites": prereqs,
            "acceptance_criteria": [
                f"Issue #{issue_number} problem statement is resolved.",
                "All automated tests pass cleanly with zero regressions.",
            ],
            "testing_strategy": "Run unit tests covering modified paths and edge cases.",
            "possible_challenges": challenges,
            "estimated_learning_time": 15,
            "confidence_reasoning": (
                "High confidence based on clear issue descriptions and "
                "deterministic mock rule evaluation."
            ),
        }

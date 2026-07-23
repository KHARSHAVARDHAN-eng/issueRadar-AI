"""Prompt template for AI Issue Analysis and AI Issue Coach."""

ISSUE_ANALYSIS_PROMPT_TEMPLATE = (
    "You are a Lead Open Source Architect analyzing GitHub issue #{number} "
    "from repository '{repo_name}'.\n\n"
    "Issue Title: {title}\n"
    "Issue Description:\n"
    "{body}\n\n"
    "Issue Labels: {labels}\n"
    "Comments Count: {comment_count}\n\n"
    "Generate a comprehensive analysis and actionable open-source coaching guide in JSON.\n\n"
    "Return ONLY a valid JSON object matching the following structure:\n"
    "{\n"
    '  "summary": "<1-2 sentence technical summary>",\n'
    '  "difficulty": "<beginner|intermediate|advanced|expert>",\n'
    '  "estimated_time_minutes": <integer estimated minutes>,\n'
    '  "risk": "<low|medium|high>",\n'
    '  "component": "<subsystem or module name>",\n'
    '  "languages": ["<language1>", "<language2>"],\n'
    '  "likely_files": ["<filepath1>", "<filepath2>"],\n'
    '  "merge_probability": <float 0.0 to 1.0>,\n'
    '  "ai_confidence": <float 0.0 to 1.0>,\n'
    '  "problem_explanation": "<Plain English breakdown of what is wrong and why>",\n'
    '  "implementation_plan": [\n'
    '    "Step 1: Locate ...",\n'
    '    "Step 2: Modify ...",\n'
    '    "Step 3: Test ..."\n'
    "  ],\n"
    '  "required_knowledge": ["<Concept/Tech 1>", "<Concept/Tech 2>"],\n'
    '  "prerequisites": ["<Prerequisite 1>", "<Prerequisite 2>"],\n'
    '  "acceptance_criteria": ["<Criterion 1>", "<Criterion 2>"],\n'
    '  "testing_strategy": "<Detailed strategy to test and verify code changes>",\n'
    '  "possible_challenges": ["<Pitfall 1>", "<Pitfall 2>"],\n'
    '  "estimated_learning_time": <integer minutes needed to study background context>,\n'
    '  "confidence_reasoning": "<Explanation of confidence score '
    'based on issue clarity and scope>"\n'
    "}\n"
)

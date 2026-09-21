"""
Rule 5: Prove Your AI Skills (Demonstration vs. Skill Listing)
Key Findings (Jeff Su):
- Oxford Experiment: Adding role-relevant AI skills increased interview selection chance by up to 15 percentage points.
- 60% of hiring managers want candidates to PROVE their AI skills with real workflow projects, not just list "ChatGPT" in skills.
- 86% of hiring managers prioritize work experience over formal education.
"""
import re

BARE_AI_KEYWORDS = [
    "chatgpt", "gemini", "claude", "prompt engineering", "generative ai", "genai", "llms", "ai tools"
]

def audit_and_prove_ai_skills(resume_text: str) -> dict:
    resume_lower = resume_text.lower()
    bare_mentions = []
    for kw in BARE_AI_KEYWORDS:
        if re.search(rf"\b{re.escape(kw)}\b", resume_lower):
            bare_mentions.append(kw)

    # Check if AI skills are proven with real actions/links/metrics
    # e.g., "using Claude to ...", "automated with Gemini ... [link]"
    proven_ai_bullets = []
    lines = [l.strip() for l in resume_text.splitlines() if l.strip().startswith(("-", "*", "•", "1.", "2.", "3.", "4."))]
    for l in lines:
        l_lower = l.lower()
        if any(kw in l_lower for kw in BARE_AI_KEYWORDS):
            # check if it has a verb and metric or link
            has_action = any(v in l_lower for v in ["automated", "built", "engineered", "cut", "reduced", "scaled", "created", "deployed"])
            has_metric = bool(re.search(r"\d+[%|x|k|hrs|hours|mins|minutes]", l_lower))
            if has_action and has_metric:
                proven_ai_bullets.append(l)

    has_proven = len(proven_ai_bullets) > 0
    has_bare_only = (len(bare_mentions) > 0) and not has_proven

    score = 95 if has_proven else (60 if has_bare_only else 70)
    advice = ""
    if has_bare_only:
        advice = "You list AI keywords (e.g. 'ChatGPT') as static skills. 60% of hiring managers want demonstrated proof. Convert this into an achievement bullet with measurable time saved and an inspectable proof link."
    elif not has_proven and not bare_mentions:
        advice = "No modern AI workflow skills detected. Adding role-relevant AI experience provides up to a +15 percentage point interview lift (Oxford Study). Add an AI automation project."
    else:
        advice = f"Strong demonstration: Found {len(proven_ai_bullets)} AI-assisted workflow achievement(s) with quantified outcomes."

    examples = [
        "Cut sprint backlog triage from 4 hours to 45 minutes using Claude Code to automate issue categorization and acceptance criteria verification. [github.com/user/pm-skills]",
        "Automated customer bug replication workflows using Gemini Flash agents, slashing QA escalation turnaround by 65%.",
        "Engineered internal documentation vector retrieval agent using Ollama and Python, eliminating 8 hours/week of cross-team onboarding questions."
    ]

    return {
        "rule": "Rule 5: Prove Your AI Skills",
        "score": score,
        "has_proven_ai_skills": has_proven,
        "bare_mentions_found": bare_mentions,
        "proven_bullets_found": proven_ai_bullets,
        "advice": advice,
        "research_insight": "Oxford experiment: up to +15 percentage points higher interview selection when AI skills are demonstrated with evidence.",
        "recommended_templates": examples
    }

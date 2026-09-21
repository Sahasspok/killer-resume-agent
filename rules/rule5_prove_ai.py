"""
Rule 5: Prove Your AI Skills (Demonstration vs. Skill Listing)
Key Findings (Jeff Su):
- Oxford Experiment: Adding role-relevant AI skills increased interview selection chance by up to 15 percentage points.
- 60% of hiring managers want candidates to PROVE their AI skills with real workflow projects, not just list "ChatGPT" in skills.
- 86% of hiring managers prioritize work experience over formal education.
"""
import re

BARE_AI_KEYWORDS = [
    "chatgpt", "gemini", "claude", "copilot", "prompt engineering", "generative ai",
    "genai", "llms", "llm", "ai tools", "ai-powered", "ai agents", "machine learning"
]

AI_ACTION_VERBS = [
    "automated", "built", "engineered", "cut", "reduced", "scaled", "created",
    "deployed", "drove", "delivered", "launched", "implemented", "integrated",
    "designed", "led", "developed", "orchestrated"
]

def audit_and_prove_ai_skills(resume_text: str) -> dict:
    resume_lower = resume_text.lower()
    bare_mentions = []
    for kw in BARE_AI_KEYWORDS:
        if re.search(rf"\b{re.escape(kw)}\b", resume_lower):
            bare_mentions.append(kw)

    # Check for verified AI certifications (e.g. 'Introduction to generative AI', Google/Coursera/DeepLearning)
    has_ai_certification = False
    for cert_pattern in [r"certifi[a-z]*:?.*(?:generative ai|machine learning|deep learning|llm|artificial intelligence)",
                         r"introduction to generative ai",
                         r"deeplearning\.ai", r"aws machine learning", r"google ai"]:
        if re.search(cert_pattern, resume_lower):
            has_ai_certification = True
            break

    # Check if AI skills are proven with real actions, metrics, or product outcomes
    proven_ai_bullets = []
    lines = [l.strip() for l in resume_text.splitlines() if l.strip().startswith(("-", "*", "•", "1.", "2.", "3.", "4.", "5.", "6.", "7.", "8."))]
    for l in lines:
        l_lower = l.lower()
        if any(kw in l_lower for kw in BARE_AI_KEYWORDS):
            has_action = any(v in l_lower for v in AI_ACTION_VERBS)
            has_outcome_or_metric = bool(re.search(r"(?:\d+[%|x|k|hrs|hours|mins|minutes|story\s+points|days]|mvp|production|enterprise|launch|resolution|velocity|pipeline|http|github)", l_lower))
            if has_action and has_outcome_or_metric:
                proven_ai_bullets.append(l)

    has_proven = len(proven_ai_bullets) > 0
    has_bare_only = (len(bare_mentions) > 0) and not has_proven and not has_ai_certification

    if has_proven:
        score = 100 if has_ai_certification else 95
        advice = f"Strong demonstration: Found {len(proven_ai_bullets)} AI-assisted workflow achievement(s) with quantified outcomes."
    elif has_ai_certification:
        score = 85
        advice = "Recognized formal AI certification detected. Anchor this with an achievement bullet demonstrating daily workflow application to reach 95+ score."
    elif has_bare_only:
        score = 75
        advice = "You list AI keywords (e.g. 'ChatGPT' or 'Generative AI') as static skills. 60% of hiring managers want demonstrated proof. Convert this into an achievement bullet with measurable time saved or product delivery."
    else:
        score = 65
        advice = "No modern AI workflow skills detected. Adding role-relevant AI experience provides up to a +15 percentage point interview lift (Oxford Study). Add an AI automation project or certification."

    examples = [
        "Cut sprint backlog triage from 4 hours to 45 minutes using Claude Code to automate issue categorization and acceptance criteria verification. [github.com/user/pm-skills]",
        "Automated customer bug replication workflows using Gemini Flash agents, slashing QA escalation turnaround by 65%.",
        "Drove delivery of innovative AI-powered mobile and web features across Global MVP, scaling velocity by 50% and cutting defect turnaround to under 24 hours."
    ]

    return {
        "rule": "Rule 5: Prove Your AI Skills",
        "score": score,
        "has_proven_ai_skills": has_proven or has_ai_certification,
        "has_ai_certification": has_ai_certification,
        "bare_mentions_found": bare_mentions,
        "proven_bullets_found": proven_ai_bullets,
        "advice": advice,
        "research_insight": "Oxford experiment: up to +15 percentage points higher interview selection when AI skills are demonstrated with evidence.",
        "recommended_templates": examples
    }

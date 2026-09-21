"""
Rule 5: Prove Your AI Skills (Demonstration vs. Skill Listing)
Key Findings (Jeff Su):
- Oxford Experiment: Adding role-relevant AI skills increased interview selection chance by up to 15 percentage points.
- 60% of hiring managers want candidates to PROVE their AI skills with real workflow projects, not just list "ChatGPT" in skills.
- 86% of hiring managers prioritize work experience over formal education.
"""
import re

WORKFLOW_AI_TOOLS = [
    "chatgpt", "gemini", "claude", "copilot", "github copilot", "cursor",
    "prompt engineering", "notion ai", "perplexity", "midjourney", "v0",
    "otter.ai", "langchain", "llamaindex", "ollama"
]

PRODUCT_AI_PHRASES = [
    r"\bai-powered\s+(?:[a-z0-9\-]+\s+)?(?:mobile|web|platform|product|app|experience|startup|saas|tool|solution|company)\b",
    r"\bai\s+(?:platform|startup|company|product|solution|business)\b",
    r"\buser\s+generated\s+content.*ai\b"
]

AI_AUTOMATION_VERBS = [
    "automate", "automated", "automating", "built", "build", "engineered", "engineer",
    "cut", "cutting", "reduced", "reduce", "reducing", "scaled", "scale", "created",
    "create", "deployed", "deploy", "accelerated", "accelerate", "streamlined", "streamline",
    "triaged", "triage", "generated", "generate", "drafted", "draft", "analyzed", "analyze",
    "synthesized", "synthesize", "instituted", "leveraged", "leverage", "utilized", "utilize",
    "used", "using", "integrated", "integrate", "applied", "apply", "saving", "saved"
]

def audit_and_prove_ai_skills(resume_text: str) -> dict:
    """
    Jeff Su Rule 5: Prove Your AI Skills.
    Profession-agnostic check:
    1. Is AI used as a personal workflow skill (not just company product/industry descriptor)?
    2. Are AI certifications tied to demonstrable work outcomes?
    3. Are specific AI tools named in the daily workflow?
    4. Is there at least one AI-augmented achievement bullet (Action + Tool + Outcome)?
    """
    resume_lower = resume_text.lower()
    issues = []
    strengths = []

    # 1. Check for specific workflow AI tools named
    tools_found = [t for t in WORKFLOW_AI_TOOLS if re.search(rf"\b{re.escape(t)}\b", resume_lower)]
    
    # 2. Check for verified formal AI certifications
    has_ai_certification = False
    for cert_pattern in [r"certifi[a-z]*:?.*(?:generative ai|machine learning|deep learning|llm|artificial intelligence)",
                         r"introduction to generative ai",
                         r"deeplearning\.ai", r"aws machine learning", r"google ai"]:
        if re.search(cert_pattern, resume_lower):
            has_ai_certification = True
            break

    # 3. Check for product-only AI mentions
    is_product_only_mention = any(re.search(p, resume_lower) for p in PRODUCT_AI_PHRASES)

    # 4. Check for genuine AI-augmented achievement bullets
    # Universal formula: Used [AI Tool] to [Action], saving [Y hours/week or Z%]
    proven_ai_bullets = []
    lines = [l.strip() for l in resume_text.splitlines() if l.strip().startswith(("-", "*", "•", "1.", "2.", "3.", "4.", "5.", "6.", "7.", "8."))]
    for l in lines:
        l_lower = l.lower()
        has_tool = any(t in l_lower for t in WORKFLOW_AI_TOOLS) or bool(re.search(r'\b(?:ai|llm|generative\s+ai|ai-assisted|ai-powered|prompt\s+engineering)\b', l_lower))
        if has_tool:
            has_action = any(v in l_lower for v in AI_AUTOMATION_VERBS)
            has_metric = bool(re.search(r"(?:\d+[%|x|k|hrs|hours|mins|minutes|story\s+points|days]|saving|reduced|cutting|slashing|turnaround)", l_lower))
            # Ensure it is about candidate's workflow, not just describing the product features
            not_just_product_desc = not ("platform, i drive the delivery" in l_lower or "powered mobile and web experiences" in l_lower and not has_metric)
            if has_action and has_metric and not_just_product_desc:
                proven_ai_bullets.append(l)

    has_proven = len(proven_ai_bullets) > 0

    # Diagnostic Flags
    # Flag A: AI mentioned only as product/industry descriptor
    if is_product_only_mention and not has_proven and not (tools_found and len(tools_found) > 1):
        issues.append({
            "code": "AI_PRODUCT_ONLY_NOT_WORKFLOW_SKILL",
            "message": "'AI' appears only as an employer/product description (e.g. 'AI-powered platform'), not a personal workflow skill. Managing an AI product does not prove you use AI to accelerate your own work.",
            "fix": "Specify personal AI tool usage in your daily workflow (e.g. 'Used Claude/ChatGPT to draft acceptance criteria, cutting sprint backlog triage by 3 hours weekly')."
        })

    # Flag B: AI certification without outcome
    if has_ai_certification and not has_proven:
        issues.append({
            "code": "AI_CERTIFICATION_WITHOUT_OUTCOME",
            "message": "AI certification is listed as static education without a corresponding project outcome or measured efficiency gain. Rule 5 requires practical application, not just coursework.",
            "fix": "Tie the certification to an experience bullet demonstrating daily workflow application and time saved."
        })

    # Flag C: No AI tools named in workflow
    if len(tools_found) == 0:
        issues.append({
            "code": "NO_AI_TOOLS_IN_WORKFLOW",
            "message": "No daily AI productivity tools (e.g. ChatGPT, Claude, GitHub Copilot, Cursor, Notion AI) are named in your tool stack. 60%+ of hiring managers expect modern professionals to name their AI tool stack.",
            "fix": "Add an 'AI & Automation Tools' category in your Skills section naming 2-3 tools you use daily."
        })
    else:
        strengths.append(f"AI tools identified in workflow: {', '.join(tools_found[:4])}.")

    # Flag D: No AI-augmented achievement bullet
    if not has_proven:
        issues.append({
            "code": "NO_AI_AUGMENTED_ACHIEVEMENT_BULLET",
            "message": "No bullet demonstrating AI-augmented workflow automation (e.g. 'Used AI to automate X, saving Y hours/week'). This is the single clearest Rule 5 differentiator across all professions.",
            "fix": "Add a high-impact achievement bullet: 'Leveraged [Claude/ChatGPT] to [automate task], cutting turnaround from [X] to [Y] hours.'"
        })
    else:
        strengths.append(f"Found {len(proven_ai_bullets)} demonstrated AI-augmented achievement(s) with quantified outcomes.")

    # Calculate calibrated score
    if has_proven and len(tools_found) > 0 and has_ai_certification:
        score = 100
        advice = f"Strong demonstration: Verified AI credentials, active workflow tools ({', '.join(tools_found[:3])}), and {len(proven_ai_bullets)} quantified automation bullet(s)."
    elif has_proven and len(tools_found) > 0:
        score = 95
        advice = f"Strong demonstration: Named workflow tools and {len(proven_ai_bullets)} AI-augmented achievement(s)."
    elif has_ai_certification and len(tools_found) > 0:
        score = 85
        advice = "Recognized AI credential and tools listed. Add a concrete achievement bullet showing hours saved to reach 95+ score."
    elif has_ai_certification:
        score = 75
        advice = "Static AI certification listed without workflow outcome. Anchor to a daily automation bullet."
    elif len(tools_found) > 0:
        score = 75
        advice = "AI tools listed as static skills. Convert into an achievement bullet with measurable time saved."
    elif is_product_only_mention:
        score = 65
        advice = "AI mentioned only as a product/industry descriptor. Demonstrate personal workflow adoption."
    else:
        score = 60
        advice = "No modern AI workflow skills detected. Adding role-relevant AI experience provides up to a +15 percentage point interview lift (Oxford Study)."

    examples = [
        "Automated sprint backlog triage and user story refinement using Claude Code, cutting weekly PM overhead from 4 hours to 45 minutes.",
        "Engineered customer bug replication workflows using Gemini Flash agents, slashing QA escalation turnaround by 65%.",
        "Leveraged ChatGPT to draft curriculum lesson plans and student rubrics, reducing weekly administrative prep by 5 hours."
    ]

    return {
        "rule": "Rule 5: Prove Your AI Skills",
        "score": score,
        "has_proven_ai_skills": has_proven,
        "has_ai_certification": has_ai_certification,
        "tools_found": tools_found,
        "proven_bullets_found": proven_ai_bullets,
        "issues": issues,
        "strengths": strengths,
        "advice": advice,
        "research_insight": "Oxford experiment: up to +15 percentage points higher interview selection when AI skills are demonstrated with evidence.",
        "recommended_templates": examples
    }

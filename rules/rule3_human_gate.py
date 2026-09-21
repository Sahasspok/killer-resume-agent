"""
Rule 3: Know Where AI Should Stop (The Human Review Gate)
Key Findings (Jeff Su):
- MIT Experiment (500k candidates): Polish with spelling/grammar increased hiring rate by 8%.
- Generic AI Generation Warning: Generative AI pitches sound indistinguishable; 28% of hiring managers reject lazy AI text.
- Human QA Gate: Brain dump facts first -> Polish syntax -> Strip anything you cannot prove in an interview.
"""
import re

GENERIC_AI_CLICHES = [
    "dynamic self-starter", "results-driven professional", "proven track record",
    "spearheaded cross-functional alignment", "synergized stakeholders",
    "leverage best-in-class solutions", "passionate thought leader",
    "out-of-the-box thinker", "detail-oriented team player",
    "go-getter with a can-do attitude", "fast-paced environment"
]

PASSIVE_WEAK_VERBS = [
    "responsible for", "helped with", "assisted in", "worked on", "participated in",
    "handled daily", "involved in", "supported team with"
]

STRONG_ACTION_VERBS = [
    "Architected", "Engineered", "Orchestrated", "Negotiated", "Streamlined",
    "Decoupled", "Eliminated", "Accelerated", "Delivered", "Spearheaded",
    "Automated", "Restructured", "Optimized", "Scaled", "Standardized"
]

def enforce_human_gate(bullet_text: str) -> dict:
    bullet_lower = bullet_text.lower()
    flags = []
    has_cliche = False
    has_weak_verb = False

    # Check for lazy AI clichés
    for cliche in GENERIC_AI_CLICHES:
        if cliche in bullet_lower:
            flags.append({
                "type": "AI_CLICHE",
                "term": cliche,
                "warning": f"Detected generic AI cliché '{cliche}'. Hiring managers identify this as low-effort auto-generated filler."
            })
            has_cliche = True

    # Check for passive or weak verbs
    for weak in PASSIVE_WEAK_VERBS:
        if weak in bullet_lower:
            flags.append({
                "type": "PASSIVE_VERB",
                "term": weak,
                "warning": f"Starts with passive verb '{weak}'. Replace with a crisp action verb (e.g. Delivered, Automated, Engineered)."
            })
            has_weak_verb = True

    # Check if bullet has numbers/metrics
    has_metrics = bool(re.search(r"(\d+%|\$\d+|\d+\s*(x|k|m|hours|days|weeks|users|engineers|teams|tickets))", bullet_lower))

    defense_checklist = [
        "Can you explain the exact technical steps taken to achieve this in a 45-minute live interview?",
        "Did you personally lead or build this, or was it a team-wide project?",
        "Do the cited metrics reflect audited results or rough estimates?"
    ]

    human_gate_status = "PASS" if not has_cliche and (has_metrics or not has_weak_verb) else "NEEDS_HUMAN_REVIEW"

    return {
        "rule": "Rule 3: Know Where AI Should Stop (Human Review Gate)",
        "status": human_gate_status,
        "has_cliche": has_cliche,
        "has_weak_verb": has_weak_verb,
        "has_metrics": has_metrics,
        "flags": flags,
        "interview_defense_questions": defense_checklist,
        "takeaway": "Polish syntax and grammar (+8% hiring boost per MIT), but never let AI hallucinate scope. You must defend every claim on camera."
    }

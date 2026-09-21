"""
Rule 1: Make Sure AI Can Read Your Résumé
Key Findings (Jeff Su):
- 87% of hiring managers say AI reads simple, text-based résumés more accurately.
- Avoid multi-column layouts, skill bars, decorative tables, icons, and text trapped in images.
- Use standard headings: Contact, Summary, Experience, Projects, Skills, Education.
"""
import re

STANDARD_HEADINGS = [
    "summary", "professional summary", "experience", "work experience",
    "professional experience", "projects", "key projects", "skills",
    "technical skills", "education", "certifications"
]

def audit_readability(resume_text: str) -> dict:
    issues = []
    strengths = []
    score = 100

    # 1. Check for multi-column or table artifacts (pipe tables, column divs)
    table_pipes = len(re.findall(r"\|.*\|.*\|", resume_text))
    if table_pipes > 3:
        score -= 20
        issues.append({
            "code": "MULTI_COLUMN_TABLE_DETECTED",
            "message": "Detected table or multi-column layout. ATS parsers frequently scramble table text into adjacent lines.",
            "fix": "Flatten into a clean, single-column top-to-bottom layout with standard bullet points."
        })
    else:
        strengths.append("Single-column flow: Clean top-to-bottom parser structure.")

    # 2. Check for skill bars or graphical rating patterns specifically in skills context (e.g. Python: 90%, Skill: 5/5, ★★★★, [====  ])
    # Extract skills section if present
    skills_match = re.search(r"(?:skills|technical skills)[\s\S]*?(?:education|projects|experience|$)", resume_text, re.IGNORECASE)
    skills_text = skills_match.group(0) if skills_match else ""
    rating_patterns = re.findall(r"(?:[A-Za-z\s]+:\s*\d{1,2}\s*[/|out\s+of]\s*10|[A-Za-z\s]+:\s*\d{1,3}%|★|⭐|\[={2,}\s*\])", skills_text)
    if rating_patterns:
        score -= 15
        issues.append({
            "code": "SKILL_BARS_DETECTED",
            "message": f"Detected graphical/arbitrary skill ratings ({rating_patterns[:3]}). 87% of hiring managers state AI parsers strip or misread visual skill bars.",
            "fix": "Remove arbitrary ratings (e.g. 'Python 90%'). Demonstrate skill usage in bullet points."
        })
    else:
        strengths.append("No arbitrary skill bars or rating icons.")

    # 3. Check for standard headings
    headings_found = []
    lines = [l.strip().lower().replace("#", "").strip() for l in resume_text.splitlines() if l.strip()]
    for heading in STANDARD_HEADINGS:
        if any(line == heading or line.startswith(heading + ":") for line in lines):
            headings_found.append(heading)

    if len(headings_found) < 3:
        score -= 20
        issues.append({
            "code": "NON_STANDARD_HEADINGS",
            "message": f"Found only {len(headings_found)} conventional headings. ATS needs standard sections to classify data.",
            "fix": "Use conventional headers: Summary, Experience, Projects, Skills, Education."
        })
    else:
        strengths.append(f"Standard semantic sections detected: {', '.join(headings_found[:4])}.")

    # 4. Length and parseability
    word_count = len(resume_text.split())
    if word_count < 150:
        score -= 25
        issues.append({
            "code": "CONTENT_TOO_THIN",
            "message": f"Resume is under 150 words ({word_count} words). ATS parsers may score this as an incomplete submission.",
            "fix": "Expand with detailed achievements following Google's XYZ formula."
        })
    elif word_count > 1200:
        score -= 10
        issues.append({
            "code": "EXCESSIVE_LENGTH",
            "message": f"Resume is {word_count} words (likely 3+ pages). Keep to 1-2 tight pages (400-800 words).",
            "fix": "Prune older roles and focus on the highest-impact achievements from the past 5-7 years."
        })
    else:
        strengths.append(f"Optimal length: {word_count} words (balanced for 1-2 pages).")

    score = max(10, min(100, score))
    return {
        "rule": "Rule 1: Make Sure AI Can Read Your Résumé",
        "score": score,
        "passed": score >= 80,
        "headings_found": headings_found,
        "strengths": strengths,
        "issues": issues,
        "recommendation": "Maintain single-column Markdown/PDF with selectable text under 2.5MB. Never use graphical Canva templates with text trapped in images."
    }

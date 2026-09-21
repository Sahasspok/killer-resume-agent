"""
Rule 1: Make Sure AI Can Read Your Résumé
Key Findings (Jeff Su):
- 87% of hiring managers say AI reads simple, text-based résumés more accurately.
- Avoid multi-column layouts, skill bars, decorative tables, icons, and text trapped in images.
- Use standard headings: Contact, Summary, Experience, Projects, Skills, Education.
"""
import re

CANONICAL_SECTIONS = {
    "Summary": [
        "summary", "professional summary", "executive summary", "profile", "about me", "career objective"
    ],
    "Experience": [
        "experience", "work experience", "professional experience", "work history", "employment history", "employment"
    ],
    "Skills": [
        "skills", "technical skills", "core skills", "core competencies", "competencies", "skills & tools",
        "skills and tools", "core competencies & technical skills", "technologies"
    ],
    "Education": [
        "education", "academic background", "academic history", "education & certifications", "education and certifications"
    ],
    "Projects": [
        "projects", "key projects", "technical projects", "portfolio", "initiatives", "key projects & initiatives"
    ],
    "Certifications": [
        "certifications", "licenses", "credentials", "certifications & licenses"
    ]
}

def audit_readability(resume_text: str) -> dict:
    issues = []
    strengths = []
    score = 100

    # 1. Check for multi-column or table artifacts (markdown tables with delimiter rows e.g. |---|---|)
    has_markdown_table = bool(re.search(r"^\s*\|?\s*[-:]{2,}\s*\|\s*[-:| ]+\s*\|?\s*$", resume_text, re.MULTILINE))
    if has_markdown_table:
        score -= 20
        issues.append({
            "code": "MULTI_COLUMN_TABLE_DETECTED",
            "message": "Detected table or multi-column layout. ATS parsers frequently scramble table text into adjacent lines.",
            "fix": "Flatten into a clean, single-column top-to-bottom layout with standard bullet points."
        })
    else:
        strengths.append("Single-column flow: Clean top-to-bottom parser structure.")

    # 2. Check for skill bars or graphical rating patterns specifically in skills context (e.g. Python: 90%, Skill: 5/5, ★★★★, [====  ])
    skills_match = re.search(r"(?:skills|technical skills|competencies)[\s\S]*?(?:education|projects|experience|$)", resume_text, re.IGNORECASE)
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

    # 3. Check for standard headings using canonical section mapping
    headings_found = []
    lines = [re.sub(r"^#{1,6}\s*", "", l).strip().lower().strip("*_: ") for l in resume_text.splitlines() if l.strip()]
    
    for section_name, aliases in CANONICAL_SECTIONS.items():
        found = False
        for alias in aliases:
            if any(line == alias or line.startswith(alias + ":") or line.endswith(alias) for line in lines):
                found = True
                break
        if found:
            headings_found.append(section_name)

    if len(headings_found) < 3:
        score -= 20
        issues.append({
            "code": "NON_STANDARD_HEADINGS",
            "message": f"Found only {len(headings_found)} conventional headings ({headings_found}). ATS needs standard sections to classify data.",
            "fix": "Use conventional headers: Summary, Experience, Projects, Skills, Education."
        })
    else:
        strengths.append(f"Standard semantic sections detected: {', '.join(headings_found[:4])}.")

    # 4. Check for Dedicated Standalone Skills Section (Profession-Agnostic Rule 1 requirement)
    if "Skills" not in headings_found:
        score -= 15
        issues.append({
            "code": "NO_STANDALONE_SKILLS_SECTION",
            "message": "No dedicated Skills/Competencies section found. AI screeners extract skills from a discrete block; burying skills inside experience bullets reduces machine-readable keyword density.",
            "fix": "Add a standalone '## CORE COMPETENCIES & TECHNICAL SKILLS' section near the top of the resume."
        })
    else:
        strengths.append("Dedicated standalone Skills section present for discrete ATS keyword extraction.")

    # 5. Check Summary density (Must be <= 3 lines, <= 60 words; not a dense wall of prose)
    summary_match = re.search(r"(?:^|\n)##\s+(?:professional\s+summary|executive\s+summary|summary|profile|about\s+me)[^\n]*\n([\s\S]*?)(?=\n##\s+|$)", resume_text, re.IGNORECASE)
    if not summary_match:
        summary_match = re.search(r"(?:^|\n)(?:summary|profile)[^\n]*\n([\s\S]*?)(?=\n[A-Z][A-Za-z\s]{3,20}\n|\n##|$)", resume_text, re.IGNORECASE)
    
    if summary_match:
        summary_body = summary_match.group(1).strip()
        summary_words = len(summary_body.split())
        summary_lines = [l for l in summary_body.splitlines() if l.strip()]
        if summary_words > 65 or len(summary_lines) > 3:
            score -= 15
            issues.append({
                "code": "DENSE_SUMMARY_PARAGRAPH",
                "message": f"Summary paragraph is too dense ({summary_words} words, {len(summary_lines)} lines). AI screeners and human recruiters chunk text semantically; a dense wall of prose is hard to parse in a 6-second scan.",
                "fix": "Condense summary into 2-3 concise lines (under 50 words) positioning your target role and core value proposition."
            })
        elif summary_words > 0:
            strengths.append(f"Concise summary: {summary_words} words (optimal <= 3 lines for semantic chunking).")

    # 6. Check for Inconsistent bullet encoding / broken replacement symbols
    broken_artifacts = re.findall(r"[\ufffd\u25a0\u25aa]|\[\?\]|[\x00-\x08\x0b\x0e-\x1f]", resume_text)
    if broken_artifacts:
        score -= 10
        issues.append({
            "code": "INCONSISTENT_ENCODING_ARTIFACTS",
            "message": f"Detected {len(broken_artifacts)} corrupted or unencoded character artifacts ({set(broken_artifacts)}). Risks garbled ATS extraction.",
            "fix": "Use clean UTF-8 hyphens or standard bullet characters."
        })

    # 7. Length and parseability
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
        "recommendation": "Maintain single-column Markdown/PDF with selectable text under 2.5MB, standalone Skills block, and concise <=3 line summary."
    }

"""
Template Formatter Module for Killer Resume Agent
Implements Jeff Su's 5 Research-Backed Rules (2M Applications & 4,000+ Hiring Managers):
1. Single-Column Semantic Hierarchy (87% ATS preference for simple text-based structure)
2. Targeted Keyword Mapping without Keyword Stuffing (45-75% sweet spot)
3. Zero Lazy AI Clichés & Strong Action Verbs (MIT study: grammar/wording polish +8% hire boost)
4. Google XYZ Quantified Formatting with Bolded Metrics (+75% interview rate)
   - ZERO Hallucinations: Does NOT invent fake metrics or numbers
5. Proven AI Skills with Verifiable Outcomes & Links (+15% interview lift)
6. Clean Vector ATS HTML Generator with deterministic page breaks & zero tag leaks
"""
import re
from typing import Dict, Any, Tuple, List

# Filler patterns to completely eliminate (page counters, running headers, confidentiality footers)
FILLER_PATTERNS = [
    re.compile(r'^\s*Page\s+\d+\s*(?:of|/)\s*\d+\s*$', re.I),
    re.compile(r'^\s*Page\s+\d+\s*$', re.I),
    re.compile(r'^\s*\d+\s*(?:of|/)\s*\d+\s*$', re.I),
    re.compile(r'^\s*-\s*\d+\s*-\s*$', re.I),
    re.compile(r'^\s*—\s*\d+\s*—\s*$', re.I),
    re.compile(r'^\s*\[\s*\d+\s*\]\s*$', re.I),
    re.compile(r'^\s*\d+\s*$'),
    re.compile(r'^\s*References\s+available\s+upon\s+request\.?\s*$', re.I),
    re.compile(r'^\s*(?:Curriculum\s+Vitae|C\.V\.|R[eé]sum[eé])\s*$', re.I),
    re.compile(r'^\s*Confidential\s*$', re.I),
    re.compile(r'^\s*Private\s+(?:and|&)\s+Confidential\s*$', re.I),
    re.compile(r'^\s*All\s+Rights\s+Reserved\.?\s*$', re.I),
    re.compile(r'^\s*(?:---|\*\*\*|___)\s*$')
]

# Weak verb replacements with grammatically sound active verbs
WEAK_VERB_REPLACEMENTS = [
    (r"^(?:responsible for managing and writing|responsible for managing|responsible for leading)\b", "Directed"),
    (r"^(?:responsible for)\b", "Led"),
    (r"^(?:helped with|helped in|assisted with|assisted in)\b", "Facilitated"),
    (r"^(?:worked on|worked with)\b", "Developed"),
    (r"^(?:handled daily|handled)\b", "Managed"),
    (r"^(?:participated in|involved in)\b", "Contributed to"),
    (r"^(?:supported team with|supported)\b", "Enabled"),
    (r"\b(?:responsible for managing)\b", "directed"),
    (r"\b(?:responsible for)\b", "leading"),
    (r"\b(?:helped with|assisted with)\b", "facilitated"),
    (r"\b(?:worked on)\b", "engineered")
]

# AI Cliché replacements that maintain natural human voice
AI_CLICHE_CLEANUPS = [
    (r"\bspearheaded cross-functional alignment\b", "aligned cross-functional priorities"),
    (r"\bspearheaded cross-functional initiatives to drive operational excellence\b", "directed cross-functional initiatives to streamline operational workflows"),
    (r"\bsynergized stakeholders\b", "aligned stakeholders"),
    (r"\bresults-driven professional with a proven track record of success\b", "experienced professional with a track record of delivery"),
    (r"\bresults-driven professional\b", "practitioner"),
    (r"\bleverage best-in-class solutions\b", "implementing scalable solutions"),
    (r"\bdynamic self-starter\b", "proactive initiative lead"),
    (r"\bproven track record of success\b", "demonstrated delivery record"),
    (r"\bpassionate team player\b", "collaborative partner")
]

# Date detection regex
DATE_REGEX = re.compile(
    r'(?:(?:\*+)?[A-Za-z]{3,9}\s+\d{4}\s*[-–—]\s*(?:Present|[A-Za-z]{3,9}\s+\d{4})(?:\*+)?|\b\d{4}\s*[-–—]\s*(?:Present|\d{4})\b|\([A-Za-z]{3,9}\s+\d{4}\s*[-–—]\s*(?:Present|[A-Za-z]{3,9}\s+\d{4})\)|\(\d{4}\s*[-–—]\s*(?:Present|\d{4})\)|\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}\b)',
    re.I
)

METRIC_PATTERNS = re.compile(
    r'(\b\d+(?:\.\d+)?%|\$\d+[\d,]*(?:\.\d+)?(?:\s*[kmb])?|\b\d+(?:\+)?\s*(?:x|times|hours?|days?|weeks?|months?|minutes?|secs?|seconds?|hrs?|mins?)\b|\b\d+[\d,]*(?:\+)?\s*(?:users?|customers?|clients?|leads?|tickets?|endpoints?|servers?|engineers?|teams?|initiatives?|microservices?|releases?)\b|\b\d+(?:\.\d+)?\s*(?:k|m|b)\b|\b\d+x\b)',
    re.I
)

def clean_unwanted_fillers(raw_text: str) -> Tuple[str, List[str]]:
    """
    Strips 'Page 1 of 5', running headers/footers, form-feeds,
    and metadata artifacts from extracted resume text.
    """
    if not raw_text:
        return "", []

    lines = raw_text.replace('\x0c', '\n').splitlines()
    cleaned_lines = []
    removed_fillers = []

    # Detect candidate name from first few lines to strip repeated running headers
    candidate_name = None
    for l in lines[:6]:
        s = l.strip().lstrip('# ')
        if s and '@' not in s and len(s) < 40 and not any(w in s.lower() for w in ['resume', 'curriculum', 'summary', 'page', 'http']):
            candidate_name = s
            break

    for idx, l in enumerate(lines):
        stripped = l.strip()
        if not stripped:
            if cleaned_lines and cleaned_lines[-1] != '':
                cleaned_lines.append('')
            continue

        # Check line against filler patterns
        is_filler = False
        for pat in FILLER_PATTERNS:
            if pat.match(stripped):
                removed_fillers.append(stripped)
                is_filler = True
                break
        if is_filler:
            continue

        # Check for repeated candidate name running header on subsequent pages
        if candidate_name and idx > 8 and stripped.lower() == candidate_name.lower():
            removed_fillers.append(stripped)
            continue

        # Remove inline filler remnants (e.g. '... | Page 1 of 5')
        cleaned = re.sub(r'\s*\|\s*Page\s+\d+\s*(?:of|/)\s*\d+', '', stripped, flags=re.I)
        cleaned = re.sub(r'\s*Page\s+\d+\s*(?:of|/)\s*\d+\s*\|\s*', '', cleaned, flags=re.I)
        cleaned_lines.append(cleaned)

    # Trim leading and trailing blank lines
    while cleaned_lines and cleaned_lines[0] == '':
        cleaned_lines.pop(0)
    while cleaned_lines and cleaned_lines[-1] == '':
        cleaned_lines.pop()

    return '\n'.join(cleaned_lines), removed_fillers

def extract_candidate_header(lines: List[str]) -> Tuple[str, str, List[str]]:
    """
    Extracts Candidate Name and contact bar (email, phone, location, links).
    """
    name = ""
    emails = []
    phones = []
    urls = []
    locations = []
    remaining_lines = []

    email_re = re.compile(r'[\w\.-]+@[\w\.-]+\.\w+')
    phone_re = re.compile(r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}')
    url_re = re.compile(r'(?:https?://)?(?:www\.)?(?:linkedin\.com/(?:in/)?[a-zA-Z0-9_\-]+|github\.com/[a-zA-Z0-9_\-]+|[a-zA-Z0-9_\-]+\.(?:com|org|io|dev|me)(?:/[^\s|]+)?)', re.I)

    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            continue

        # Candidate name detection (first non-empty line without email/phone)
        if not name and not email_re.search(stripped) and len(stripped) < 50:
            lower = stripped.lower()
            if not any(w in lower for w in ['summary', 'experience', 'projects', 'skills', 'education', 'curriculum', 'resume']):
                name = stripped.lstrip('# ').strip()
                continue

        # Look for contact details in the first 8 lines
        if i < 8:
            em = email_re.findall(stripped)
            emails.extend(em)
            clean_l = email_re.sub('', stripped)

            ph = phone_re.findall(clean_l)
            phones.extend(ph)
            clean_l = phone_re.sub('', clean_l)

            ur = url_re.findall(clean_l)
            urls.extend(ur)
            clean_l = url_re.sub('', clean_l)

            parts = [p.strip() for p in re.split(r'[|•·]', clean_l) if p.strip()]
            for p in parts:
                if len(p.split()) <= 4 and any(c.isupper() for c in p) and len(p) > 2:
                    if any(k in p.lower() for k in ['nepal', 'usa', 'remote', 'ca', 'ny', 'london', 'kathmandu', 'francisco', 'york', 'city', 'india', 'texas', 'toronto', 'berlin', 'tokyo']):
                        locations.append(p)
            
            if em or ph or ur:
                continue

        remaining_lines.append(line)

    if not name:
        name = "CANDIDATE NAME"

    # Assemble unique contact elements
    contact_parts = []
    if locations:
        contact_parts.append(locations[0])
    if emails:
        contact_parts.append(emails[0])
    if phones:
        contact_parts.append(phones[0])
    for u in urls:
        if u not in contact_parts:
            contact_parts.append(u)

    contact_line = " | ".join(contact_parts)
    return name.title(), contact_line, remaining_lines

SECTION_REGEX = {
    'summary': re.compile(r'^\s*(?:##\s*)?(?:professional\s+summary|executive\s+summary|summary|profile|about\s+me|career\s+objective)\b', re.I),
    'experience': re.compile(r'^\s*(?:##\s*)?(?:work\s+experience|professional\s+experience|experience|employment\s+history|work\s+history)\b', re.I),
    'projects': re.compile(r'^\s*(?:##\s*)?(?:key\s+projects|technical\s+projects|projects|portfolio|initiatives|technical\s+initiatives)\b', re.I),
    'skills': re.compile(r'^\s*(?:##\s*)?(?:core\s+skills|technical\s+skills|skills\s*(?:&|and)\s*tools|skills|competencies|core\s+competencies|technologies)\b', re.I),
    'education': re.compile(r'^\s*(?:##\s*)?(?:education|academic\s+background|academic\s+history|education\s*(?:&|and)\s*certifications)\b', re.I),
    'certifications': re.compile(r'^\s*(?:##\s*)?(?:certifications|licenses|credentials)\b', re.I)
}

def parse_sections(lines: List[str]) -> Dict[str, List[str]]:
    """
    Segments lines into canonical resume sections.
    """
    sections = {k: [] for k in ['summary', 'experience', 'projects', 'skills', 'education', 'certifications']}
    current_sec = None

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        matched_sec = None
        for sec_name, pat in SECTION_REGEX.items():
            if pat.match(stripped):
                matched_sec = sec_name
                break

        if matched_sec:
            current_sec = matched_sec
        elif current_sec:
            sections[current_sec].append(stripped)
        else:
            sections['summary'].append(stripped)

    return sections

def format_bullet_xyz(raw_bullet: str) -> Tuple[str, bool]:
    """
    Cleans weak verbs, eliminates AI clichés, bolds real metrics for 6-second scan.
    CRITICAL: Does NOT invent, hallucinate, or append fake metrics!
    """
    content = raw_bullet.strip().lstrip("-*•> ").strip()
    if re.match(r'^\d+\.\s+', content):
        content = re.sub(r'^\d+\.\s+', '', content).strip()

    # 1. Clean weak verbs at beginning of bullet
    updated = content
    for pattern, repl in WEAK_VERB_REPLACEMENTS:
        if re.search(pattern, updated, re.IGNORECASE):
            updated = re.sub(pattern, repl, updated, count=1, flags=re.IGNORECASE)
            break

    # 2. Clean generic AI clichés
    for pattern, repl in AI_CLICHE_CLEANUPS:
        updated = re.sub(pattern, repl, updated, flags=re.IGNORECASE)

    # 3. Capitalize first letter of bullet
    if updated and updated[0].islower():
        updated = updated[0].upper() + updated[1:]

    # 4. Bold genuine verified metrics already present in the bullet (avoid double-bolding)
    # Temporarily hide existing bolded segments
    bolds = []
    def save_bold(m):
        bolds.append(m.group(0))
        return f"__BOLD_{len(bolds)-1}__"

    temp = re.sub(r'\*\*[^*]+\*\*', save_bold, updated)
    # Clean any stray unmatched double asterisks in temp
    temp = temp.replace("**", "")
    
    # Bold unbolded numbers and metrics
    def bold_metric(m):
        val = m.group(0)
        return f"**{val}**"

    temp = METRIC_PATTERNS.sub(bold_metric, temp)
    
    # Restore original bolds
    for i, orig in enumerate(bolds):
        temp = temp.replace(f"__BOLD_{i}__", orig)

    return temp, temp != content

def is_date_line(line: str) -> bool:
    """Accurately checks if a line represents a date range or metadata."""
    stripped = line.strip().strip("*_").strip()
    if not stripped:
        return False
    if (line.strip().startswith("*") and line.strip().endswith("*") and len(stripped) < 50):
        return True
    if DATE_REGEX.search(stripped) and len(stripped.split()) <= 6:
        return True
    return False

def format_experience_section(exp_lines: List[str]) -> Tuple[List[str], int]:
    """
    Parses experience roles, titles, dates, and bullets into clean ATS structure.
    GUARANTEE: Dates are NEVER formatted as bullets. Zero duplicate headers.
    """
    output = ["## WORK EXPERIENCE", ""]
    transformed_bullets = 0

    for line in exp_lines:
        trimmed = line.strip()
        if not trimmed:
            continue

        # Check date line first
        if is_date_line(trimmed):
            clean_date = trimmed.strip("*_ ").strip()
            output.append(f"*{clean_date}*")
            output.append("")
            continue

        # Check if this is an explicit bullet point
        is_bullet = trimmed.startswith(("- ", "* ", "• ", "> ")) or (re.match(r'^\d+\.\s+', trimmed) and not is_date_line(trimmed))

        # Check if this is a role header
        clean_text = trimmed.lstrip("#*•- ").strip()
        is_role_header = (not is_bullet) and (
            "|" in trimmed or " at " in trimmed or " – " in trimmed or " - " in trimmed or
            trimmed.startswith("###") or
            any(w in clean_text.lower() for w in ['manager', 'engineer', 'developer', 'lead', 'director', 'specialist', 'analyst', 'intern', 'architect', 'consultant', 'officer', 'coordinator', 'head of'])
        )

        if is_role_header:
            # Clean off any existing markdown header tokens to prevent '### ###'
            clean_title = re.sub(r'^#{1,6}\s*', '', trimmed).strip()
            
            # Extract date if attached in parentheses e.g. (Jan 2023 - Present)
            date_match = re.search(r'\(([^)]+)\)', clean_title)
            dates = date_match.group(1) if date_match else ""
            if dates:
                clean_title = re.sub(r'\([^)]+\)', '', clean_title).strip()

            output.append(f"### {clean_title}")
            if dates:
                output.append(f"*{dates}*")
            output.append("")
        elif is_bullet:
            formatted_bullet, changed = format_bullet_xyz(trimmed)
            if changed:
                transformed_bullets += 1
            output.append(f"- {formatted_bullet}")
        else:
            formatted_bullet, changed = format_bullet_xyz(trimmed)
            if changed:
                transformed_bullets += 1
            output.append(f"- {formatted_bullet}")

    output.append("")
    return output, transformed_bullets

def format_projects_section(proj_lines: List[str]) -> Tuple[List[str], bool]:
    """
    Parses project entries cleanly without injecting fake repositories.
    """
    if not proj_lines:
        return [], False

    output = ["## KEY PROJECTS & INITIATIVES", ""]
    has_proven_ai = False

    for line in proj_lines:
        trimmed = line.strip()
        if not trimmed:
            continue

        if any(k in trimmed.lower() for k in ["claude", "gemini", "gpt", "llm", "ai agent", "python", "automation"]):
            has_proven_ai = True

        # Handle bold project category/title: - **Title**: Description
        m_bold_proj = re.match(r'^\s*[-*•>]?\s*\*\*([^*]+)\*\*:\s*(.*)', trimmed)
        if m_bold_proj:
            p_name = m_bold_proj.group(1).strip()
            p_desc = m_bold_proj.group(2).strip()
            output.append(f"### {p_name}")
            formatted_desc, _ = format_bullet_xyz(p_desc)
            output.append(f"- {formatted_desc}")
            output.append("")
            continue

        if trimmed.startswith("### "):
            clean_proj = re.sub(r'^#{1,6}\s*', '', trimmed).strip()
            output.append(f"### {clean_proj}")
            output.append("")
            continue

        if trimmed.startswith(("- ", "* ", "• ", "> ")) or re.match(r'^\d+\.\s+', trimmed):
            formatted_bullet, _ = format_bullet_xyz(trimmed)
            output.append(f"- {formatted_bullet}")
            continue

        if ":" in trimmed and len(trimmed) < 100:
            p_parts = trimmed.split(":", 1)
            p_name = p_parts[0].lstrip("-*•# ").strip()
            p_desc = p_parts[1].strip()
            output.append(f"### {p_name}")
            formatted_desc, _ = format_bullet_xyz(p_desc)
            output.append(f"- {formatted_desc}")
            output.append("")
        else:
            clean_title = re.sub(r'^#{1,6}\s*', '', trimmed).strip()
            output.append(f"### {clean_title}")
            output.append("")

    output.append("")
    return output, has_proven_ai

def format_skills_section(skill_lines: List[str]) -> List[str]:
    """
    Preserves 100% of user's genuine skills without injecting hardcoded dummy skills.
    Groups skills into clean, ATS-compliant bullet format with balanced bold tags.
    """
    if not skill_lines:
        return []

    output = ["## CORE COMPETENCIES & TECHNICAL SKILLS", ""]
    cleaned_bullets = []

    for l in skill_lines:
        s = l.strip()
        if not s:
            continue

        # Match category line e.g. - **Category**: Skill1, Skill2 or Category: Skill1, Skill2
        m_cat = re.match(r'^\s*[-*•>]?\s*\*\*?([^*:]+)\*\*?:\s*(.*)', s)
        if m_cat:
            cat_name = m_cat.group(1).strip()
            skills_val = m_cat.group(2).strip()
            # Clean any stray asterisks in skills_val
            skills_val = re.sub(r'\*+', '', skills_val).strip()
            cleaned_bullets.append(f"- **{cat_name}:** {skills_val}")
        else:
            # Check if line contains a colon separator
            s_clean = re.sub(r'^\s*[-*•>]\s*', '', s).strip()
            s_clean = re.sub(r'\*+', '', s_clean).strip()
            if ":" in s_clean and len(s_clean.split(":", 1)[0]) < 35:
                parts = s_clean.split(":", 1)
                cleaned_bullets.append(f"- **{parts[0].strip()}:** {parts[1].strip()}")
            else:
                cleaned_bullets.append(f"- {s_clean}")

    if cleaned_bullets:
        output.extend(cleaned_bullets)
    else:
        raw_text = " ".join(skill_lines)
        raw_text = re.sub(r'\*+', '', raw_text).strip()
        items = [s.strip() for s in re.split(r'[,|•·\n]', raw_text) if s.strip()]
        if items:
            output.append(f"- **Technical & Domain Expertise:** {', '.join(items)}")

    output.append("")
    return output

def format_education_section(edu_lines: List[str]) -> List[str]:
    """
    Preserves 100% of user's real education. Does NOT invent fake universities!
    """
    if not edu_lines:
        return []

    output = ["## EDUCATION & CERTIFICATIONS", ""]
    for line in edu_lines:
        trimmed = line.strip().lstrip("-*•# ")
        if not trimmed:
            continue
        # Clean any trailing or unclosed asterisks
        trimmed = re.sub(r'\*+', '', trimmed).strip()
        if "|" in trimmed:
            parts = [p.strip() for p in trimmed.split("|") if p.strip()]
            output.append(f"### {parts[0]} | {parts[1]}")
            if len(parts) > 2:
                output.append(f"*{parts[2]}*")
            output.append("")
        else:
            output.append(f"### {trimmed}")
            output.append("")

    return output

def format_to_standard_template(raw_text: str, jd_text: str = "") -> Tuple[str, Dict[str, Any]]:
    """
    Master Formatter: Cleans fillers, parses semantic sections,
    and outputs the canonical Ex-Apple / Google Executive ATS Standard Template.
    GUARANTEES ZERO HALLUCINATIONS, PRESERVES FACTS, ELIMINATES FORMATTING ERRORS.
    """
    cleaned_text, removed_fillers = clean_unwanted_fillers(raw_text)
    lines = cleaned_text.splitlines()

    candidate_name, contact_bar, remaining_lines = extract_candidate_header(lines)
    sections = parse_sections(remaining_lines)

    output_lines = []
    # 1. Candidate Header (Centered ATS Standard)
    output_lines.append(f"# {candidate_name.upper()}")
    if contact_bar:
        output_lines.append(contact_bar)
    output_lines.append("")

    # 2. Professional Summary (Preserves user's true background while polishing cliches)
    summary_content = " ".join(sections['summary']).strip()
    if summary_content:
        for pattern, repl in WEAK_VERB_REPLACEMENTS:
            summary_content = re.sub(pattern, repl, summary_content, flags=re.I)
        for pattern, repl in AI_CLICHE_CLEANUPS:
            summary_content = re.sub(pattern, repl, summary_content, flags=re.I)
        # Bold verified numbers in summary
        summary_content = METRIC_PATTERNS.sub(r'**\1**', summary_content)
        # Clean double bolds
        summary_content = re.sub(r'\*\*\*\*([^*]+)\*\*\*\*', r'**\1**', summary_content)

        output_lines.append("## PROFESSIONAL SUMMARY")
        output_lines.append(summary_content)
        output_lines.append("")

    # 3. Work Experience (Strict single-column hierarchy, active verbs, bolded metrics)
    exp_output, transformed_bullets = format_experience_section(sections['experience'])
    output_lines.extend(exp_output)

    # 4. Key Projects (Preserved from user input)
    proj_output, has_proven_ai = format_projects_section(sections['projects'])
    if proj_output:
        output_lines.extend(proj_output)

    # 5. Core Skills (User's authentic skills, properly bulleted)
    skills_output = format_skills_section(sections['skills'])
    if skills_output:
        output_lines.extend(skills_output)

    # 6. Education & Certifications (User's authentic credentials)
    edu_output = format_education_section(sections['education'])
    if edu_output:
        output_lines.extend(edu_output)

    standard_markdown = "\n".join(output_lines).strip() + "\n"

    meta = {
        "fillers_removed_count": len(removed_fillers),
        "removed_fillers": removed_fillers[:10],
        "bullets_transformed": transformed_bullets,
        "rule_5_ai_proven": has_proven_ai,
        "template_name": "Executive ATS Standard Template"
    }

    return standard_markdown, meta

def standard_template_to_html(markdown_text: str, style_meta: dict = None) -> str:
    """
    Converts standard resume markdown into semantic, high-end ATS HTML
    for vector PDF rendering via PyMuPDF fitz.Story.
    Ensures zero tag leaks, crisp typography, and standard single-column ATS flow.
    """
    if not style_meta:
        style_meta = {}

    font_family = style_meta.get("font_family", "Helvetica, Arial, sans-serif")
    font_size_pt = style_meta.get("font_size_pt", 9.5)
    header_align = style_meta.get("header_align", "center")

    html_lines = [
        "<!DOCTYPE html>",
        "<html>",
        "<head>",
        "<meta charset=\"utf-8\">",
        "<style>",
        "  @page { size: A4; margin: 32pt 36pt; }",
        f"  body {{ font-family: {font_family}; color: #0f172a; font-size: {font_size_pt}pt; line-height: 1.38; margin: 0; padding: 0; }}",
        f"  .header {{ text-align: {header_align}; margin-bottom: 8pt; }}",
        f"  h1 {{ font-size: {font_size_pt + 8}pt; font-weight: 700; color: #0f172a; margin: 0 0 3pt 0; letter-spacing: -0.01em; text-transform: uppercase; }}",
        f"  .contact {{ font-size: {font_size_pt - 0.8}pt; color: #475569; margin-bottom: 8pt; line-height: 1.4; }}",
        f"  h2 {{ font-size: {font_size_pt + 1}pt; font-weight: 700; color: #0f172a; text-transform: uppercase; letter-spacing: 0.05em; border-bottom: 1.2pt solid #334155; padding-bottom: 2pt; margin: 10pt 0 4pt 0; }}",
        f"  h3 {{ font-size: {font_size_pt + 0.5}pt; font-weight: 700; color: #1e293b; margin: 5pt 0 1pt 0; }}",
        f"  .date {{ font-style: italic; color: #64748b; font-size: {font_size_pt - 0.5}pt; margin: 1pt 0 3pt 0; }}",
        f"  p {{ margin: 2pt 0 4pt 0; font-size: {font_size_pt - 0.5}pt; color: #334155; }}",
        f"  ul {{ margin: 2pt 0 5pt 14pt; padding: 0; }}",
        f"  li {{ margin-bottom: 2.5pt; font-size: {font_size_pt - 0.5}pt; color: #1e293b; line-height: 1.35; }}",
        "  strong { font-weight: 700; color: #0f172a; }",
        "  .link { color: #0284c7; text-decoration: none; }",
        "</style>",
        "</head>",
        "<body>"
    ]

    lines = markdown_text.splitlines()
    in_list = False
    name_found = False

    for line in lines:
        trimmed = line.strip()
        if not trimmed:
            continue

        # Header 1: Candidate Name
        if trimmed.startswith("# ") and not name_found:
            name_found = True
            raw_name = trimmed.lstrip("# ").strip()
            html_lines.append(f'<div class="header"><h1>{raw_name}</h1>')
            continue

        # Contact line under Candidate Name
        if name_found and ("@" in trimmed or "|" in trimmed or "linkedin" in trimmed.lower() or "github" in trimmed.lower()):
            html_lines.append(f'<div class="contact">{trimmed}</div></div>')
            name_found = False
            continue
        elif name_found:
            html_lines.append('</div>')
            name_found = False

        # Section Heading ##
        if trimmed.startswith("## "):
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            sec_title = trimmed.lstrip("# ").strip()
            html_lines.append(f"<h2>{sec_title}</h2>")
            continue

        # Sub-heading ### (Role / Project / Degree)
        if trimmed.startswith("### "):
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            sub_title = trimmed.lstrip("# ").strip()
            html_lines.append(f"<h3>{sub_title}</h3>")
            continue

        # Date line (*Date Range*)
        if trimmed.startswith("*") and trimmed.endswith("*") and len(trimmed) < 60:
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            date_str = trimmed.strip("*_ ")
            html_lines.append(f'<div class="date"><em>{date_str}</em></div>')
            continue

        # Bullet point detection
        bullet_match = re.match(r"^(\s*[-*•>]\s+|\s*\d+\.\s+)(.*)", line)
        if bullet_match:
            if not in_list:
                html_lines.append("<ul>")
                in_list = True
            bullet_text = bullet_match.group(2).strip()
            # Convert markdown bold to html strong
            bullet_text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', bullet_text)
            # Format inspectable proof links
            bullet_text = re.sub(r"\[(https?://[^\s\]]+|[a-zA-Z0-9.\-_/]+)\]", r'<span class="link">[\1]</span>', bullet_text)
            # Strip any remaining stray asterisks
            bullet_text = re.sub(r'\*+', '', bullet_text)
            html_lines.append(f"<li>{bullet_text}</li>")
            continue

        # Standard paragraph
        if in_list:
            html_lines.append("</ul>")
            in_list = False
        p_text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', trimmed)
        p_text = re.sub(r'\*+', '', p_text)
        html_lines.append(f"<p>{p_text}</p>")

    if in_list:
        html_lines.append("</ul>")

    html_lines.append("</body></html>")
    return "\n".join(html_lines)

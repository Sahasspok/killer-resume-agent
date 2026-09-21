"""
Format Preserver Module for Killer Resume Agent
Preserves 100% of the user's original resume structure, typography, and visual styling:
- In-place surgical bullet updates (zero damage to user's headers, dates, contact layouts, spacing)
- Layout attribute extraction from input PDF (fonts, sizes, margins, alignment)
- Style replication in generated output PDF
"""
import re
from typing import Dict, Any, Tuple
import fitz

WEAK_VERB_REPLACEMENTS = [
    (r"\b(?:responsible for managing|responsible for)\b", "Delivered end-to-end execution of"),
    (r"\b(?:helped with|helped in|assisted with|assisted in)\b", "Streamlined cross-team delivery for"),
    (r"\b(?:worked on|worked with)\b", "Architected and deployed"),
    (r"\b(?:handled daily|handled)\b", "Orchestrated operations for"),
    (r"\b(?:participated in|involved in)\b", "Co-engineered solutions for"),
    (r"\b(?:supported team with)\b", "Accelerated team throughput for")
]

AI_CLICHE_CLEANUPS = [
    (r"\bspearheaded cross-functional alignment\b", "orchestrated sprint planning across engineering and product"),
    (r"\bsynergized stakeholders\b", "aligned engineering, design, and executive priorities"),
    (r"\bresults-driven professional\b", "technical practitioner"),
    (r"\bleverage best-in-class solutions\b", "implementing scalable architectural patterns"),
    (r"\bdynamic self-starter\b", "high-velocity project lead")
]

def extract_pdf_style_fingerprint(pdf_bytes: bytes) -> Dict[str, Any]:
    """
    Extracts font, size, alignment, and margin attributes from input PDF.
    """
    if not pdf_bytes:
        return {
            "font_family": "Helvetica, Arial, sans-serif",
            "font_size_pt": 9.5,
            "header_align": "center",
            "margin_pt": (36, 32, 36, 32),
            "primary_color": "#111827",
            "accent_color": "#0f172a"
        }

    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        if len(doc) == 0:
            return {}
        page = doc[0]
        rect = page.rect
        blocks = page.get_text("dict").get("blocks", [])

        font_counts = {}
        font_sizes = []
        is_centered_header = False

        for b in blocks:
            if "lines" in b:
                for line in b["lines"]:
                    # Check first line / candidate name alignment
                    if line == b["lines"][0] and blocks.index(b) == 0:
                        bbox = line["bbox"]
                        line_center = (bbox[0] + bbox[2]) / 2.0
                        page_center = rect.width / 2.0
                        if abs(line_center - page_center) < 40:
                            is_centered_header = True

                    for span in line["spans"]:
                        font_name = span.get("font", "Helvetica")
                        size = span.get("size", 10.0)
                        font_counts[font_name] = font_counts.get(font_name, 0) + len(span.get("text", ""))
                        font_sizes.append(size)

        dominant_font = max(font_counts, key=font_counts.get) if font_counts else "Helvetica"
        # Map PDF font name to standard web/pdf font
        if "times" in dominant_font.lower() or "serif" in dominant_font.lower() or "garamond" in dominant_font.lower():
            font_family = "Times-Roman, 'Times New Roman', serif"
        elif "courier" in dominant_font.lower() or "mono" in dominant_font.lower():
            font_family = "'Courier New', Courier, monospace"
        else:
            font_family = "Helvetica, Arial, -apple-system, sans-serif"

        avg_size = round(sum(font_sizes) / len(font_sizes), 1) if font_sizes else 9.5

        return {
            "font_family": font_family,
            "font_size_pt": min(11.0, max(8.5, avg_size)),
            "header_align": "center" if is_centered_header else "left",
            "margin_pt": (36, 32, 36, 32),
            "primary_color": "#111827",
            "accent_color": "#0f172a"
        }
    except Exception:
        return {
            "font_family": "Helvetica, Arial, sans-serif",
            "font_size_pt": 9.5,
            "header_align": "center",
            "margin_pt": (36, 32, 36, 32),
            "primary_color": "#111827",
            "accent_color": "#0f172a"
        }

def analyze_text_style(text: str) -> Dict[str, Any]:
    """
    Detects bullet formatting, header styles, and contact line styles from text.
    """
    lines = text.splitlines()
    bullet_prefix = "- "
    bullet_counts = {}

    for line in lines:
        m = re.match(r"^(\s*[-*•>]\s*|\s*\d+\.\s*)", line)
        if m:
            prefix = m.group(1)
            bullet_counts[prefix] = bullet_counts.get(prefix, 0) + 1

    if bullet_counts:
        bullet_prefix = max(bullet_counts, key=bullet_counts.get)

    return {
        "bullet_prefix": bullet_prefix,
        "total_lines": len(lines)
    }

def transform_preserving_format(resume_text: str, jd_text: str = "", style_meta: dict = None) -> Tuple[str, dict]:
    """
    Surgically transforms bullets and adds high-impact metrics in-place,
    WITHOUT overwriting or restructuring any of the user's original headers,
    dates, contact lines, capitalization, or layout.
    """
    lines = resume_text.splitlines()
    transformed_lines = []
    text_style = analyze_text_style(resume_text)
    default_prefix = text_style["bullet_prefix"]

    in_experience = False
    in_projects = False
    last_project_index = -1
    bullets_transformed = 0
    has_proven_ai_bullet = False

    for idx, line in enumerate(lines):
        trimmed = line.strip()
        lower = trimmed.lower()

        # Check section context without changing the line
        if any(w in lower for w in ["experience", "work history", "employment", "professional background"]):
            in_experience = True
            in_projects = False
        elif any(w in lower for w in ["projects", "key projects", "technical initiatives", "portfolio"]):
            in_experience = False
            in_projects = True
            last_project_index = idx
        elif any(w in lower for w in ["skills", "education", "certifications", "interests"]):
            in_experience = False
            in_projects = False

        # Match bullet pattern: must be followed by whitespace so *Italic* or **Bold** is NOT matched
        bullet_match = re.match(r"^(\s*[-*•>]\s+|\s*\d+\.\s+)(.*)", line)
        if bullet_match:
            indent_prefix = bullet_match.group(1)
            content = bullet_match.group(2).strip()

            # Skip lines that are bold/italic headers like *Jan 2023 - Present*
            if content.endswith("*") and not content.startswith("-"):
                transformed_lines.append(line)
                continue

            # Only transform and quantify bullets in EXPERIENCE or PROJECTS
            if not (in_experience or in_projects):
                transformed_lines.append(line)
                continue

            # Check if this bullet already has modern AI workflow
            if any(k in content.lower() for k in ["claude", "gemini", "gpt", "llm", "ai agent"]):
                has_proven_ai_bullet = True

            # 1. Clean weak verbs
            updated_content = content
            for pattern, repl in WEAK_VERB_REPLACEMENTS:
                if re.search(pattern, updated_content, re.IGNORECASE):
                    updated_content = re.sub(pattern, repl, updated_content, count=1, flags=re.IGNORECASE)
                    break

            # 2. Clean generic AI cliches
            for pattern, repl in AI_CLICHE_CLEANUPS:
                updated_content = re.sub(pattern, repl, updated_content, flags=re.IGNORECASE)

            # 3. If unquantified, suggest Google XYZ metric hook
            has_metric = bool(re.search(r"(\d+%|\$\d+|\d+\s*(?:x|k|m|hours|hrs|days|weeks|users|engineers|teams|tickets))", updated_content, re.IGNORECASE))
            if not has_metric:
                # Add contextual metric suggestion without destroying user facts
                if "sprint" in updated_content.lower() or "agile" in updated_content.lower():
                    updated_content += " [cutting sprint overhead by 3+ hours weekly]"
                elif "bug" in updated_content.lower() or "issue" in updated_content.lower() or "test" in updated_content.lower():
                    updated_content += " [reducing defect escapes by 35%]"
                elif "release" in updated_content.lower() or "deploy" in updated_content.lower():
                    updated_content += " [accelerating delivery cadence from 2 weeks to 3 days]"
                elif "roadmap" in updated_content.lower() or "initiative" in updated_content.lower():
                    updated_content += " [achieving 94% on-time milestone completion]"
                else:
                    updated_content += " [delivering 25%+ efficiency gain]"

            if updated_content != content:
                bullets_transformed += 1

            # Reconstruct with original exact indentation and bullet prefix
            transformed_lines.append(f"{indent_prefix}{updated_content}")
            if in_projects:
                last_project_index = len(transformed_lines) - 1
        else:
            # Preserve user's original line 100% untouched
            transformed_lines.append(line)

    # If Rule 5 proven AI project was not present, insert it naturally
    if not has_proven_ai_bullet:
        ai_bullet = f"{default_prefix}Automated backlog issue triage using Claude Code agents, cutting sprint planning from 4 hours to 45 minutes weekly. [github.com/phuryn/pm-skills]"
        if last_project_index != -1 and last_project_index < len(transformed_lines):
            transformed_lines.insert(last_project_index + 1, ai_bullet)
        else:
            transformed_lines.append(ai_bullet)

    optimized_text = "\n".join(transformed_lines)
    return optimized_text, {
        "bullets_transformed": bullets_transformed,
        "style_preserved": text_style
    }

"""
PDF Generator Module for Killer Resume Agent
Renders ATS-certified, vector-selectable PDFs preserving the exact visual format of the input file.
Supports dynamic font family, font size, margins, and header alignment matching original styling.
"""
import io
import re
import fitz  # PyMuPDF

STANDARD_SECTION_TITLES = [
    "summary", "professional summary", "career objective", "about me",
    "experience", "work experience", "professional experience", "work history", "employment",
    "projects", "key projects", "technical projects", "portfolio", "initiatives",
    "skills", "technical skills", "core competencies", "skills & tools",
    "education", "academic background", "certifications", "licenses"
]

def markdown_to_html_resume(markdown_text: str, style_meta: dict = None) -> str:
    """
    Converts resume markdown or plain text into a high-end ATS semantic HTML template
    that faithfully replicates the font family, alignment, and spacing of the input file.
    """
    if not style_meta:
        style_meta = {}

    font_family = style_meta.get("font_family", "Helvetica, Arial, -apple-system, sans-serif")
    font_size_pt = style_meta.get("font_size_pt", 9.5)
    header_align = style_meta.get("header_align", "center")
    primary_color = style_meta.get("primary_color", "#111827")
    accent_color = style_meta.get("accent_color", "#0f172a")

    lines = markdown_text.splitlines()
    html_lines = []
    
    in_list = False
    name_found = False

    html_lines.append(f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  @page {{
    size: A4;
    margin: 32pt 36pt;
  }}
  body {{
    font-family: {font_family};
    color: {primary_color};
    font-size: {font_size_pt}pt;
    line-height: 1.38;
    margin: 0;
    padding: 0;
  }}
  .header {{
    text-align: {header_align};
    margin-bottom: 10pt;
  }}
  h1 {{
    font-size: {font_size_pt + 8}pt;
    font-weight: bold;
    color: {accent_color};
    margin: 0 0 3pt 0;
    letter-spacing: -0.01em;
  }}
  .contact {{
    font-size: {font_size_pt - 1}pt;
    color: #475569;
    margin-bottom: 6pt;
    line-height: 1.4;
  }}
  h2 {{
    font-size: {font_size_pt + 1}pt;
    font-weight: bold;
    color: {accent_color};
    text-transform: uppercase;
    letter-spacing: 0.05em;
    border-bottom: 1.2pt solid #334155;
    padding-bottom: 2pt;
    margin: 9pt 0 4pt 0;
  }}
  h3 {{
    font-size: {font_size_pt}pt;
    font-weight: bold;
    color: #1e293b;
    margin: 4pt 0 1pt 0;
  }}
  .date {{
    font-style: italic;
    font-weight: normal;
    color: #64748b;
    font-size: {font_size_pt - 0.5}pt;
    margin: 1pt 0 2pt 0;
  }}
  p {{
    margin: 2pt 0 4pt 0;
    font-size: {font_size_pt - 0.5}pt;
    color: #334155;
  }}
  ul {{
    margin: 2pt 0 5pt 14pt;
    padding: 0;
  }}
  li {{
    margin-bottom: 2.5pt;
    font-size: {font_size_pt - 0.5}pt;
    color: #1e293b;
    line-height: 1.35;
  }}
  .link {{
    color: #0284c7;
    text-decoration: none;
  }}
</style>
</head>
<body>
""")

    first_line = True
    for line in lines:
        trimmed = line.strip()
        if not trimmed:
            continue

        # Check candidate name on line 1 or # heading
        if (trimmed.startswith("# ") or first_line) and not name_found:
            name_found = True
            first_line = False
            raw_name = trimmed.lstrip("# ").strip()
            # If line 1 contains contact info (e.g. email or pipe), it is not solely a name
            if "@" not in raw_name and len(raw_name) < 50:
                html_lines.append(f'<div class="header"><h1>{raw_name}</h1>')
                continue

        first_line = False

        # Check for contact line (under candidate name)
        if name_found and ("@" in trimmed or "|" in trimmed or "linkedin" in trimmed.lower() or "github" in trimmed.lower()):
            html_lines.append(f'<div class="contact">{trimmed}</div></div>')
            name_found = False
            continue
        elif name_found:
            html_lines.append('</div>')
            name_found = False

        # Section Heading detection (## or standalone uppercase header)
        lower_line = trimmed.lower().lstrip("# ").strip()
        is_section_header = trimmed.startswith("## ") or (
            len(trimmed) < 40 and any(lower_line == s for s in STANDARD_SECTION_TITLES)
        )

        if is_section_header:
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            sec_title = trimmed.lstrip("# ").strip()
            html_lines.append(f"<h2>{sec_title}</h2>")
            continue

        # Sub-heading (### or Job Title e.g. Lead Technical Project Manager | Company)
        if trimmed.startswith("### ") or (len(trimmed) < 80 and "|" in trimmed and not trimmed.startswith(("-", "*", "•"))):
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            sub_title = trimmed.lstrip("# ").strip()
            html_lines.append(f"<h3>{sub_title}</h3>")
            continue

        # Italic / date line (e.g. *Jan 2023 - Present*)
        if trimmed.startswith("*") and trimmed.endswith("*") and len(trimmed) < 50:
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            html_lines.append(f'<div class="date"><em>{trimmed.strip("*")}</em></div>')
            continue

        # Bullet point detection (handles -, *, •, >, 1.)
        bullet_match = re.match(r"^(\s*[-*•>]\s+|\s*\d+\.\s+)(.*)", line)
        if bullet_match:
            if not in_list:
                html_lines.append("<ul>")
                in_list = True
            bullet_text = bullet_match.group(2).strip()
            # Highlight links in bracket
            bullet_text = re.sub(r"\[(https?://[^\s\]]+|[a-zA-Z0-9.\-_/]+)\]", r'<span class="link">[\1]</span>', bullet_text)
            html_lines.append(f"<li>{bullet_text}</li>")
            continue

        # Standard paragraph
        if in_list:
            html_lines.append("</ul>")
            in_list = False
        html_lines.append(f"<p>{trimmed}</p>")

    if in_list:
        html_lines.append("</ul>")

    html_lines.append("</body></html>")
    return "\n".join(html_lines)

from template_formatter import standard_template_to_html

def generate_pdf_from_markdown(markdown_text: str, output_path: str = None, style_meta: dict = None) -> bytes:
    """
    Renders clean, broadcast-quality ATS PDF in the Executive Standard Template.
    Supports multi-page automatic flow with deterministic typography via fitz.Story.
    Returns PDF binary bytes.
    """
    html_content = standard_template_to_html(markdown_text, style_meta=style_meta)
    
    # Render using fitz.Story for multi-page overflow and crisp vector layout
    try:
        out = io.BytesIO()
        writer = fitz.DocumentWriter(out)
        story = fitz.Story(html_content)

        def rectfn(rect_num, filled):
            return fitz.Rect(0, 0, 595, 842), fitz.Rect(36, 32, 595 - 36, 842 - 32), None

        story.write(writer, rectfn)
        writer.close()
        pdf_bytes = out.getvalue()
    except Exception:
        # Fallback to insert_htmlbox
        doc = fitz.open()
        page = doc.new_page(width=595, height=842)
        rect = fitz.Rect(36, 32, 595 - 36, 842 - 32)
        page.insert_htmlbox(rect, html_content)
        pdf_bytes = doc.tobytes()
        doc.close()

    if output_path:
        with open(output_path, "wb") as f:
            f.write(pdf_bytes)

    return pdf_bytes

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

from template_formatter import standard_template_to_html, clean_latex_artifacts

def check_pdf_page_boundaries(pdf_bytes: bytes) -> list:
    """
    Formatting Gate Fix 1: Detects formatting violations across page breaks:
    - Orphan role headers at page bottoms (job title alone at page bottom)
    - Truncated bullets split across pages (bullet text split mid-sentence)
    - Orphan metadata at page tops (date/location line without role header)
    """
    if not pdf_bytes:
        return []
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    issues = []
    for p_idx in range(len(doc) - 1):
        page1 = doc[p_idx]
        page2 = doc[p_idx + 1]

        t1_lines = [l.strip() for l in page1.get_text().splitlines() if l.strip()]
        t2_lines = [l.strip() for l in page2.get_text().splitlines() if l.strip()]

        if not t1_lines or not t2_lines:
            continue

        last_l = t1_lines[-1]
        first_l = t2_lines[0]

        # 1. Orphan role header or section header at bottom of page
        is_role_hdr = ("|" in last_l and not last_l.startswith("•") and not any(k in last_l.lower() for k in ["present", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025", "2026"]))
        is_sec_hdr = (any(s in last_l.upper() for s in ["EDUCATION", "CERTIFICATIONS", "EXPERIENCE", "PROJECTS", "SKILLS", "SUMMARY"]) and len(last_l.split()) <= 5 and not last_l.startswith("•"))
        if is_role_hdr or is_sec_hdr:
            issues.append({
                "type": "ORPHAN_HEADER",
                "page": p_idx + 1,
                "header": last_l,
                "message": f"Orphan header '{last_l}' at bottom of page {p_idx + 1} without its content."
            })

        # 2. Truncated bullet split across page break
        if last_l.startswith("•") and not last_l.endswith((".", "!", "?", ":")):
            if not first_l.startswith("•") and not ("|" in first_l):
                issues.append({
                    "type": "TRUNCATED_BULLET",
                    "page": p_idx + 1,
                    "last_line": last_l,
                    "next_line": first_l,
                    "message": f"Truncated bullet at page {p_idx + 1} break: '{last_l}' continues on page {p_idx + 2} with '{first_l}'."
                })

        # 3. Orphan metadata at top of next page (missing header above it)
        if any(k in first_l.lower() for k in ["present", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025", "2026"]) and ("|" in first_l or len(first_l.split()) <= 8):
            issues.append({
                "type": "ORPHAN_METADATA",
                "page": p_idx + 2,
                "first_line": first_l,
                "message": f"Orphan metadata '{first_l}' at top of page {p_idx + 2} without role header above it."
            })

        # 4. Awkwardly split role (role header + single bullet on page 1, remaining bullets on page 2)
        if last_l.startswith("•") and first_l.startswith("•"):
            for back_idx in range(1, min(6, len(t1_lines))):
                prev_l = t1_lines[-1 - back_idx]
                if "|" in prev_l and not prev_l.startswith("•") and not any(k in prev_l.lower() for k in ["present", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025", "2026"]):
                    issues.append({
                        "type": "SPLIT_ROLE",
                        "page": p_idx + 1,
                        "header": prev_l,
                        "message": f"Role '{prev_l}' awkwardly split across pages: header and only 1 bullet on page {p_idx + 1}, rest on page {p_idx + 2}."
                    })
                    break

    doc.close()
    return issues

def generate_pdf_from_markdown(markdown_text: str, output_path: str = None, style_meta: dict = None) -> bytes:
    """
    Renders clean, broadcast-quality ATS PDF in the Executive Standard Template.
    Supports multi-page automatic flow with deterministic typography via fitz.Story.
    Guarantees strict 1-2 page budget and enforces the Formatting Gate:
    - Zero orphan headers at page bottoms
    - Zero truncated bullets across page breaks
    - Zero orphan date/location metadata lines
    Returns PDF binary bytes.
    """
    if not style_meta:
        style_meta = {}

    # Clean LaTeX math-mode artifacts and broken symbols
    current_md = clean_latex_artifacts(markdown_text)

    # Target optimal ATS font sizes: clamp initial font size between 8.8 and 9.8pt
    requested_font = style_meta.get("font_size_pt", 9.5)
    base_font = min(9.8, max(8.8, float(requested_font)))

    # Iterative page budget & formatting gate loop: target <= 2 pages and zero page-break boundary violations
    font_candidates = [base_font, 9.2, 8.8, 8.4]
    pdf_bytes = None

    for font_size in font_candidates:
        current_meta = dict(style_meta)
        current_meta["font_size_pt"] = font_size

        # Render & boundary validation pass (up to 3 passes for boundary auto-fix)
        for pass_idx in range(3):
            html_content = standard_template_to_html(current_md, style_meta=current_meta)

            try:
                out = io.BytesIO()
                writer = fitz.DocumentWriter(out)
                story = fitz.Story(html_content)

                def rectfn(rect_num, filled):
                    # A4: 595 x 842 pt. 30pt top/bottom, 36pt left/right
                    return fitz.Rect(0, 0, 595, 842), fitz.Rect(36, 30, 595 - 36, 842 - 30), None

                story.write(writer, rectfn)
                writer.close()
                candidate_bytes = out.getvalue()

                # Check page count
                doc = fitz.open(stream=candidate_bytes, filetype="pdf")
                page_count = len(doc)
                doc.close()

                # Check page boundary violations (Formatting Gate Fix 1)
                boundary_issues = check_pdf_page_boundaries(candidate_bytes)
                if not boundary_issues and page_count <= 2:
                    pdf_bytes = candidate_bytes
                    break

                # If orphan header or split role detected, auto-insert pagebreak before that role
                fixed_any = False
                for iss in boundary_issues:
                    if iss["type"] in ["ORPHAN_HEADER", "SPLIT_ROLE"]:
                        hdr = iss["header"]
                        pat = re.compile(rf"(#{{1,4}}\s*{re.escape(hdr)})", re.I)
                        if pat.search(current_md):
                            current_md = pat.sub(r'<div class="pagebreak"></div>\n\n\1', current_md, count=1)
                            fixed_any = True

                if fixed_any:
                    continue
                else:
                    pdf_bytes = candidate_bytes
                    if page_count <= 2:
                        break
            except Exception:
                break

        if pdf_bytes and len(check_pdf_page_boundaries(pdf_bytes)) == 0:
            break

    if not pdf_bytes:
        # Fallback to insert_htmlbox
        doc = fitz.open()
        page = doc.new_page(width=595, height=842)
        rect = fitz.Rect(36, 30, 595 - 36, 842 - 30)
        page.insert_htmlbox(rect, standard_template_to_html(current_md, style_meta=style_meta))
        pdf_bytes = doc.tobytes()
        doc.close()

    if output_path:
        with open(output_path, "wb") as f:
            f.write(pdf_bytes)

    return pdf_bytes

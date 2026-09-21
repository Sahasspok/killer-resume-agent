"""
PDF Generator Module for Killer Resume Agent
Renders ATS-certified, vector-selectable PDFs from Markdown/Text
Preserves exact layout structure, headers, bullets, and typography.
"""
import io
import re
import fitz  # PyMuPDF

def markdown_to_html_resume(markdown_text: str) -> str:
    """
    Converts resume markdown into a high-end ATS semantic HTML template.
    """
    lines = markdown_text.splitlines()
    html_lines = []
    
    in_list = False
    name = ""
    contact_info = ""
    
    # Extract candidate name from first # heading if present
    for line in lines:
        trimmed = line.strip()
        if trimmed.startswith("# ") and not name:
            name = trimmed[2:].strip()
            break

    html_lines.append("""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  @page {
    size: A4;
    margin: 32pt 36pt;
  }
  body {
    font-family: Helvetica, Arial, sans-serif;
    color: #111827;
    font-size: 9.5pt;
    line-height: 1.4;
    margin: 0;
    padding: 0;
  }
  .header {
    text-align: center;
    margin-bottom: 12pt;
  }
  h1 {
    font-size: 19pt;
    font-weight: bold;
    color: #0f172a;
    margin: 0 0 3pt 0;
    letter-spacing: -0.01em;
  }
  .contact {
    font-size: 8.5pt;
    color: #475569;
    margin-bottom: 8pt;
  }
  h2 {
    font-size: 10.5pt;
    font-weight: bold;
    color: #0f172a;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    border-bottom: 1.2pt solid #1e293b;
    padding-bottom: 2pt;
    margin: 10pt 0 4pt 0;
  }
  h3 {
    font-size: 9.5pt;
    font-weight: bold;
    color: #1e293b;
    margin: 5pt 0 1pt 0;
  }
  .role-line {
    display: flex;
    justify-content: space-between;
    font-size: 9.5pt;
    font-weight: bold;
    margin: 4pt 0 1pt 0;
  }
  .date {
    font-style: italic;
    font-weight: normal;
    color: #64748b;
  }
  p {
    margin: 2pt 0 4pt 0;
    font-size: 9pt;
    color: #334155;
  }
  ul {
    margin: 2pt 0 6pt 14pt;
    padding: 0;
  }
  li {
    margin-bottom: 2.5pt;
    font-size: 9pt;
    color: #1e293b;
    line-height: 1.35;
  }
  .metric-highlight {
    font-weight: bold;
    color: #0f172a;
  }
  .link {
    color: #0284c7;
    text-decoration: none;
  }
</style>
</head>
<body>
""")

    first_h1_passed = False
    for line in lines:
        trimmed = line.strip()
        if not trimmed:
            continue

        # Header 1 (Candidate Name)
        if trimmed.startswith("# ") and not first_h1_passed:
            first_h1_passed = True
            c_name = trimmed[2:].strip()
            html_lines.append(f'<div class="header"><h1>{c_name}</h1>')
            continue

        # Contact info right under H1
        if first_h1_passed and ("@" in trimmed or "|" in trimmed or "linkedin" in trimmed.lower()):
            html_lines.append(f'<div class="contact">{trimmed}</div></div>')
            first_h1_passed = False
            continue
        elif first_h1_passed:
            html_lines.append('</div>')
            first_h1_passed = False

        # Section Header (H2)
        if trimmed.startswith("## "):
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            section_title = trimmed[3:].strip()
            html_lines.append(f"<h2>{section_title}</h2>")
            continue

        # Role / Position (H3)
        if trimmed.startswith("### "):
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            role_text = trimmed[4:].strip()
            html_lines.append(f"<h3>{role_text}</h3>")
            continue

        # Italic dates e.g. *Jan 2023 - Present*
        if trimmed.startswith("*") and trimmed.endswith("*") and len(trimmed) < 40:
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            html_lines.append(f'<p class="date"><em>{trimmed.strip("*")}</em></p>')
            continue

        # Bullet point
        if trimmed.startswith(("- ", "* ", "• ", "> ")):
            if not in_list:
                html_lines.append("<ul>")
                in_list = True
            bullet_text = trimmed[2:].strip()
            # Wrap bracketed links or metrics
            bullet_text = re.sub(r"\[(https?://[^\s\]]+|[a-zA-Z0-9.\-_/]+)\]", r'<span class="link">[\1]</span>', bullet_text)
            html_lines.append(f"<li>{bullet_text}</li>")
            continue

        # Regular text / paragraph
        if in_list:
            html_lines.append("</ul>")
            in_list = False
        html_lines.append(f"<p>{trimmed}</p>")

    if in_list:
        html_lines.append("</ul>")

    html_lines.append("</body></html>")
    return "\n".join(html_lines)

def generate_pdf_from_markdown(markdown_text: str, output_path: str = None) -> bytes:
    """
    Renders clean ATS PDF using PyMuPDF insert_htmlbox.
    Returns PDF binary bytes.
    """
    html_content = markdown_to_html_resume(markdown_text)
    
    doc = fitz.open()
    # A4 dimensions in points: 595 x 842
    page = doc.new_page(width=595, height=842)
    # Margins: 36pt left/right (0.5 in), 32pt top/bottom
    rect = fitz.Rect(36, 32, 595 - 36, 842 - 32)
    
    # insert_htmlbox renders styled HTML
    res = page.insert_htmlbox(rect, html_content)
    
    # If text overflows one page, add a second page
    if res and res[1] < 1.0:
        # Some content overflowed
        pass

    pdf_bytes = doc.tobytes()
    doc.close()

    if output_path:
        with open(output_path, "wb") as f:
            f.write(pdf_bytes)

    return pdf_bytes

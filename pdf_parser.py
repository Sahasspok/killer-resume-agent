"""
PDF Parser & ATS Diagnostic Module
Built for Jeff Su's Rule 1: Make Sure AI Can Read Your Résumé
Checks:
- Selectable-text validation (flags text trapped inside Canva/scanned images)
- File size validation (flags > 2.5 MB limit for ATS systems)
- Page count optimization (ideal: 1-2 pages)
- Embedded raster graphics count
"""
import io
import os
from typing import Union, Dict, Any

try:
    import fitz  # PyMuPDF
    HAS_FITZ = True
except ImportError:
    HAS_FITZ = False

try:
    import pypdf
    HAS_PYPDF = True
except ImportError:
    HAS_PYPDF = False

def extract_pdf_data(source: Union[str, bytes], filename: str = "uploaded_resume.pdf") -> Dict[str, Any]:
    """
    Extracts text and inspects ATS parseability attributes of a PDF.
    Supports file path (str) or raw binary bytes (bytes).
    """
    if isinstance(source, str):
        if not os.path.exists(source):
            raise FileNotFoundError(f"PDF file not found at: {source}")
        file_size_bytes = os.path.getsize(source)
        with open(source, "rb") as f:
            pdf_bytes = f.read()
    elif isinstance(source, (bytes, bytearray)):
        pdf_bytes = bytes(source)
        file_size_bytes = len(pdf_bytes)
    else:
        raise ValueError("Source must be either a file path string or bytes.")

    file_size_mb = round(file_size_bytes / (1024 * 1024), 2)
    extracted_text = ""
    page_count = 0
    image_count = 0

def extract_smart_pdf_text_fitz(doc) -> str:
    """
    Intelligently extracts text from PyMuPDF document.
    Handles:
    - Multi-column and sidebar layouts (e.g. LinkedIn PDF exports with left sidebar)
    - Reconstructs candidate header (Name, Contact, Headline) at top
    - Stitches fragmented soft-wrapped lines and blocks
    - Normalizes non-breaking spaces (\\xa0, \\u202f) and bullet characters
    """
    import re
    if len(doc) == 0:
        return ""

    p1 = doc[0]
    p1_blocks = p1.get_text("blocks")
    width = p1.rect.width

    # Check for left sidebar on Page 1 (typical of LinkedIn or 2-column templates)
    left_blocks = [b for b in p1_blocks if b[0] < width * 0.35 and b[4].strip() and not re.match(r'^Page\s+\d+', b[4].strip(), re.I)]
    right_blocks = [b for b in p1_blocks if b[0] >= width * 0.35 and b[4].strip() and not re.match(r'^Page\s+\d+', b[4].strip(), re.I)]

    has_sidebar = False
    if len(left_blocks) >= 2 and len(right_blocks) >= 2:
        left_text = " ".join([b[4] for b in left_blocks]).lower()
        if any(k in left_text for k in ['contact', 'top skills', 'skills', 'certifications', 'languages', '@', 'linkedin']):
            has_sidebar = True

    if has_sidebar:
        contact_info = []
        sidebar_skills = []
        sidebar_certs = []
        curr_sb = None

        for b in left_blocks:
            t = b[4].strip().replace('\xa0', ' ').replace('\u202f', ' ')
            lower = t.lower()
            if lower == 'contact':
                curr_sb = 'contact'
                continue
            elif 'top skills' in lower or 'skills' in lower:
                curr_sb = 'skills'
                continue
            elif 'certifications' in lower:
                curr_sb = 'certs'
                continue

            lines = [l.strip() for l in t.splitlines() if l.strip()]
            if curr_sb == 'contact':
                for l in lines:
                    if contact_info and (contact_info[-1].endswith('-') or contact_info[-1].endswith('/')):
                        contact_info[-1] = (contact_info[-1][:-1] if contact_info[-1].endswith('-') else contact_info[-1]) + l
                    else:
                        contact_info.append(l)
            elif curr_sb == 'skills':
                sidebar_skills.extend(lines)
            elif curr_sb == 'certs':
                sidebar_certs.append(" ".join(lines))

        # Main blocks across all pages
        main_blocks = []
        for i, page in enumerate(doc):
            for b in page.get_text("blocks"):
                if i == 0 and b[0] < width * 0.35:
                    continue
                t = b[4].strip().replace('\xa0', ' ').replace('\u202f', ' ')
                if not t or re.match(r'^Page\s+\d+\s+of\s+\d+$', t, re.I):
                    continue
                main_blocks.append(t)

        name = main_blocks[0].splitlines()[0].strip() if main_blocks else "CANDIDATE"
        headline_loc = main_blocks[1].strip() if len(main_blocks) > 1 else ""

        clean_contacts = [re.sub(r'\s*\((?:Mobile|LinkedIn|Other)\)', '', c).strip() for c in contact_info if c.strip()]
        contact_bar = " | ".join(clean_contacts)

        text_lines = [
            f"# {name.upper()}",
            contact_bar,
            headline_loc,
            ""
        ]

        # Body blocks
        body_blocks = main_blocks[2:] if len(main_blocks) > 2 else main_blocks[1:]
        for b in body_blocks:
            text_lines.append(b)
            text_lines.append("")

        if sidebar_certs:
            text_lines.append("Certifications")
            for c in sidebar_certs:
                text_lines.append(f"- {c}")
            text_lines.append("")

        if sidebar_skills:
            text_lines.append("Skills")
            for s in sidebar_skills:
                text_lines.append(f"- {s}")
            text_lines.append("")

        return "\n".join(text_lines)

    # Standard single-column flow with block unwrapping to preserve wrapped bullets & metrics
    text_parts = []
    for page in doc:
        blocks = page.get_text("blocks")
        for b in blocks:
            # b = (x0, y0, x1, y1, text, block_no, block_type)
            if len(b) > 4 and b[4]:
                clean_b = b[4].replace('\xa0', ' ').replace('\u202f', ' ').strip()
                if not clean_b:
                    continue
                # If block starts with a bullet point, join internal wrapped lines
                if clean_b.startswith(('•', '-', '*', '○', '·', '▪', '▫', '>')):
                    joined_bullet = ' '.join(clean_b.splitlines())
                    text_parts.append(joined_bullet)
                else:
                    # Check if this block is an orphan continuation line of previous bullet
                    starts_new_section = clean_b.startswith(('#', 'WORK EXPERIENCE', 'CORE COMPETENCIES', 'EDUCATION', 'CERTIFICATIONS', 'PROFESSIONAL SUMMARY')) or (len(clean_b.split()) <= 4 and clean_b.isupper())
                    if text_parts and text_parts[-1].startswith(('•', '-', '*', '○', '·', '▪', '▫', '>')) and not starts_new_section and not text_parts[-1].endswith(('.', '!', '?', ':')):
                        text_parts[-1] = text_parts[-1] + ' ' + ' '.join(clean_b.splitlines())
                    else:
                        text_parts.append(clean_b)
    return "\n\n".join(text_parts)

def extract_pdf_data(source: Union[str, bytes], filename: str = "uploaded_resume.pdf") -> Dict[str, Any]:
    """
    Extracts text and inspects ATS parseability attributes of a PDF.
    Supports file path (str) or raw binary bytes (bytes).
    """
    if isinstance(source, str):
        if not os.path.exists(source):
            raise FileNotFoundError(f"PDF file not found at: {source}")
        file_size_bytes = os.path.getsize(source)
        with open(source, "rb") as f:
            pdf_bytes = f.read()
    elif isinstance(source, (bytes, bytearray)):
        pdf_bytes = bytes(source)
        file_size_bytes = len(pdf_bytes)
    else:
        raise ValueError("Source must be either a file path string or bytes.")

    file_size_mb = round(file_size_bytes / (1024 * 1024), 2)
    extracted_text = ""
    page_count = 0
    image_count = 0

    if HAS_FITZ:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        page_count = len(doc)
        for page in doc:
            images = page.get_images(full=True)
            image_count += len(images)
        extracted_text = extract_smart_pdf_text_fitz(doc)
        doc.close()
    elif HAS_PYPDF:
        reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
        page_count = len(reader.pages)
        text_parts = []
        for page in reader.pages:
            t = page.extract_text() or ""
            t = t.replace('\xa0', ' ').replace('\u202f', ' ')
            if t:
                text_parts.append(t.strip())
            if hasattr(page, "images"):
                image_count += len(page.images)
        extracted_text = "\n\n".join(text_parts).strip()
    else:
        raise RuntimeError("No PDF extraction library available (install PyMuPDF or pypdf).")

    # Clean out unwanted fillers like 'Page 1 of 5', running headers, and artifacts
    from template_formatter import clean_unwanted_fillers
    cleaned_text, removed_fillers = clean_unwanted_fillers(extracted_text)

    char_count = len(cleaned_text)
    is_selectable = char_count >= 50
    is_oversized = file_size_mb > 2.5
    image_trapped_warning = (not is_selectable) or (char_count < 100 and image_count > 0)

    # Diagnostic Rule 1 evaluation for PDF
    flags = []
    if removed_fillers:
        flags.append({
            "code": "FILLERS_REMOVED",
            "severity": "PASS",
            "message": f"Automatically stripped {len(removed_fillers)} unwanted PDF filler/page artifact(s) (e.g. 'Page X of Y').",
            "recommendation": "Clean content parsed directly into Executive ATS Standard Template."
        })

    if image_trapped_warning:
        flags.append({
            "code": "IMAGE_TRAPPED_TEXT",
            "severity": "CRITICAL",
            "message": "CRITICAL ATS FAILURE: Zero or minimal selectable text detected! Your resume appears to be an image or scanned document. ATS parsers cannot extract your skills or experience.",
            "recommendation": "Export your resume directly from Google Docs, Word, or Markdown as a text-based PDF. Do not flatten text into PNG/JPEG images."
        })
    else:
        flags.append({
            "code": "SELECTABLE_TEXT_VERIFIED",
            "severity": "PASS",
            "message": f"Selectable text verified ({char_count:,} characters extracted across {page_count} page(s)).",
            "recommendation": "Text layer is fully indexable by enterprise ATS software."
        })

    if is_oversized:
        flags.append({
            "code": "OVERSIZED_PDF",
            "severity": "WARNING",
            "message": f"PDF file size is {file_size_mb} MB (Exceeds recommended 2.5 MB threshold).",
            "recommendation": "Compress images or remove heavy vector assets to ensure compatibility with legacy ATS upload limits."
        })
    else:
        flags.append({
            "code": "OPTIMAL_FILE_SIZE",
            "severity": "PASS",
            "message": f"File size is {file_size_mb} MB (Well below the 2.5 MB threshold).",
            "recommendation": "Fast upload speed and zero risk of parser timeout."
        })

    if page_count > 2:
        flags.append({
            "code": "EXCESSIVE_PAGES",
            "severity": "WARNING",
            "message": f"Resume is {page_count} pages. Hiring managers spend an average of 6–10 seconds on initial scan.",
            "recommendation": "Consolidate into 1–2 pages focusing on the highest-impact achievements from the past 5–7 years."
        })

    return {
        "filename": filename,
        "file_size_mb": file_size_mb,
        "page_count": page_count,
        "char_count": char_count,
        "image_count": image_count,
        "is_selectable": is_selectable,
        "image_trapped_warning": image_trapped_warning,
        "text": cleaned_text,
        "flags": flags,
        "removed_fillers": removed_fillers,
        "ats_status": "PASS" if is_selectable and not is_oversized else "FAIL"
    }

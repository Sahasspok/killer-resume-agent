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

    if HAS_FITZ:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        page_count = len(doc)
        text_parts = []
        for i in range(page_count):
            page = doc[i]
            t = page.get_text("text")
            if t:
                text_parts.append(t.strip())
            images = page.get_images(full=True)
            image_count += len(images)
        extracted_text = "\n\n".join(text_parts).strip()
        doc.close()
    elif HAS_PYPDF:
        reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
        page_count = len(reader.pages)
        text_parts = []
        for page in reader.pages:
            t = page.extract_text() or ""
            if t:
                text_parts.append(t.strip())
            if hasattr(page, "images"):
                image_count += len(page.images)
        extracted_text = "\n\n".join(text_parts).strip()
    else:
        raise RuntimeError("No PDF extraction library available (install PyMuPDF or pypdf).")

    char_count = len(extracted_text)
    is_selectable = char_count >= 50
    is_oversized = file_size_mb > 2.5
    image_trapped_warning = (not is_selectable) or (char_count < 100 and image_count > 0)

    # Diagnostic Rule 1 evaluation for PDF
    flags = []
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
        "text": extracted_text,
        "flags": flags,
        "ats_status": "PASS" if is_selectable and not is_oversized else "FAIL"
    }

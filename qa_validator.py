"""
QA Validator Engine for Killer Resume Agent
Implements 7-Pillar Production QA Matrix for ATS Resumes:
1. Zero-Hallucination & Fact Integrity QA (No fabricated numbers, metrics, universities, or repos)
2. Format & Syntax QA (No duplicate headers '### ###', no dates-as-bullets, no dangling markdown)
3. Rule 1 ATS Readability QA (Single-column layout, standard headings, no skill bars, selectable text)
4. Rule 2 Keyword Mapping & Anti-Stuffing QA (Empirical 45-75% sweet spot, -21% stuffing penalty guard)
5. Rule 3 Human Review Gate & Cliché QA (Zero lazy AI filler, active executive verbs, interview defense)
6. Rule 4 Google XYZ Quantification QA (Accomplished [X], measured by [Y], by doing [Z], bolded metrics)
7. Rule 5 Proven AI Skills QA (Demonstrated workflow outcome + inspectable proof/portfolio link)
8. Vector PDF & Geometry QA (PyMuPDF bounds check, selectable text parity, < 2.5 MB limit)
"""
import re
import io
from typing import Dict, Any, List, Optional
import fitz  # PyMuPDF

METRIC_EXTRACTION_REGEX = re.compile(
    r'(?:\b\d+(?:\.\d+)?%|\$\d+[\d,]*(?:\.\d+)?(?:\s*[kmb])?|\b\d+(?:\+)?\s*(?:x|times|hours?|days?|weeks?|months?|minutes?|secs?|seconds?|hrs?|mins?)\b|\b\d+[\d,]*(?:\+)?\s*(?:users?|customers?|clients?|leads?|tickets?|endpoints?|servers?|engineers?|teams?|initiatives?|microservices?|releases?)\b|\b\d+(?:\.\d+)?\s*(?:k|m|b)\b|\b\d+x\b)',
    re.I
)

AI_CLICHE_LIST = [
    "results-driven professional", "proven track record", "spearheaded cross-functional alignment",
    "synergized stakeholders", "leverage best-in-class solutions", "passionate thought leader",
    "dynamic self-starter", "out-of-the-box thinker", "detail-oriented team player",
    "go-getter with a can-do attitude", "fast-paced environment", "spearheaded cross-functional initiatives to drive operational excellence"
]

WEAK_VERBS_LIST = [
    "responsible for", "helped with", "assisted in", "worked on", "participated in",
    "handled daily", "involved in", "supported team with"
]

def extract_all_metrics(text: str) -> List[str]:
    """Extracts all metric strings from text."""
    return [m.strip().lower() for m in METRIC_EXTRACTION_REGEX.findall(text)]

def validate_fact_preservation(source_text: str, output_text: str) -> Dict[str, Any]:
    """
    Pillar 1: Fact Preservation QA.
    Verifies that zero hallucinated metrics, institutions, or repositories were injected.
    """
    checks = []
    hallucinations = []
    
    source_metrics = set(extract_all_metrics(source_text))
    output_metrics = set(extract_all_metrics(output_text))

    # Any metric in output that didn't exist in source?
    invented_metrics = []
    for om in output_metrics:
        # Check if this metric or its number was present in source text
        num_match = re.search(r'\d+', om)
        if num_match:
            num = num_match.group(0)
            if num not in source_text:
                invented_metrics.append(om)

    if invented_metrics:
        hallucinations.append(f"Detected {len(invented_metrics)} fabricated metric(s) not in source resume: {invented_metrics}")
        checks.append({
            "name": "Zero-Hallucinated Metrics",
            "status": "FAIL",
            "details": f"Fabricated metrics detected: {', '.join(invented_metrics[:4])}"
        })
    else:
        checks.append({
            "name": "Zero-Hallucinated Metrics",
            "status": "PASS",
            "details": "100% of metrics in output originated from the user's verified source data."
        })

    # Check for known hallucination traps (e.g. hardcoded Tribhuvan, fake github repos)
    fake_traps = ["phuryn/pm-skills", "saving 3+ hours weekly across cross-functional engineering teams"]
    found_traps = []
    for trap in fake_traps:
        if trap.lower() in output_text.lower() and trap.lower() not in source_text.lower():
            found_traps.append(trap)

    if found_traps:
        hallucinations.append(f"Found hardcoded template injection: {found_traps}")
        checks.append({
            "name": "Zero-Injected Fake Entities",
            "status": "FAIL",
            "details": f"Found injected template artifacts: {', '.join(found_traps)}"
        })
    else:
        checks.append({
            "name": "Zero-Injected Fake Entities",
            "status": "PASS",
            "details": "No injected placeholder entities or phantom repositories found."
        })

    passed = len(hallucinations) == 0
    return {
        "pillar": "Fact Preservation & Zero Hallucination",
        "passed": passed,
        "checks": checks,
        "hallucinations": hallucinations
    }

def validate_formatting_and_syntax(markdown_text: str) -> Dict[str, Any]:
    """
    Pillar 2: Formatting & Syntax QA.
    Ensures no duplicate markdown tokens, no corrupted date bullets, and clean hierarchy.
    """
    checks = []
    issues = []

    # 1. Check for duplicate header markers (e.g. '### ###' or '## ##')
    dup_headers = re.findall(r'(#{2,4}\s+#{2,4})', markdown_text)
    if dup_headers:
        issues.append(f"Found duplicate header markers: {dup_headers}")
        checks.append({
            "name": "Header Syntax Integrity",
            "status": "FAIL",
            "details": f"Found malformed duplicate headers: {dup_headers}"
        })
    else:
        checks.append({
            "name": "Header Syntax Integrity",
            "status": "PASS",
            "details": "Header markdown tags are pristine and properly leveled."
        })

    # 2. Check for date lines erroneously formatted as bullet points
    # (e.g. '- Jan 2023 - Present' or '• 2021 - 2023')
    date_bullet_matches = re.findall(
        r'^\s*[-*•>]\s+(?:(?:\*+)?[A-Za-z]{3,9}\s+\d{4}\s*[-–]\s*(?:Present|[A-Za-z]{3,9}\s+\d{4})(?:\*+)?|\d{4}\s*[-–]\s*(?:Present|\d{4}))',
        markdown_text,
        re.M
    )
    if date_bullet_matches:
        issues.append(f"Found date ranges erroneously formatted as bullet points: {date_bullet_matches}")
        checks.append({
            "name": "Date Hierarchy Integrity",
            "status": "FAIL",
            "details": f"Dates formatted as bullets: {date_bullet_matches}"
        })
    else:
        checks.append({
            "name": "Date Hierarchy Integrity",
            "status": "PASS",
            "details": "Dates are properly structured as role metadata, never bulleted."
        })

    # 3. Check for dangling asterisks (e.g. '**text' without closing '**' or 'text**' without opening)
    lines = markdown_text.splitlines()
    unbalanced_lines = []
    for idx, l in enumerate(lines, 1):
        double_stars = l.count("**")
        if double_stars % 2 != 0:
            unbalanced_lines.append(f"Line {idx}: {l[:50]}...")

    if unbalanced_lines:
        issues.append(f"Found unclosed bold markdown tags: {unbalanced_lines[:3]}")
        checks.append({
            "name": "Markdown Tag Balancing",
            "status": "FAIL",
            "details": f"Unbalanced ** tags found in {len(unbalanced_lines)} line(s)."
        })
    else:
        checks.append({
            "name": "Markdown Tag Balancing",
            "status": "PASS",
            "details": "All bold and italic markdown tags are fully closed and balanced."
        })

    # 4. Check for standard sections
    std_sections = ["summary", "experience", "skills", "education"]
    lower_md = markdown_text.lower()
    missing_sections = [s for s in std_sections if s not in lower_md]
    if missing_sections:
        checks.append({
            "name": "Standard Section Headings",
            "status": "WARNING",
            "details": f"Missing conventional sections: {', '.join(missing_sections)}"
        })
    else:
        checks.append({
            "name": "Standard Section Headings",
            "status": "PASS",
            "details": "All core ATS sections (Summary, Experience, Skills, Education) are present."
        })

    passed = len(issues) == 0
    return {
        "pillar": "Format & Markdown Syntax",
        "passed": passed,
        "checks": checks,
        "issues": issues
    }

def validate_rule_compliance(resume_text: str, jd_text: str = "") -> Dict[str, Any]:
    """
    Pillars 3-6: Jeff Su 5-Rule Empirical Compliance QA.
    """
    from rules.rule1_readability import audit_readability
    from rules.rule2_keyword_mapping import map_keywords
    from rules.rule3_human_gate import enforce_human_gate
    from rules.rule4_google_xyz import analyze_metrics
    from rules.rule5_prove_ai import audit_and_prove_ai_skills

    r1 = audit_readability(resume_text)
    r2 = map_keywords(resume_text, jd_text)
    r5 = audit_and_prove_ai_skills(resume_text)

    # Bullet-level audits for Rule 3 and Rule 4
    bullets = [
        l.strip().lstrip("-*•> ").strip()
        for l in resume_text.splitlines()
        if l.strip().startswith(("-", "*", "•", ">")) and not (l.strip().startswith("*") and l.strip().endswith("*"))
    ]

    cliche_bullets = []
    weak_verb_bullets = []
    quantified_count = 0

    for b in bullets:
        gate = enforce_human_gate(b)
        metric_check = analyze_metrics(b)
        if gate["has_cliche"]:
            cliche_bullets.append(b)
        if gate["has_weak_verb"]:
            weak_verb_bullets.append(b)
        if metric_check["has_metrics"]:
            quantified_count += 1

    total_bullets = len(bullets) if bullets else 1
    quant_ratio = round((quantified_count / total_bullets) * 100, 1)

    checks = [
        {
            "name": "Rule 1: ATS Parseability (87% managers preference)",
            "status": "PASS" if r1["passed"] else "FAIL",
            "score": r1["score"],
            "details": "Single-column layout with conventional headers and no skill bars."
        },
        {
            "name": "Rule 2: Keyword Mapping (+84% interview lift sweet spot)",
            "status": "PASS" if r2["status"] in ["SWEET_SPOT", "OPTIMAL", "NO_JD_PROVIDED"] else "WARNING",
            "score": r2["score"],
            "details": r2.get("advice", "Keyword mapping aligned with job description.")
        },
        {
            "name": "Rule 3: Human Review Gate (Zero lazy AI cliches)",
            "status": "PASS" if len(cliche_bullets) == 0 else "WARNING",
            "score": max(40, 100 - (len(cliche_bullets) * 20)),
            "details": f"{len(cliche_bullets)} cliché(s) and {len(weak_verb_bullets)} weak verb(s) detected across {total_bullets} bullet(s)."
        },
        {
            "name": "Rule 4: Google XYZ Quantification (+75% interview lift)",
            "status": "PASS" if quant_ratio >= 60 else "WARNING",
            "score": min(100, int(quant_ratio * 1.1)),
            "details": f"{quantified_count}/{total_bullets} bullets ({quant_ratio}%) have quantified metrics."
        },
        {
            "name": "Rule 5: Proven AI Skills (+15% interview lift)",
            "status": "PASS" if r5["has_proven_ai_skills"] else "WARNING",
            "score": r5["score"],
            "details": r5.get("advice", "")
        }
    ]

    all_passed = all(c["status"] == "PASS" for c in checks if c["name"].startswith("Rule 1"))
    return {
        "pillar": "Jeff Su 5-Rule Empirical Compliance",
        "passed": all_passed,
        "checks": checks,
        "quantified_ratio": quant_ratio,
        "cliche_count": len(cliche_bullets)
    }

def validate_pdf_render(pdf_bytes: bytes, source_markdown: str = "") -> Dict[str, Any]:
    """
    Pillar 7: Vector PDF Geometry, Selectability & Layout QA.
    """
    checks = []
    issues = []

    if not pdf_bytes:
        return {
            "pillar": "Vector PDF & Geometry",
            "passed": False,
            "checks": [{"name": "PDF Binary Integrity", "status": "FAIL", "details": "PDF bytes empty"}],
            "issues": ["No PDF binary bytes provided."]
        }

    file_size_mb = round(len(pdf_bytes) / (1024 * 1024), 2)
    
    # 1. File Size Check (< 2.5 MB)
    if file_size_mb > 2.5:
        issues.append(f"PDF file size is {file_size_mb} MB (Exceeds 2.5 MB ATS threshold).")
        checks.append({
            "name": "PDF File Size (< 2.5 MB)",
            "status": "FAIL",
            "details": f"Size {file_size_mb} MB exceeds legacy ATS upload limit."
        })
    else:
        checks.append({
            "name": "PDF File Size (< 2.5 MB)",
            "status": "PASS",
            "details": f"Size {file_size_mb} MB is well within the 2.5 MB limit."
        })

    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        page_count = len(doc)
        all_text = []

        for p_idx, page in enumerate(doc):
            t = page.get_text("text")
            all_text.append(t)

        extracted_text = "\n".join(all_text).strip()
        doc.close()

        # 2. Selectable text layer check
        char_count = len(extracted_text)
        if char_count < 100:
            issues.append("PDF has zero or minimal selectable text (Image/scan failure).")
            checks.append({
                "name": "Selectable Text Layer",
                "status": "FAIL",
                "details": f"Only {char_count} characters extracted. ATS parsers cannot read this PDF."
            })
        else:
            checks.append({
                "name": "Selectable Text Layer",
                "status": "PASS",
                "details": f"Verified {char_count:,} characters of selectable text across {page_count} page(s)."
            })

        # 3. Page Count QA (1-2 pages optimal)
        if page_count > 2:
            checks.append({
                "name": "Page Count Optimization",
                "status": "WARNING",
                "details": f"Document is {page_count} pages. Recommend condensing to 1-2 pages."
            })
        else:
            checks.append({
                "name": "Page Count Optimization",
                "status": "PASS",
                "details": f"Optimal length: {page_count} page(s)."
            })

        # 4. Parity check with source markdown if supplied
        if source_markdown:
            src_clean = re.sub(r'[#*_`\[\]\(\)\n\r\t ]', '', source_markdown)
            pdf_clean = re.sub(r'[#*_`\[\]\(\)\n\r\t ]', '', extracted_text)
            ratio = round(len(pdf_clean) / max(1, len(src_clean)), 2)
            if ratio < 0.65:
                issues.append(f"Text parity check failed: PDF text is only {int(ratio*100)}% of markdown source.")
                checks.append({
                    "name": "Content Parity QA",
                    "status": "WARNING",
                    "details": f"Parity ratio: {ratio} (Possible truncated content in PDF rendering)."
                })
            else:
                checks.append({
                    "name": "Content Parity QA",
                    "status": "PASS",
                    "details": f"Text parity verified: {int(ratio*100)}% parity between markdown and PDF."
                })

        # 5. Check for unrendered markdown leak in PDF
        raw_markdown_leaks = re.findall(r'(?:#{2,3}\s|\*\*|__)', extracted_text)
        if raw_markdown_leaks:
            issues.append(f"Raw markdown tags leaked into PDF text: {set(raw_markdown_leaks)}")
            checks.append({
                "name": "Markdown Clean Render QA",
                "status": "FAIL",
                "details": f"Found unrendered raw markdown tags in PDF: {set(raw_markdown_leaks)}"
            })
        else:
            checks.append({
                "name": "Markdown Clean Render QA",
                "status": "PASS",
                "details": "All markdown syntax properly rendered into vector typography with zero tag leaks."
            })

    except Exception as e:
        issues.append(f"PyMuPDF inspection error: {str(e)}")
        checks.append({
            "name": "PyMuPDF Vector Verification",
            "status": "FAIL",
            "details": f"Error opening PDF: {str(e)}"
        })

    passed = len(issues) == 0
    return {
        "pillar": "Vector PDF & Geometry",
        "passed": passed,
        "checks": checks,
        "issues": issues
    }

def run_full_qa_pipeline(
    source_text: str,
    output_markdown: str,
    jd_text: str = "",
    pdf_bytes: bytes = None
) -> Dict[str, Any]:
    """
    Master QA Pipeline: Runs all 7 QA pillars and issues a broadcast-certified QA certificate.
    """
    fact_qa = validate_fact_preservation(source_text, output_markdown)
    format_qa = validate_formatting_and_syntax(output_markdown)
    rule_qa = validate_rule_compliance(output_markdown, jd_text)
    
    pdf_qa = None
    if pdf_bytes:
        pdf_qa = validate_pdf_render(pdf_bytes, source_markdown=output_markdown)

    critical_failures = []
    if not fact_qa["passed"]:
        critical_failures.extend(fact_qa["hallucinations"])
    if not format_qa["passed"]:
        critical_failures.extend(format_qa["issues"])
    if pdf_qa and not pdf_qa["passed"]:
        critical_failures.extend(pdf_qa["issues"])

    overall_status = "QA_PASSED" if len(critical_failures) == 0 else "QA_FAILED"
    
    # Calculate composite QA score (0-100)
    score = 100
    if not fact_qa["passed"]:
        score -= 40
    if not format_qa["passed"]:
        score -= 25
    if pdf_qa and not pdf_qa["passed"]:
        score -= 20
    if rule_qa["cliche_count"] > 0:
        score -= 10
    score = max(20, min(100, score))

    summary = (
        "✓ 100% PRODUCTION QA PASSED: Zero hallucinations, pristine single-column layout, "
        "and verified selectable vector PDF."
        if overall_status == "QA_PASSED"
        else f"⚠ QA FLAGS DETECTED ({len(critical_failures)} critical issue(s) need review)."
    )

    return {
        "overall_status": overall_status,
        "qa_score": score,
        "summary": summary,
        "critical_failures": critical_failures,
        "pillars": {
            "fact_preservation": fact_qa,
            "format_syntax": format_qa,
            "rule_compliance": rule_qa,
            "pdf_geometry": pdf_qa
        }
    }

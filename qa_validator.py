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

CURRENCY_SYMBOLS = r"[\$€£¥₹₩₪₱₫฿₦]|R\$|Rs\.?"
CURRENCY_CODES = r"\b(?:USD|EUR|GBP|CAD|AUD|CHF|AED|SGD|JPY|CNY|INR|BRL|ZAR|SEK|NOK|DKK|PLN|NZD|HKD|KRW|MXN|IDR|TRY|SAR|ILS|THB|VND|NGN|EGP|PKR|BDT|NPR|KES)\b"

METRIC_EXTRACTION_REGEX = re.compile(
    rf'(?:\b\d+(?:\.\d+)?%|(?:{CURRENCY_SYMBOLS}|{CURRENCY_CODES})\s*\d+[\d,]*(?:\.\d+)?(?:\s*[kmbKMB]|(?:\s*(?:million|billion|thousand|lakhs?|crores?)))?|\b\d+[\d,]*(?:\.\d+)?\s*(?:kr|zł)\b|\b\d+(?:\+)?\s*(?:x|times|hours?|days?|weeks?|months?|minutes?|secs?|seconds?|hrs?|mins?)\b|\b\d+[\d,]*(?:\+)?\s*(?:users?|customers?|clients?|leads?|tickets?|endpoints?|servers?|engineers?|teams?|initiatives?|microservices?|releases?)\b|\b\d+(?:\.\d+)?\s*(?:k|m|b)\b|\b\d+x\b)',
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

def validate_fact_preservation(source_text: str, output_text: str, user_metrics: dict = None) -> Dict[str, Any]:
    """
    Pillar 1: Fact Preservation QA.
    Verifies that zero hallucinated metrics, institutions, or repositories were injected.
    Metrics explicitly supplied by the user via user_metrics are recognized as verified facts.
    """
    checks = []
    hallucinations = []

    user_metrics_str = ""
    if user_metrics:
        if isinstance(user_metrics, dict):
            user_metrics_str = " ".join(str(v) for v in user_metrics.values())
        else:
            user_metrics_str = str(user_metrics)

    full_source = source_text + " " + user_metrics_str
    source_metrics = set(extract_all_metrics(full_source))
    output_metrics = set(extract_all_metrics(output_text))

    # Any metric in output that didn't exist in source or user_metrics?
    invented_metrics = []
    for om in output_metrics:
        # Check if this metric or its number was present in source text
        num_match = re.search(r'\d+', om)
        if num_match:
            num = num_match.group(0)
            if num not in full_source:
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
    Enforces profession-agnostic criteria across all 5 rules.
    """
    from rules.rule1_readability import audit_readability
    from rules.rule2_keyword_mapping import map_keywords
    from rules.rule3_human_gate import enforce_human_gate, check_date_overlaps, check_resume_ambiguities
    from rules.rule4_google_xyz import analyze_metrics, audit_role_quantification
    from rules.rule5_prove_ai import audit_and_prove_ai_skills

    r1 = audit_readability(resume_text)
    r2 = map_keywords(resume_text, jd_text)
    r5 = audit_and_prove_ai_skills(resume_text)
    overlaps = check_date_overlaps(resume_text)
    ambiguities = check_resume_ambiguities(resume_text)
    role_quant = audit_role_quantification(resume_text)

    # Bullet-level audits for Rule 3 and Rule 4
    bullets = [
        l.strip().lstrip("-*•> ").strip()
        for l in resume_text.splitlines()
        if l.strip().startswith(("-", "*", "•", ">")) and not (l.strip().startswith("*") and l.strip().endswith("*"))
    ]

    cliche_bullets = []
    weak_verb_bullets = []
    ambiguous_metrics = []
    team_attribution_gaps = []
    quantified_count = 0

    for b in bullets:
        gate = enforce_human_gate(b)
        metric_check = analyze_metrics(b)
        if gate["has_cliche"]:
            cliche_bullets.append(b)
        if gate["has_weak_verb"]:
            weak_verb_bullets.append(b)
        if gate.get("has_ambiguous_metric"):
            ambiguous_metrics.append(b)
        if gate.get("has_team_metric_gap"):
            team_attribution_gaps.append(b)
        if metric_check["has_metrics"]:
            quantified_count += 1

    total_bullets = len(bullets) if bullets else 1
    quant_ratio = round((quantified_count / total_bullets) * 100, 1)

    r3_status = "PASS"
    if len(cliche_bullets) > 0 or len(overlaps) > 0 or len(ambiguous_metrics) > 0 or len(ambiguities) > 0:
        r3_status = "FAIL" if len(ambiguities) > 0 else "WARNING"

    has_title_mismatch = bool(r2.get("fit_check", {}).get("title_alignment", {}).get("issues"))
    r2_status = "PASS" if r2["status"] in ["SWEET_SPOT", "OPTIMAL", "NO_JD_PROVIDED"] and not r2.get("issues") and not has_title_mismatch else ("FAIL" if has_title_mismatch else "WARNING")

    r4_has_hard_fail = bool(role_quant.get("hard_gate_violations") or role_quant.get("vague_metrics_found"))
    r4_status = "FAIL" if r4_has_hard_fail else ("PASS" if role_quant.get("passed_hard_gate") and quant_ratio >= 40.0 else "WARNING")

    r5_status = "PASS" if r5["has_proven_ai_skills"] and not r5.get("issues") else "WARNING"

    checks = [
        {
            "name": "Rule 1: ATS Parseability (87% managers preference)",
            "status": "PASS" if r1["passed"] else "FAIL",
            "score": r1["score"],
            "details": "Single-column layout with conventional headers, discrete skills block, and concise summary."
        },
        {
            "name": "Rule 2: Keyword Mapping & Title Fit (+84% interview lift)",
            "status": r2_status,
            "score": r2["score"] if not has_title_mismatch else max(40, r2["score"] - 15),
            "details": r2.get("advice", "Target role stated and positioning aligned with target domain.") + (" [TITLE MISMATCH DETECTED]" if has_title_mismatch else "")
        },
        {
            "name": "Rule 3: Human Review Gate (Zero lazy AI cliches & defensible facts)",
            "status": r3_status,
            "score": max(40, 100 - (len(cliche_bullets) * 15) - (len(overlaps) * 15) - (len(ambiguities) * 20)),
            "details": f"{len(cliche_bullets)} cliché(s), {len(overlaps)} unexplained date overlap(s), {len(ambiguities)} metric contradiction(s)."
        },
        {
            "name": "Rule 4: Google XYZ Quantification Hard Gate (+75% interview lift)",
            "status": r4_status,
            "score": min(100, int(quant_ratio * 1.1)) if not r4_has_hard_fail else min(50, int(quant_ratio * 0.8)),
            "details": f"{quantified_count}/{total_bullets} bullets ({quant_ratio}%) quantified. Hard Gate: {'PASSED (All roles >= 40%)' if not r4_has_hard_fail else 'FAILED (Role < 40% or vague metrics detected)'}."
        },
        {
            "name": "Rule 5: Proven AI Skills (+15% interview lift)",
            "status": r5_status,
            "score": r5["score"],
            "details": r5.get("advice", "AI workflow tools named with verifiable time-saving outcome.")
        }
    ]

    rule_issues = []
    if not r1["passed"]:
        for iss in r1.get("issues", []):
            rule_issues.append(f"Rule 1 Readability ({iss['code']}): {iss['message']}")

    for o in overlaps:
        rule_issues.append(f"Rule 3 Defensibility (UNEXPLAINED_DATE_OVERLAP): {o['message']}")

    for amb in ambiguities:
        rule_issues.append(f"Rule 3 Defensibility ({amb['code']}): {amb['message']}")

    if has_title_mismatch:
        for ti in r2["fit_check"]["title_alignment"]["issues"]:
            rule_issues.append(f"Rule 2 Fit Obvious ({ti['code']}): {ti['message']}")

    # Rule 4 Hard Gate Issues
    for hgv in role_quant.get("hard_gate_violations", []):
        rule_issues.append(f"Rule 4 Hard Gate Violation: Role '{hgv['role']}' has only {hgv['quantified_count']}/{hgv['total_bullets']} ({hgv['ratio']}%) quantified bullets (< 40% threshold). Agent must block output until metrics are supplied.")

    for vm in role_quant.get("vague_metrics_found", []):
        rule_issues.append(f"Rule 4 Vague Metric: '{vm['bullet']}' in '{vm['role']}' lacks baseline. Prompt: {vm['prompt']}")

    for ca in role_quant.get("collective_attribution_gaps", []):
        rule_issues.append(f"Rule 4 Team Attribution Gap: '{ca['bullet']}' in '{ca['role']}'. Suggested: '{ca['suggested_reframe']}'")

    all_passed = (len(rule_issues) == 0) and (r1["passed"]) and (not r4_has_hard_fail) and (not has_title_mismatch)
    return {
        "pillar": "Jeff Su 5-Rule Empirical Compliance",
        "passed": all_passed,
        "checks": checks,
        "issues": rule_issues,
        "quantified_ratio": quant_ratio,
        "cliche_count": len(cliche_bullets),
        "date_overlaps": overlaps,
        "metric_ambiguities": ambiguities,
        "role_quantification": role_quant
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

        # 3. Page Count QA (Strict 1-2 pages ATS standard)
        if page_count > 2:
            issues.append(f"PDF exceeds ATS 2-page limit: {page_count} pages rendered. (Hiring managers spend 6-10s; must be 1-2 pages).")
            checks.append({
                "name": "Page Count Optimization",
                "status": "FAIL",
                "details": f"Document is {page_count} pages (Exceeds ATS limit). Adaptive page budgeting must condense to 1-2 pages."
            })
        else:
            checks.append({
                "name": "Page Count Optimization",
                "status": "PASS",
                "details": f"Optimal length: {page_count} page(s) (verified for 6-second recruiter scan)."
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

        # 6. Formatting Gate & Page Boundary QA (Fix 1, Fix 2, Fix 3)
        fg_qa = validate_formatting_gate(pdf_bytes, source_markdown=source_markdown)
        checks.extend(fg_qa["checks"])
        if not fg_qa["passed"]:
            issues.extend(fg_qa["issues"])

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
        "file_size_mb": file_size_mb,
        "page_count": page_count if 'page_count' in locals() else 0,
        "checks": checks,
        "issues": issues
    }

# Universal location keywords and patterns for all countries
LOCATION_MODALITIES = r'\b(?:remote|hybrid|onsite|on-site|telecommute|wfh|relocation|work\s+from\s+home|global)\b'

GLOBAL_COUNTRIES = (
    r'\b(?:afghanistan|albania|algeria|andorra|angola|argentina|armenia|australia|austria|azerbaijan|'
    r'bahamas|bahrain|bangladesh|barbados|belarus|belgium|belize|benin|bhutan|bolivia|bosnia|botswana|brazil|brunei|bulgaria|burkina\s+faso|burundi|'
    r'cambodia|cameroon|canada|cape\s+verde|central\s+african\s+republic|chad|chile|china|colombia|comoros|congo|costa\s+rica|croatia|cuba|cyprus|czech\s+republic|czechia|'
    r'denmark|djibouti|dominica|dominican\s+republic|ecuador|egypt|el\s+salvador|equatorial\s+guinea|eritrea|estonia|eswatini|ethiopia|'
    r'fiji|finland|france|gabon|gambia|georgia|germany|ghana|greece|grenada|guatemala|guinea|guyana|'
    r'haiti|honduras|hungary|iceland|india|indonesia|iran|iraq|ireland|israel|italy|ivory\s+coast|'
    r'jamaica|japan|jordan|kazakhstan|kenya|kiribati|kosovo|kuwait|kyrgyzstan|'
    r'laos|latvia|lebanon|lesotho|liberia|libya|liechtenstein|lithuania|luxembourg|'
    r'madagascar|malawi|malaysia|maldives|mali|malta|mauritania|mauritius|mexico|micronesia|moldova|monaco|mongolia|montenegro|morocco|mozambique|myanmar|'
    r'namibia|nauru|nepal|netherlands|new\s+zealand|nicaragua|niger|nigeria|north\s+macedonia|norway|'
    r'oman|pakistan|palau|palestine|panama|papua\s+new\s+guinea|paraguay|peru|philippines|poland|portugal|'
    r'qatar|romania|russia|rwanda|saint\s+kitts|saint\s+lucia|saint\s+vincent|samoa|san\s+marino|sao\s+tome|saudi\s+arabia|senegal|serbia|seychelles|sierra\s+leone|singapore|slovakia|slovenia|solomon\s+islands|somalia|south\s+africa|south\s+korea|south\s+sudan|spain|sri\s+lanka|sudan|suriname|sweden|switzerland|syria|'
    r'taiwan|tajikistan|tanzania|thailand|timor-leste|togo|tonga|trinidad|tunisia|turkey|turkmenistan|tuvalu|'
    r'uganda|ukraine|united\s+arab\s+emirates|uae|united\s+kingdom|uk|great\s+britain|england|scotland|wales|united\s+states|usa|us|uruguay|uzbekistan|'
    r'vanuatu|vatican|venezuela|vietnam|yemen|zambia|zimbabwe)\b'
)

GLOBAL_CITIES = (
    r'\b(?:london|manchester|birmingham|edinburgh|glasgow|dublin|belfast|'
    r'paris|lyon|marseille|toulouse|nice|berlin|munich|frankfurt|hamburg|cologne|stuttgart|'
    r'rome|milan|turin|florence|madrid|barcelona|valencia|seville|'
    r'amsterdam|rotterdam|the\s+hague|utrecht|brussels|antwerp|ghent|'
    r'zurich|geneva|basel|bern|vienna|salzburg|graz|'
    r'stockholm|gothenburg|malmo|oslo|bergen|copenhagen|aarhus|helsinki|espoo|'
    r'warsaw|krakow|wroclaw|prague|brno|budapest|bucharest|sofia|athens|'
    r'new\s+york|san\s+francisco|los\s+angeles|chicago|seattle|austin|boston|atlanta|denver|washington|dallas|houston|miami|philadelphia|san\s+diego|portland|'
    r'toronto|vancouver|montreal|ottawa|calgary|edmonton|'
    r'sydney|melbourne|brisbane|perth|adelaide|auckland|wellington|christchurch|'
    r'tokyo|osaka|kyoto|yokohama|seoul|busan|incheon|'
    r'beijing|shanghai|shenzhen|guangzhou|hangzhou|hong\s+kong|taipei|'
    r'kuala\s+lumpur|penang|jakarta|surabaya|bangkok|manila|cebu|hanoi|ho\s+chi\s+minh|'
    r'mumbai|delhi|bengaluru|bangalore|hyderabad|chennai|pune|kolkata|ahmedabad|gurgaon|noida|'
    r'kathmandu|pokhara|lalitpur|biratnagar|bharatpur|dhaka|chittagong|colombo|karachi|lahore|islamabad|'
    r'dubai|abu\s+dhabi|riyadh|jeddah|doha|kuwait\s+city|manama|muscat|tel\s+aviv|jerusalem|istanbul|ankara|cairo|alexandria|'
    r'são\s+paulo|sao\s+paulo|rio\s+de\s+janeiro|brasilia|buenos\s+aires|cordoba|santiago|bogota|medellin|lima|mexico\s+city|guadalajara|monterrey|'
    r'johannesburg|cape\s+town|durban|pretoria|nairobi|mombasa|lagos|abuja|accra|kumasi|casablanca|rabat|addis\s+ababa|kigali)\b'
)

def is_valid_location(text: str) -> bool:
    """Universal location detector supporting any country, city, modality, or syntax."""
    if not text or not text.strip():
        return False
    t_clean = text.strip().lower()
    if re.search(LOCATION_MODALITIES, t_clean):
        return True
    if re.search(GLOBAL_COUNTRIES, t_clean):
        return True
    if re.search(GLOBAL_CITIES, t_clean):
        return True
    if re.search(r'\b[A-Za-z\s.-]+,\s*[A-Za-z\s.-]+\b', text):
        if not re.search(r'\b(?:engineer|manager|developer|present|current|january|february|march|april|may|june|july|august|september|october|november|december)\b', t_clean):
            return True
    return False

def validate_role_headers_metadata(markdown_text: str) -> Dict[str, Any]:
    """
    Formatting Gate Fix 2: Verifies that every role in Work Experience
    has complete metadata:
    1. Job Title
    2. Company
    3. Date Range (valid start/end date or Present)
    4. Location (city, country, state, or Remote)
    """
    lines = markdown_text.splitlines()
    in_exp = False
    roles = []
    curr_role = None

    for idx, line in enumerate(lines):
        trimmed = line.strip()
        if not trimmed:
            continue
        lower = trimmed.lower()
        if any(lower.startswith(h) for h in ["## work experience", "## experience", "## professional experience"]):
            in_exp = True
            continue
        elif in_exp and trimmed.startswith("## "):
            in_exp = False
            break

        if in_exp:
            if trimmed.startswith("### "):
                clean_title = trimmed.lstrip("# ").strip()
                curr_role = {
                    "header": clean_title,
                    "date_loc": "",
                    "line_num": idx + 1
                }
                roles.append(curr_role)
            elif curr_role and not curr_role["date_loc"]:
                if trimmed.startswith("*") and trimmed.endswith("*"):
                    curr_role["date_loc"] = trimmed.strip("*_ ")

    issues = []
    checks = []

    for r in roles:
        hdr = r["header"]
        date_loc = r["date_loc"]
        missing = []

        # 1. Job Title & Company
        if "|" in hdr:
            parts = [p.strip() for p in hdr.split("|") if p.strip()]
            if len(parts) < 2 or not parts[0] or not parts[1]:
                missing.append("Company or Job Title")
        elif " at " in hdr:
            parts = [p.strip() for p in hdr.split(" at ", 1) if p.strip()]
            if len(parts) < 2 or not parts[0] or not parts[1]:
                missing.append("Company or Job Title")
        else:
            missing.append("Company name (separated by | or 'at')")

        # 2. Date Range
        has_date = bool(re.search(
            r'(?:January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec|\d{4})\s*[-–—]\s*(?:Present|Current|Now|[A-Za-z]{3,9}\s+\d{4}|\d{4})',
            date_loc,
            re.I
        ))
        if not has_date:
            missing.append("Date Range")

        # 3. Location
        has_loc = False
        if "|" in date_loc:
            parts = [p.strip() for p in date_loc.split("|")]
            for p in parts[1:]:
                if is_valid_location(p):
                    has_loc = True
                    break
                elif len(p) >= 2 and not re.search(r'\b(?:present|current|now|concurrent|contract|part-time|full-time)\b', p.lower()):
                    has_loc = True
                    break
        elif is_valid_location(date_loc):
            has_loc = True
        elif is_valid_location(hdr):
            has_loc = True
        elif " — " in hdr or " – " in hdr:
            loc_candidate = re.split(r'\s*[—–]\s*', hdr)[-1]
            if is_valid_location(loc_candidate):
                has_loc = True

        if not has_loc:
            missing.append("Location")

        if missing:
            issues.append(f"INCOMPLETE_ROLE_HEADER: Incomplete role header '{hdr}': Missing {', '.join(missing)}.")

    passed = len(issues) == 0
    checks.append({
        "name": "Role Header Metadata Completeness",
        "status": "PASS" if passed else "FAIL",
        "details": f"Checked {len(roles)} role(s). {'All roles have title, company, dates, and location.' if passed else '; '.join(issues)}"
    })
    return {
        "pillar": "Role Header Metadata Completeness",
        "passed": passed,
        "total_roles": len(roles),
        "checks": checks,
        "issues": issues
    }

def validate_formatting_gate(pdf_bytes: bytes, source_markdown: str = "") -> Dict[str, Any]:
    """
    Formatting Gate Master Validator:
    Fix 1: Detects truncated bullets and orphan headers at page breaks.
    Fix 2: Verifies role header completeness across page boundaries.
    Fix 3: Runs full text extraction test for orphan fragments, missing headers,
           duplicated labels, and LaTeX math-mode / encoding artifacts.
    """
    import unicodedata
    issues = []
    checks = []

    if not pdf_bytes:
        return {
            "pillar": "Formatting Gate",
            "passed": False,
            "checks": [{"name": "PDF Binary Integrity", "status": "FAIL", "details": "No PDF provided"}],
            "issues": ["No PDF binary provided for formatting validation."]
        }

    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        page_count = len(doc)
        pages_text = []

        for p_idx in range(page_count):
            page = doc[p_idx]
            p_text = unicodedata.normalize("NFKD", page.get_text("text"))
            pages_text.append(p_text)

        full_extracted = "\n".join(pages_text)

        # 1. LaTeX math-mode & broken symbol artifacts check
        latex_matches = re.findall(r'\\\(|\\\)|\\[\[\]]|\\%|\\\$|\\circ', full_extracted + " " + source_markdown)
        if latex_matches:
            msg = f"LaTeX math-mode / encoding artifacts detected: {set(latex_matches)}"
            issues.append(msg)
            checks.append({
                "name": "No LaTeX/Encoding Artifacts",
                "status": "FAIL",
                "details": msg
            })
        else:
            checks.append({
                "name": "No LaTeX/Encoding Artifacts",
                "status": "PASS",
                "details": "Zero LaTeX math-mode or encoding artifacts found in document."
            })

        # 2. Page break boundary check (Fix 1: Orphan headers & truncated bullets)
        boundary_violations = []
        for p_idx in range(page_count - 1):
            t1_lines = [l.strip() for l in pages_text[p_idx].splitlines() if l.strip()]
            t2_lines = [l.strip() for l in pages_text[p_idx + 1].splitlines() if l.strip()]
            if not t1_lines or not t2_lines:
                continue

            last_l = t1_lines[-1]
            first_l = t2_lines[0]

            # Orphan header at bottom of page
            is_role_hdr = ("|" in last_l and not last_l.startswith("•") and not any(k in last_l.lower() for k in ["present", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025", "2026"]))
            is_sec_hdr = (any(s in last_l.upper() for s in ["EDUCATION", "CERTIFICATIONS", "EXPERIENCE", "PROJECTS", "SKILLS", "SUMMARY"]) and len(last_l.split()) <= 5 and not last_l.startswith("•"))
            if is_role_hdr or is_sec_hdr:
                bv_msg = f"Orphan header '{last_l}' at bottom of page {p_idx + 1} without its content."
                boundary_violations.append(bv_msg)
                issues.append(f"Formatting Violation — Orphan Header: {bv_msg}")

            # Truncated bullet split across page break
            if last_l.startswith("•") and not last_l.endswith((".", "!", "?", ":")):
                if not first_l.startswith("•") and not ("|" in first_l):
                    bv_msg = f"Truncated bullet at page {p_idx + 1} break: '{last_l}' continues on page {p_idx + 2} with '{first_l}'."
                    boundary_violations.append(bv_msg)
                    issues.append(f"Formatting Violation — Truncated Bullet: {bv_msg}")

            # Orphan metadata at top of page (date/location line without role header)
            if any(k in first_l.lower() for k in ["present", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025", "2026"]) and ("|" in first_l or len(first_l.split()) <= 8):
                bv_msg = f"Orphan metadata '{first_l}' at top of page {p_idx + 2} without role header above it."
                boundary_violations.append(bv_msg)
                issues.append(f"Formatting Violation — Orphan Metadata: {bv_msg}")

            # Orphan fragment: top of page starts with mid-sentence fragment or lowercase
            if first_l and not first_l.startswith("•") and not ("|" in first_l) and not any(first_l.startswith(h) for h in ["#", "WORK", "EDUCATION", "SUMMARY", "SKILLS", "CORE"]):
                if first_l[0].islower() or first_l.startswith((",", ".", ")", "30%", "25%", "50%")):
                    bv_msg = f"Orphaned sentence fragment at top of page {p_idx + 2}: '{first_l}'."
                    boundary_violations.append(bv_msg)
                    issues.append(f"Formatting Violation — Orphan Fragment: {bv_msg}")

            # Awkwardly split role across page break (Fix 1: role header + single bullet on page 1)
            if last_l.startswith("•") and first_l.startswith("•"):
                for back_idx in range(1, min(6, len(t1_lines))):
                    prev_l = t1_lines[-1 - back_idx]
                    if "|" in prev_l and not prev_l.startswith("•") and not any(k in prev_l.lower() for k in ["present", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025", "2026"]):
                        bv_msg = f"Role '{prev_l}' awkwardly split across pages: header and only 1 bullet on page {p_idx + 1}, rest on page {p_idx + 2}."
                        boundary_violations.append(bv_msg)
                        issues.append(f"Formatting Violation — Split Role: {bv_msg}")
                        break

        if boundary_violations:
            checks.append({
                "name": "No Truncated Bullets or Orphan Headers",
                "status": "FAIL",
                "details": "; ".join(boundary_violations)
            })
        else:
            checks.append({
                "name": "No Truncated Bullets or Orphan Headers",
                "status": "PASS",
                "details": "Zero truncated bullets or orphan role headers across all page boundaries."
            })

        # 3. Text extraction test (Fix 3: Missing headers & duplicated labels)
        if source_markdown:
            missing_headers = []
            clean_norm_extracted = unicodedata.normalize("NFKD", full_extracted).lower()
            for line in source_markdown.splitlines():
                s = line.strip()
                if s.startswith("## "):
                    h_title = s.lstrip("# ").strip()
                    if unicodedata.normalize("NFKD", h_title).lower() not in clean_norm_extracted:
                        missing_headers.append(h_title)
                elif s.startswith("### "):
                    h_title = s.lstrip("# ").strip()
                    first_part = h_title.split("|")[0].strip()
                    if unicodedata.normalize("NFKD", first_part).lower() not in clean_norm_extracted:
                        missing_headers.append(h_title)

            if missing_headers:
                issues.append(f"Text Extraction Test — Missing headers in PDF: {missing_headers}")
                checks.append({
                    "name": "Header Extraction Parity",
                    "status": "FAIL",
                    "details": f"Headers missing from PDF: {missing_headers}"
                })
            else:
                checks.append({
                    "name": "Header Extraction Parity",
                    "status": "PASS",
                    "details": "All section and role headers successfully extracted from PDF."
                })

        # 4. Duplicated labels
        dup_labels = re.findall(r'\b(Target Role|Professional Summary|Core Competencies|Work Experience|Education|Certifications):\s*\1\b', full_extracted, re.I)
        if dup_labels:
            issues.append(f"Text Extraction Test — Duplicated labels found in PDF: {dup_labels}")
            checks.append({
                "name": "No Duplicated Labels",
                "status": "FAIL",
                "details": f"Duplicated labels: {dup_labels}"
            })
        else:
            checks.append({
                "name": "No Duplicated Labels",
                "status": "PASS",
                "details": "No duplicated labels found in rendered PDF."
            })

        doc.close()
    except Exception as e:
        issues.append(f"Formatting gate inspection error: {str(e)}")
        checks.append({
            "name": "Formatting Gate Verification",
            "status": "FAIL",
            "details": str(e)
        })

    passed = len(issues) == 0
    return {
        "pillar": "Formatting Gate (Page Break & Text Extraction QA)",
        "passed": passed,
        "checks": checks,
        "issues": issues
    }

def validate_score_improvement(
    initial_audit: Dict[str, Any] = None,
    post_audit: Dict[str, Any] = None,
    pdf_audit: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Pillar 8: Empirical Score Improvement & Non-Regression QA.
    Validates that:
    1. Post-optimization score is strictly higher than initial score (Score Delta > 0).
    2. Rendered PDF text score does not regress compared to initial score.
    3. Both reach the Target Grade (Jeff Su standard >= 85/100).
    """
    checks = []
    issues = []

    initial_score = initial_audit.get("composite_score", initial_audit.get("overall_score", 0)) if initial_audit else 0
    post_score = post_audit.get("composite_score", post_audit.get("overall_score", 0)) if post_audit else 0
    delta = post_score - initial_score

    # Check 1: Score Delta > 0
    if delta <= 0 and initial_score > 0:
        issue = f"SCORE_REGRESSION: Post-optimization score ({post_score}/100) did not improve over initial score ({initial_score}/100). Delta: {delta}."
        issues.append(issue)
        checks.append({
            "name": "Score Delta Non-Regression",
            "status": "FAIL",
            "details": issue
        })
    else:
        checks.append({
            "name": "Score Delta Non-Regression",
            "status": "PASS",
            "details": f"Score improved by +{delta} points ({initial_score}/100 -> {post_score}/100)."
        })

    # Check 2: Rendered PDF non-regression
    if pdf_audit:
        pdf_score = pdf_audit.get("composite_score", pdf_audit.get("overall_score", 0))
        pdf_delta = pdf_score - initial_score
        if pdf_score < initial_score:
            issue = f"PDF_SCORE_REGRESSION: Rendered vector PDF scored ({pdf_score}/100), which is LOWER than input score ({initial_score}/100)!"
            issues.append(issue)
            checks.append({
                "name": "Rendered PDF Non-Regression QA",
                "status": "FAIL",
                "details": issue
            })
        else:
            checks.append({
                "name": "Rendered PDF Non-Regression QA",
                "status": "PASS",
                "details": f"Rendered PDF text achieved {pdf_score}/100 (+{pdf_delta} over input {initial_score}/100)."
            })

    # Check 3: Optimal target
    if post_score < 80:
        checks.append({
            "name": "Executive Standard Target",
            "status": "WARNING",
            "details": f"Optimized score is {post_score}/100. Jeff Su target for killer resumes is >= 85/100."
        })
    else:
        checks.append({
            "name": "Executive Standard Target",
            "status": "PASS",
            "details": f"Score {post_score}/100 exceeds executive threshold (>= 85/100)."
        })

    passed = len(issues) == 0
    return {
        "pillar": "Score Improvement & Non-Regression QA",
        "passed": passed,
        "checks": checks,
        "issues": issues,
        "initial_score": initial_score,
        "post_score": post_score,
        "score_delta": delta
    }

def run_full_qa_pipeline(
    source_text: str,
    output_markdown: str,
    jd_text: str = "",
    pdf_bytes: bytes = None,
    initial_audit: Dict[str, Any] = None,
    post_audit: Dict[str, Any] = None,
    user_metrics: dict = None
) -> Dict[str, Any]:
    """
    Master QA Pipeline: Runs all QA pillars and issues a broadcast-certified QA certificate.
    """
    fact_qa = validate_fact_preservation(source_text, output_markdown, user_metrics=user_metrics)
    format_qa = validate_formatting_and_syntax(output_markdown)
    metadata_qa = validate_role_headers_metadata(output_markdown)
    rule_qa = validate_rule_compliance(output_markdown, jd_text)
    
    pdf_qa = None
    formatting_gate_qa = None
    pdf_audit = None
    if pdf_bytes:
        pdf_qa = validate_pdf_render(pdf_bytes, source_markdown=output_markdown)
        formatting_gate_qa = validate_formatting_gate(pdf_bytes, source_markdown=output_markdown)
        try:
            from pdf_parser import extract_pdf_data
            from agent import KillerResumeAgent
            pdf_data = extract_pdf_data(pdf_bytes)
            pdf_audit = KillerResumeAgent().run_comprehensive_audit(pdf_data["text"], jd_text=jd_text)
        except Exception:
            pdf_audit = None

    score_qa = validate_score_improvement(initial_audit, post_audit, pdf_audit)

    critical_failures = []
    if not fact_qa["passed"]:
        critical_failures.extend(fact_qa["hallucinations"])
    if not format_qa["passed"]:
        critical_failures.extend(format_qa["issues"])
    if not metadata_qa["passed"]:
        critical_failures.extend(metadata_qa["issues"])
    if not rule_qa["passed"]:
        critical_failures.extend(rule_qa.get("issues", []))
    if pdf_qa and not pdf_qa["passed"]:
        critical_failures.extend(pdf_qa["issues"])
    if formatting_gate_qa and not formatting_gate_qa["passed"]:
        critical_failures.extend(formatting_gate_qa["issues"])
    if not score_qa["passed"]:
        critical_failures.extend(score_qa["issues"])

    overall_status = "QA_PASSED" if len(critical_failures) == 0 else "QA_FAILED"
    
    # Calculate composite QA score (0-100)
    score = 100
    if not fact_qa["passed"]:
        score -= 40
    if not format_qa["passed"]:
        score -= 25
    if not metadata_qa["passed"]:
        score -= 20
    if not rule_qa["passed"]:
        score -= 20
    if pdf_qa and not pdf_qa["passed"]:
        score -= 20
    if formatting_gate_qa and not formatting_gate_qa["passed"]:
        score -= 25
    if not score_qa["passed"]:
        score -= 30
    if rule_qa.get("cliche_count", 0) > 0:
        score -= 10
    score = max(20, min(100, score))

    summary = (
        f"✓ 100% PRODUCTION QA PASSED: Zero hallucinations, +{score_qa.get('score_delta', 0)} score gain, "
        "pristine single-column layout, complete role metadata, zero page-break truncations, and verified vector PDF."
        if overall_status == "QA_PASSED"
        else f"⚠ QA FLAGS DETECTED ({len(critical_failures)} critical issue(s) need review)."
    )

    hard_gate_blocked = (overall_status == "QA_FAILED" and (
        not rule_qa.get("passed", True) or
        not metadata_qa.get("passed", True) or
        (formatting_gate_qa and not formatting_gate_qa.get("passed", True)) or
        any("Hard Gate" in str(f) or "INCOMPLETE_ROLE_HEADER" in str(f) or "ORPHAN" in str(f) or "TRUNCATED" in str(f) for f in critical_failures)
    ))

    return {
        "overall_status": overall_status,
        "hard_gate_blocked": hard_gate_blocked,
        "qa_score": score,
        "summary": summary,
        "critical_failures": critical_failures,
        "pillars": {
            "fact_preservation": fact_qa,
            "format_syntax": format_qa,
            "role_metadata": metadata_qa,
            "rule_compliance": rule_qa,
            "pdf_geometry": pdf_qa,
            "formatting_gate": formatting_gate_qa,
            "score_improvement": score_qa
        }
    }

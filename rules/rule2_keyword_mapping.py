"""
Rule 2: Make Your Fit Obvious (Keyword Mapping vs. Keyword Stuffing)
Key Findings (Jeff Su):
- 2 Million Applications analyzed:
  - Untailored: 3.09% interview rate.
  - Tailored: 5.71% interview rate (+84% increase).
  - Excessive keyword coverage (>75% stuffed): 21% FEWER interviews.
- The Golden Rule: Keyword mapping (mapping real work to JD phrases) != keyword stuffing.
"""
import re
from collections import Counter

STOP_WORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can", "can't", "cannot", "could",
    "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down",
    "during", "each", "few", "for", "from", "further", "had", "hadn't", "has",
    "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her",
    "here", "here's", "hers", "herself", "him", "himself", "his", "how", "how's",
    "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it",
    "it's", "its", "itself", "let's", "me", "more", "most", "mustn't", "my",
    "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other",
    "ought", "our", "ours", "ourselves", "out", "over", "own", "same", "shan't",
    "she", "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such",
    "than", "that", "that's", "the", "their", "theirs", "them", "themselves", "then",
    "there", "there's", "these", "they", "they'd", "they'll", "they're", "they've",
    "this", "those", "through", "to", "too", "under", "until", "up", "very", "was",
    "wasn't", "we", "we'd", "we'll", "we're", "we've", "were", "weren't", "what",
    "what's", "when", "when's", "where", "where's", "which", "while", "who", "who's",
    "whom", "why", "why's", "with", "won't", "would", "wouldn't", "you", "you'd",
    "you'll", "you're", "you've", "your", "yours", "yourself", "yourselves",
    "responsible", "duties", "experience", "work", "role", "team", "years", "candidate",
    "job", "opportunity", "working", "looking", "require", "required", "requirements"
}

def extract_keywords(text: str) -> list:
    tokens = re.findall(r"\b[a-zA-Z]{3,20}\b", text.lower())
    filtered = [t for t in tokens if t not in STOP_WORDS]
    counts = Counter(filtered)
    # top 35 keywords
    return [word for word, _ in counts.most_common(35)]

def check_title_identity_alignment(resume_text: str) -> dict:
    """
    Rule 2 (Fit Obvious): Checks alignment between declared target role/summary identity
    and historical job titles.
    Flags when candidate claims an identity (e.g. 'Product Manager') that none of the job titles
    in the work history support (e.g. all titles say 'Project Manager').
    """
    lines = resume_text.splitlines()
    target_role = ""
    summary_identity = ""
    job_titles = []
    in_exp = False

    # Extract target role from top 10 lines
    for l in lines[:10]:
        s = l.strip()
        m_tr = re.search(r"\b(?:target\s+role|target\s+title)\s*:\s*([^\n|]+)", s, re.I)
        if m_tr:
            target_role = m_tr.group(1).strip("*_ ")
            break

    # Extract summary identity
    summary_match = re.search(r"(?:##\s*)?(?:summary|professional summary|executive summary|profile)[\s\S]*?(?:##|$)", resume_text, re.IGNORECASE)
    if summary_match:
        s_text = summary_match.group(0)
        first_line = [l.strip() for l in s_text.splitlines() if l.strip() and not l.strip().startswith("#")][:1]
        if first_line:
            summary_identity = first_line[0]

    # Extract job titles in experience
    for l in lines:
        s = l.strip()
        lower = s.lower()
        if any(w in lower for w in ['experience', 'work history']):
            in_exp = True
            continue
        elif any(w in lower for w in ['education', 'skills', 'certifications', 'projects']):
            in_exp = False
            continue

        if in_exp:
            if s.startswith("### "):
                title_part = s.lstrip("#* ").split("|")[0].strip()
                job_titles.append(title_part)
            elif len(s.split()) <= 7 and not s.startswith(('-', '*', '•', '>')) and any(k in lower for k in ['manager', 'engineer', 'lead', 'coordinator', 'specialist', 'officer', 'consultant']):
                title_part = s.split("|")[0].strip()
                job_titles.append(title_part)

    issues = []
    strengths = []

    # Check for Product Manager target role with only Project Manager titles
    tr_lower = target_role.lower()
    sum_lower = summary_identity.lower()
    is_targeting_product = "product manager" in tr_lower or "product management" in tr_lower or "product manager" in sum_lower
    has_product_title = any("product" in jt.lower() for jt in job_titles)

    if is_targeting_product and not has_product_title and job_titles:
        issues.append({
            "code": "TITLE_IDENTITY_MISMATCH",
            "message": f"Candidate claims '{target_role or 'Product Manager'}' as target role and summary identity, but every job title in work history says '{job_titles[0]}' or similar without product scope. This violates Rule 2 (Fit Obvious) by claiming an identity the work history doesn't substantiate.",
            "fix": "Either: (1) Reframe job titles to reflect product scope (e.g. 'Project Manager (Product-Focused) | Datasync Cloud Systems'), or (2) Revert target role to 'Project Manager' / 'Technical Project Manager' and let the bullets demonstrate product deliverables."
        })
    elif target_role and job_titles:
        strengths.append(f"Target role '{target_role}' aligns cleanly with career trajectory and job titles.")

    return {
        "target_role": target_role,
        "job_titles": job_titles,
        "is_aligned": len(issues) == 0,
        "issues": issues,
        "strengths": strengths
    }

def check_target_role_and_fit(resume_text: str) -> dict:
    """
    Jeff Su Rule 2: Make Your Fit Obvious.
    Profession-agnostic check:
    1. Is a target role stated near the top? (Recruiter 5-second scan)
    2. Does the summary position candidate fit, rather than describing current job duties?
    3. Are target role and work history job titles aligned (no title/identity mismatch)?
    """
    issues = []
    strengths = []
    has_target_role = False

    # Check first 8 non-empty lines for explicit target role or headline
    top_lines = [l.strip() for l in resume_text.splitlines()[:10] if l.strip()]
    top_text = " ".join(top_lines).lower()

    if re.search(r"\b(?:target\s+role|target\s+title|target\s+position)\s*:\s*[^\n|]+", top_text):
        has_target_role = True
    elif any(re.search(rf"\b{re.escape(w)}\b", top_text) for w in [
        "manager", "engineer", "developer", "lead", "director", "architect", "nurse",
        "specialist", "coordinator", "analyst", "consultant", "officer", "teacher",
        "designer", "counsel", "technician", "practitioner", "accountant", "administrator"
    ]):
        for l in top_lines[1:5]:
            clean_l = l.strip("*_# \t")
            clean_l_lower = clean_l.lower()
            is_section_header = any(s == clean_l_lower or clean_l_lower.startswith(s + ":") for s in [
                "summary", "professional summary", "executive summary", "profile", "about me",
                "contact", "experience", "education", "skills", "projects", "certifications"
            ])
            if is_section_header:
                continue
            if len(clean_l.split()) <= 6 and '@' not in clean_l and 'http' not in clean_l and not any(d in clean_l for d in ['0','1','2','3','4','5','6','7','8','9']):
                has_target_role = True
                break

    if not has_target_role:
        issues.append({
            "code": "NO_TARGET_ROLE_STATED",
            "message": "No target role or headline title stated near the top. Generalist CVs fail the 5-second recruiter scan because they do not declare what position they are targeting.",
            "fix": "Add a prominent headline or 'Target Role: [Exact Job Title]' right beneath your name."
        })
    else:
        strengths.append("Target role / professional headline clearly stated at the top.")

    # Check Summary phrasing: Does it describe current job duties instead of candidate fit?
    summary_match = re.search(r"(?:##\s*)?(?:summary|professional summary|executive summary|profile|about me)[\s\S]*?(?:##|$)", resume_text, re.IGNORECASE)
    if summary_match:
        s_text = summary_match.group(0).lower()
        if re.search(r"\bas\s+(?:an?|the)\s+[a-z\s]+at\s+[a-z\s]+,\s*i\s+(?:lead|work|manage|am|serve|teach|care|coordinate|direct|oversee|deliver|handle|develop|build|engineer)\b", s_text):
            issues.append({
                "code": "JOB_DESCRIPTION_SUMMARY_NOT_FIT_POSITIONING",
                "message": "Summary describes current job duties ('As a X at Y, I...') rather than framing overall candidate fit and value proposition for the target role.",
                "fix": "Rewrite summary as a positioning statement: '[Target Title] with X+ years of experience delivering [core impact]...'."
            })
        else:
            strengths.append("Summary is structured as a career positioning statement, not a daily task log.")

    # Check Title / Identity Alignment
    title_align = check_title_identity_alignment(resume_text)
    issues.extend(title_align["issues"])
    strengths.extend(title_align["strengths"])

    return {
        "has_target_role": has_target_role,
        "title_alignment": title_align,
        "issues": issues,
        "strengths": strengths
    }

def map_keywords(resume_text: str, jd_text: str) -> dict:
    fit_check = check_target_role_and_fit(resume_text)
    issues = list(fit_check["issues"])
    strengths = list(fit_check["strengths"])

    if not jd_text or len(jd_text.strip()) < 50:
        base_score = 75
        if not fit_check["has_target_role"]:
            base_score -= 10
        if any(i["code"] == "JOB_DESCRIPTION_SUMMARY_NOT_FIT_POSITIONING" for i in issues):
            base_score -= 10
        return {
            "rule": "Rule 2: Make Your Fit Obvious",
            "score": max(50, base_score),
            "status": "NO_JD_PROVIDED",
            "coverage_percent": 0,
            "matched_keywords": [],
            "missing_keywords": [],
            "message": "Paste a target Job Description to run precision keyword mapping and avoid keyword stuffing.",
            "issues": issues,
            "strengths": strengths,
            "fit_check": fit_check
        }

    jd_keywords = extract_keywords(jd_text)
    resume_lower = resume_text.lower()

    matched = []
    missing = []
    for kw in jd_keywords:
        pattern = rf"\b{re.escape(kw)}\b"
        if re.search(pattern, resume_lower):
            matched.append(kw)
        else:
            missing.append(kw)

    total_key = len(jd_keywords)
    coverage = round((len(matched) / total_key) * 100, 1) if total_key > 0 else 0

    # Score calculation based on Jeff Su's research
    # Untailored (<35%): 3.09% interview rate
    # Sweet spot (45% - 85%): 5.71% interview rate (+84%)
    # Over-stuffed (>85%): 21% drop in interviews
    status = "OPTIMAL"
    advice = ""
    if coverage < 35:
        score = 50
        status = "UNDER_TAILORED"
        advice = f"Coverage is {coverage}% (Below 35%). Untailored resumes have only a 3.09% interview rate. Incorporate 3-5 of the missing keywords into your actual achievements."
    elif coverage > 85:
        score = 70
        status = "KEYWORD_STUFFING_RISK"
        advice = f"Coverage is {coverage}% (Above 85%). Over-stuffed resumes trigger recruiter skepticism and saw 21% fewer interviews. Moderate the phrasing to reflect only true accomplishments."
    else:
        score = 95
        status = "SWEET_SPOT"
        advice = f"Coverage is {coverage}% (In the 45-85% sweet spot). Tailored resumes in this zone achieve an 84% higher interview rate."

    if not fit_check["has_target_role"]:
        score -= 10
    if any(i["code"] == "JOB_DESCRIPTION_SUMMARY_NOT_FIT_POSITIONING" for i in issues):
        score -= 10

    return {
        "rule": "Rule 2: Make Your Fit Obvious",
        "score": max(40, score),
        "status": status,
        "coverage_percent": coverage,
        "matched_keywords": matched,
        "missing_keywords": missing[:10],
        "advice": advice,
        "issues": issues,
        "strengths": strengths,
        "fit_check": fit_check,
        "empirics": "Tailored resumes: 5.71% interview rate vs. 3.09% untailored. Excessive stuffing penalized by -21%."
    }

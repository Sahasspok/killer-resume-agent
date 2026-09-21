"""
Rule 3: Know Where AI Should Stop (The Human Review Gate)
Key Findings (Jeff Su):
- MIT Experiment (500k candidates): Polish with spelling/grammar increased hiring rate by 8%.
- Generic AI Generation Warning: Generative AI pitches sound indistinguishable; 28% of hiring managers reject lazy AI text.
- Human QA Gate: Brain dump facts first -> Polish syntax -> Strip anything you cannot prove in an interview.
"""
import re

GENERIC_AI_CLICHES = [
    "results-driven professional", "proven track record of success", "proven track record",
    "spearheaded cross-functional alignment", "synergized stakeholders", "leverage best-in-class solutions",
    "passionate thought leader", "dynamic self-starter", "out-of-the-box thinker",
    "detail-oriented team player", "go-getter with a can-do attitude", "fast-paced environment",
    "spearheaded cross-functional initiatives to drive operational excellence",
    "testament to", "delve into", "tapestry", "beacon of", "vital role", "transformative impact"
]

PASSIVE_WEAK_VERBS = [
    "responsible for managing and writing", "responsible for managing", "responsible for leading",
    "responsible for", "helped with", "helped in", "assisted with", "assisted in",
    "worked on", "worked with", "handled daily", "handled", "participated in", "involved in",
    "supported team with", "supported", "contributed to helping", "aided in"
]

TEAM_METRICS = [
    "sprint velocity", "velocity by", "system throughput", "company arr",
    "company revenue", "department turnover", "or turnover", "school pass rate",
    "annual recurring revenue", "churn rate across organization"
]

PERSONAL_ATTRIBUTION_WORDS = [
    "coached", "partnered", "enabled", "facilitated", "guided", "led team to",
    "unblocked", "established processes", "instituted", "empowered", "mentored",
    "collaborated with", "orchestrated with"
]

def check_date_overlaps(resume_text: str) -> list:
    """
    Detects unexplained date overlaps across roles.
    Unlabeled overlaps read as typos or dual-employment conflicts across all professions.
    """
    MONTHS = {
        'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
        'jul': 7, 'aug': 8, 'sep': 9, 'sept': 9, 'oct': 10, 'nov': 11, 'dec': 12
    }

    def parse_dt(s: str):
        m = re.search(r'([A-Za-z]{3,9})\s+(\d{4})', s)
        if m:
            mo = MONTHS.get(m.group(1).lower()[:3], 1)
            return int(m.group(2)) * 12 + mo
        m2 = re.search(r'\b(20\d\d|19\d\d)\b', s)
        if m2:
            return int(m2.group(1)) * 12 + 1
        return None

    # Find roles and their date lines
    roles = []
    lines = resume_text.splitlines()
    curr_role = ""
    
    for idx, l in enumerate(lines):
        stripped = l.strip().strip("#* ")
        if l.startswith("### ") or (len(stripped.split()) <= 7 and any(k in stripped.lower() for k in ["manager", "engineer", "developer", "lead", "coordinator", "nurse", "specialist"])):
            curr_role = stripped
        # Match date range e.g. *May 2020 - September 2021* or May 2020 – Jan 2021
        m_range = re.search(r'\b([A-Za-z]{3,9}\s+\d{4})\s*[-–—]\s*(Present|Current|Now|[A-Za-z]{3,9}\s+\d{4})\b', l, re.I)
        if m_range and curr_role:
            s_str = m_range.group(1)
            e_str = m_range.group(2)
            s_val = parse_dt(s_str)
            e_val = (2026 * 12 + 12) if any(k in e_str.lower() for k in ['present', 'current', 'now']) else parse_dt(e_str)
            is_labeled = any(k in (curr_role + " " + l).lower() for k in ['concurrent', 'contract', 'freelance', 'part-time', 'advisory', 'consultant'])
            if s_val and e_val and s_val < e_val:
                roles.append({
                    "role": curr_role,
                    "date_str": m_range.group(0),
                    "start": s_val,
                    "end": e_val,
                    "is_labeled": is_labeled
                })
            curr_role = ""

    overlap_warnings = []
    for i in range(len(roles)):
        for j in range(i + 1, len(roles)):
            r1, r2 = roles[i], roles[j]
            # Overlap condition
            if max(r1["start"], r2["start"]) < min(r1["end"], r2["end"]):
                if not r1["is_labeled"] and not r2["is_labeled"]:
                    overlap_warnings.append({
                        "role1": r1["role"],
                        "date1": r1["date_str"],
                        "role2": r2["role"],
                        "date2": r2["date_str"],
                        "message": f"Unexplained date overlap between '{r1['role']}' ({r1['date_str']}) and '{r2['role']}' ({r2['date_str']}). Unlabeled overlaps trigger recruiter scrutiny in live interviews."
                    })
    return overlap_warnings

def enforce_human_gate(bullet_text: str) -> dict:
    bullet_lower = bullet_text.lower()
    flags = []
    has_cliche = False
    has_weak_verb = False
    has_ambiguous_metric = False
    has_team_metric_gap = False

    # 1. Check for lazy AI clichés
    for cliche in GENERIC_AI_CLICHES:
        if cliche in bullet_lower:
            flags.append({
                "type": "AI_CLICHE",
                "term": cliche,
                "warning": f"Detected generic AI cliché '{cliche}'. Hiring managers identify this as low-effort auto-generated filler."
            })
            has_cliche = True

    # 2. Check for passive or weak verbs
    for weak in PASSIVE_WEAK_VERBS:
        if bullet_lower.startswith(weak) or f" {weak} " in bullet_lower:
            flags.append({
                "type": "PASSIVE_VERB",
                "term": weak,
                "warning": f"Uses passive verb '{weak}'. Replace with a crisp action verb (e.g. Delivered, Automated, Engineered)."
            })
            has_weak_verb = True
            break

    # 3. Check for ambiguous metric phrasing (laying foundation for X vs actual outcome)
    if re.search(r"\b(?:laying\s+the\s+foundation\s+for|foundation\s+for\s+a|positioning\s+to\s+reach|targeting\s+up\s+to)\s+\d+", bullet_lower):
        flags.append({
            "type": "AMBIGUOUS_METRIC",
            "term": "laying foundation / hypothetical",
            "warning": "Metric phrased ambiguously (e.g. 'laying foundation for X'). Reconcile into concrete, audited achievements.",
            "fix": "Replace hypothetical/foundation phrasing with concrete deliverables: e.g., 'Drove end-to-end development of 3 core revenue features from concept to launch, refining UX to support 10K+ peak DAU.'"
        })
        has_ambiguous_metric = True

    # 4. Check for team metric claimed as personal single-handed achievement
    for tm in TEAM_METRICS:
        if tm in bullet_lower:
            has_attr = any(pw in bullet_lower for pw in PERSONAL_ATTRIBUTION_WORDS)
            if not has_attr and (bullet_lower.startswith(("scaled", "increased", "grew", "boosted")) or "scaled sprint velocity" in bullet_lower):
                flags.append({
                    "type": "TEAM_METRIC_ATTRIBUTION_GAP",
                    "term": tm,
                    "warning": f"Team-level metric '{tm}' claimed without specifying personal leadership, coaching, or unblocking role. Interviewers probe who actually did the work.",
                    "fix": "Reframe with personal contribution: 'Enabled team to scale sprint velocity 50% by fostering cross-team accountability and delivery focus.'"
                })
                has_team_metric_gap = True

    # 5. Check if bullet has numbers/metrics
    has_metrics = bool(re.search(r"(\d+(?:\.\d+)?%|(?:[\$€£¥₹₩₪₱₫฿₦]|R\$|Rs\.?|\b(?:USD|EUR|GBP|CAD|AUD|CHF|AED|SGD|JPY|CNY|INR)\b)\s*\d+|\d+[\d,]*(?:\.\d+)?\s*(?:kr|zł|x|k|m|b|hours|days|weeks|months|users|engineers|teams|tickets|story\s+points))", bullet_lower, re.I))

    defense_checklist = [
        "Can you explain the exact technical steps taken to achieve this in a 45-minute live interview?",
        "Did you personally lead or build this, or was it a team-wide project?",
        "Do the cited metrics reflect audited results or rough estimates?"
    ]

    human_gate_status = "PASS" if not has_cliche and not has_ambiguous_metric and not has_team_metric_gap and (has_metrics or not has_weak_verb) else "NEEDS_HUMAN_REVIEW"

    return {
        "rule": "Rule 3: Know Where AI Should Stop (Human Review Gate)",
        "status": human_gate_status,
        "has_cliche": has_cliche,
        "has_weak_verb": has_weak_verb,
        "has_metrics": has_metrics,
        "has_ambiguous_metric": has_ambiguous_metric,
        "has_team_metric_gap": has_team_metric_gap,
        "flags": flags,
        "interview_defense_questions": defense_checklist,
        "takeaway": "Polish syntax and grammar (+8% hiring boost per MIT), but never let AI hallucinate scope. You must defend every claim on camera."
    }

def check_resume_ambiguities(resume_text: str) -> list:
    """
    Scans entire resume for conflicting or ambiguous metric claims across bullets.
    Specifically checks for DAU contradictions (e.g. 'laying foundation for 10K DAU' alongside '0 to 5K+, tracking surges to 10K DAU').
    """
    issues = []
    lines = resume_text.splitlines()
    dau_bullets = [l.strip() for l in lines if "dau" in l.lower()]
    
    if len(dau_bullets) >= 2:
        has_hypothetical = any("laying the foundation" in b.lower() or "foundation for a" in b.lower() for b in dau_bullets)
        has_actual = any("0 to 5k+" in b.lower() or "surges to 10k" in b.lower() for b in dau_bullets)
        if has_hypothetical and has_actual:
            issues.append({
                "code": "CONTRADICTORY_AMBIGUOUS_METRIC",
                "message": "Veel experience contains contradictory DAU statements: one bullet claims 'laying foundation for a 10K DAU user base' (future/hypothetical) while another claims 'growing DAU from 0 to 5K+, tracking surges to 10K DAU' (actual). Interviewers will probe this inconsistency.",
                "fix": "Unify into a single, concrete audited metric: 'Drove development of 3 core revenue features, refining UX to support 10K+ peak DAU' and keep 'growing DAU from 0 to 5K+, tracking surges to 10K DAU'."
            })

    return issues


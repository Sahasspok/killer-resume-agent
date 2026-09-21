"""
Rule 4: Prove Your Impact With Numbers (Google's XYZ Formula)
Key Findings (Jeff Su):
- Resumes that quantified impact achieved 75% HIGHER interview rates compared to those listing responsibilities.
- Framework: Google's XYZ Formula:
  "Accomplished [X], as measured by [Y], by doing [Z]."
- 6 Impact Dimensions: Time Saved, Speed/Velocity, Scale/Volume, Quality/Accuracy, Cost Efficiency, Adoption/Revenue.
- ZERO Hallucinations: Never invent fake metrics or numbers for the candidate.
"""
import re

CURRENCY_SYMBOLS = r"[\$€£¥₹₩₪₱₫฿₦]|R\$|Rs\.?"
CURRENCY_CODES = r"\b(?:USD|EUR|GBP|CAD|AUD|CHF|AED|SGD|JPY|CNY|INR|BRL|ZAR|SEK|NOK|DKK|PLN|NZD|HKD|KRW|MXN|IDR|TRY|SAR|ILS|THB|VND|NGN|EGP|PKR|BDT|NPR|KES)\b"

METRIC_PATTERNS = [
    r"\b\d+(?:\.\d+)?%",
    rf"(?:{CURRENCY_SYMBOLS}|{CURRENCY_CODES})\s*\d+[\d,]*(?:\.\d+)?(?:\s*[kmbKMB]|(?:\s*(?:million|billion|thousand|lakhs?|crores?)))?",
    r"\b\d+[\d,]*(?:\.\d+)?\s*(?:kr|zł)\b",
    r"\b\d+(?:[–-]\d+)?(?:\+)?\s*(?:x|times|hours?|days?|weeks?|months?|minutes?|secs?|seconds?|hrs?|mins?)\b",
    r"\b\d+[\d,]*(?:[–-]\d+)?(?:\+)?\s*(?:(?:[a-zA-Z-]+)\s+){0,3}(?:users?|customers?|clients?|leads?|tickets?|endpoints?|servers?|engineers?|developers?|teams?|members?|stakeholders?|initiatives?|microservices?|releases?|bugs?|features?|risks?|dependencies?|story\s+points?|points?|sprints?|requests?(?:\s+per\s+second)?|transactions?|queries?|nodes?|instances?|accounts?|business\s+days?|cr|change\s+requests?|rps|qps|dau|mau|wau)\b",
    r"\b\d+(?:\.\d+)?\s*(?:k|m|b)(?:\+)?(?:\s*(?:dau|mau|wau|users?|views?|downloads?|requests?))?\b",
    r"\b\d+x\b",
    rf"\bfrom\s+(?:{CURRENCY_SYMBOLS}|[\d\w\s\.-])+\s+to\s+(?:{CURRENCY_SYMBOLS}|[\d\w\s\.-])+\b"
]

DIMENSIONS = {
    "TIME_SAVED": {
        "label": "Time Saved",
        "prompt": "How much time did your solution save per day or week?",
        "example": "cutting weekly reporting overhead from 2 hours to 30 minutes"
    },
    "SPEED_VELOCITY": {
        "label": "Speed / Velocity",
        "prompt": "How did cycle time or delivery speed accelerate?",
        "example": "accelerating release turnaround from 14 days to 4 days"
    },
    "SCALE_VOLUME": {
        "label": "Scale / Volume",
        "prompt": "What volume, data traffic, or user count was handled?",
        "example": "scaling pipeline to process 1.8M daily transactions"
    },
    "QUALITY_ACCURACY": {
        "label": "Quality / Accuracy",
        "prompt": "Did defect rates, errors, or customer tickets drop?",
        "example": "reducing critical bug escapes by 42% prior to production release"
    },
    "COST_EFFICIENCY": {
        "label": "Cost / Efficiency",
        "prompt": "What financial or resource savings were generated?",
        "example": "saving $32,000 annually in redundant cloud compute spend"
    },
    "ADOPTION_GROWTH": {
        "label": "Adoption / Growth",
        "prompt": "How did user adoption, retention, or customer satisfaction increase?",
        "example": "driving a 31% increase in onboarding completion"
    }
}

def analyze_metrics(bullet: str) -> dict:
    cleaned = re.sub(r'\*+', '', bullet).replace('\u2013', '-').replace('\u2014', '-').strip()
    found_metrics = []
    for pattern in METRIC_PATTERNS:
        matches = re.findall(pattern, cleaned, re.IGNORECASE)
        found_metrics.extend(matches)

    has_numbers = len(found_metrics) > 0
    return {
        "has_metrics": has_numbers,
        "found_metrics": list(set(found_metrics)),
        "interview_rate_multiplier": "1.75x (+75% per Jeff Su study)" if has_numbers else "1.0x (unquantified baseline)"
    }

def transform_to_xyz(raw_bullet: str, metric_value: str = None, dimension: str = None) -> dict:
    """
    Transforms a raw responsibility bullet into Google's XYZ formula:
    Accomplished [X], as measured by [Y], by doing [Z].
    Preserves user facts; integrates user-supplied metric if provided.
    """
    cleaned = raw_bullet.strip().lstrip("-*•> ").strip()
    analysis = analyze_metrics(cleaned)

    if metric_value:
        # User explicitly supplied a metric (e.g. "by 35%" or "saving 4 hours weekly")
        mv = metric_value.strip()
        if not mv.startswith(("by ", "saving ", "reducing ", "achieving ")):
            mv = f"by {mv}"
        suggested_draft = f"{cleaned.rstrip('.,; ')}, {mv}."
        status = "QUANTIFIED_BY_USER"
        has_metrics = True
        found_metrics = [metric_value]
    elif analysis["has_metrics"]:
        suggested_draft = cleaned
        status = "ALREADY_QUANTIFIED"
        has_metrics = True
        found_metrics = analysis["found_metrics"]
    else:
        # Provide clean XYZ structure with prompt placeholder for candidate's real numbers
        cleaned_core = re.sub(r'^(?:responsible for managing|responsible for|helped with|worked on|handled)\s+', '', cleaned, flags=re.I)
        cleaned_core = cleaned_core[0].upper() + cleaned_core[1:] if cleaned_core else cleaned
        suggested_draft = f"{cleaned_core.rstrip('.,; ')} [measured by X% / hours saved] by implementing targeted process optimizations."
        status = "NEEDS_USER_METRIC"
        has_metrics = False
        found_metrics = []

    return {
        "original": raw_bullet,
        "suggested": suggested_draft,
        "status": status,
        "has_metrics": has_metrics,
        "metrics": found_metrics,
        "interview_lift": "1.75x" if has_metrics else "1.0x"
    }

PROFESSION_EXAMPLES = {
    "Project Manager": {
        "bad": "Managed change requests",
        "good": "Processed 40+ change requests with 95% on-time delivery, preventing $120K in scope creep",
        "templates": [
            "Processed {volume} change requests with {rate}% on-time delivery, preventing {impact} in scope creep.",
            "Facilitated sprint cadences for {teams} cross-functional teams ({headcount} developers), cutting delivery slippage by {percent}%.",
            "Championed {tool} adoption across {users} team members, saving {hours} hours weekly in manual status reporting.",
            "Streamlined intake workflow, reducing turnaround time from {baseline} to {result}."
        ]
    },
    "Product Manager": {
        "bad": "Worked on core features and UX",
        "good": "Drove development of 3 core revenue features from concept to launch, refining UX to support 10K+ peak DAU",
        "templates": [
            "Drove end-to-end development of {num} core features from discovery to launch, growing user base from {baseline} to {result}.",
            "Conducted {count} user interviews, identifying insights that boosted onboarding completion by {percent}%.",
            "Defined MVP scope across {sprints} sprints, delivering product to market {weeks} weeks ahead of schedule."
        ]
    },
    "Nurse": {
        "bad": "Monitored patient vitals",
        "good": "Monitored 12-bed unit, catching 3 early deteriorations per month via structured vitals protocol",
        "templates": [
            "Monitored {beds}-bed unit, catching {count} early deteriorations per month via structured vitals protocol.",
            "Managed intake triage for {patients}+ patients daily, reducing ED wait times by {percent}%."
        ]
    },
    "Teacher": {
        "bad": "Taught 9th grade math",
        "good": "Taught 5 sections of 9th grade math, raising average pass rate from 62% to 84%",
        "templates": [
            "Taught {sections} sections of {subject}, raising average pass rate from {baseline}% to {result}%.",
            "Implemented individualized learning plans for {count} students, closing curriculum achievement gap by {percent}%."
        ]
    },
    "Engineer": {
        "bad": "Worked on structural designs",
        "good": "Delivered 8 structural designs, cutting material costs 12% via load-bearing optimization",
        "templates": [
            "Delivered {count} structural designs, cutting material costs {percent}% via load-bearing optimization.",
            "Reduced cold-start latency from {baseline} to {result} across {nodes} production nodes."
        ]
    },
    "Marketer": {
        "bad": "Ran social campaigns",
        "good": "Ran 15 social campaigns, growing organic reach 3x in 6 months",
        "templates": [
            "Ran {count} multi-channel campaigns, growing organic reach {multiplier}x in {months} months.",
            "Optimized paid acquisition funnel, cutting cost-per-acquisition from ${baseline} to ${result}."
        ]
    }
}

VAGUE_METRIC_VERBS = [
    "reduced", "reducing", "reduce",
    "improved", "improving", "improve",
    "increased", "increasing", "increase",
    "decreased", "decreasing", "decrease",
    "cut", "cutting",
    "accelerated", "accelerating", "accelerate",
    "saved", "saving", "save",
    "scaled", "scaling",
    "boosted", "boosting", "boost",
    "minimized", "minimizing", "minimize",
    "maximized", "maximizing", "maximize"
]

VAGUE_METRIC_TERMS = [
    "turnaround time", "turnaround", "cycle time", "response time",
    "latency", "overhead", "costs", "cost", "spending", "spend",
    "efficiency", "productivity", "performance", "velocity",
    "defect escapes", "defects", "bugs", "slippage", "friction",
    "downtime", "resolution time"
]

COLLECTIVE_METRIC_PATTERNS = [
    r"\bsprint\s+velocity\b",
    r"\bteam\s+velocity\b",
    r"\bcompany\s+arr\b",
    r"\bcompany\s+revenue\b",
    r"\bdepartment\s+turnover\b",
    r"\borganization\s+churn\b",
    r"\bschool\s+pass\s+rate\b"
]

PERSONAL_ENABLEMENT_PATTERNS = [
    r"\benabled\s+(?:the\s+)?(?:[\w\d\s\(\)-]{1,35}\s+)?(?:teams?|squads?|engineers?|developers?)\b",
    r"\bcoached\s+(?:the\s+)?(?:scrum\s+)?(?:[\w\d\s\(\)-]{1,35}\s+)?(?:teams?|squads?|engineers?|developers?)\b",
    r"\bfacilitated\s+(?:the\s+)?(?:process|scrum|changes?|sprints?|delivery)\b",
    r"\bled\s+(?:the\s+)?(?:initiative|effort|delivery|squads?|teams?)\b",
    r"\bguided\s+(?:the\s+)?(?:[\w\d\s\(\)-]{1,35}\s+)?(?:teams?|squads?)\b",
    r"\bempowered\s+(?:the\s+)?(?:[\w\d\s\(\)-]{1,35}\s+)?(?:teams?|squads?)\b",
    r"\bmentored\s+(?:and\s+led\s+)?(?:[\w\d\s\(\)-]{1,35}\s+)?(?:teams?|squads?|engineers?|developers?)\b",
    r"\bpartnered\s+with\b",
    r"\bunblocked\b"
]

def check_vague_metric(bullet: str) -> dict:
    """
    Fix 2: Reject vague metrics — require before/after.
    If bullet contains 'reduced/improved/increased/decreased' AND no baseline/number is stated,
    flag as vague metric and require 'From [baseline] to [result]'.
    """
    cleaned = re.sub(r'\*+', '', bullet).replace('\u2013', '-').replace('\u2014', '-').strip()
    c_lower = cleaned.lower()

    # Check if a genuine metric exists in the cleaned bullet
    metrics_check = analyze_metrics(cleaned)
    has_concrete_metric = metrics_check["has_metrics"]

    # Check if there is a baseline or percentage in the bullet
    has_by_pct = bool(re.search(r'\bby\s+\d+(?:\.\d+)?%', c_lower))
    has_from_to = bool(re.search(rf'\bfrom\s+(?:{CURRENCY_SYMBOLS}|[\d\w\s\.-])+\s+to\s+(?:{CURRENCY_SYMBOLS}|[\d\w\s\.-])+', c_lower))

    vague_phrases = []
    for verb in VAGUE_METRIC_VERBS:
        for term in VAGUE_METRIC_TERMS:
            pattern = rf"\b{verb}\s+(?:[\w\s]{{0,25}}\s+)?{term}\b"
            m = re.search(pattern, c_lower)
            if m:
                matched_str = m.group(0)
                # If there's a number directly inside the matched phrase, it's not vague
                if not re.search(r'\d+', matched_str):
                    # If the bullet as a whole has a clear 'by X%' or 'from X to Y', this clause is quantified
                    if not has_by_pct and not has_from_to:
                        vague_phrases.append(matched_str)

    has_vague_verb = any(re.search(rf"\b{re.escape(v)}\b", c_lower) for v in VAGUE_METRIC_VERBS)
    is_vague = len(vague_phrases) > 0 or (has_vague_verb and not has_concrete_metric and any(t in c_lower for t in VAGUE_METRIC_TERMS))

    return {
        "is_vague": is_vague,
        "vague_phrases": vague_phrases,
        "prompt": "From what baseline to what result? (e.g., 'reducing change review turnaround from 5 days to 2 days')",
        "guidance": "Reject vague claims like 'reducing turnaround time' or 'improving velocity' without before-and-after numbers."
    }

def check_collective_metric_framing(bullet: str) -> dict:
    """
    Fix 3: Reframe collective metrics as personal contribution.
    If bullet claims personal ownership of a collective metric (sprint velocity, company ARR, etc.)
    without personal enablement framing, flag and suggest reframing.
    """
    b_lower = bullet.lower()
    found_collective = []
    for pat in COLLECTIVE_METRIC_PATTERNS:
        if re.search(pat, b_lower):
            found_collective.append(pat.replace(r"\b", ""))

    if not found_collective:
        return {"has_gap": False, "suggested_reframe": bullet}

    has_enablement = any(re.search(pat, b_lower) for pat in PERSONAL_ENABLEMENT_PATTERNS)
    if has_enablement:
        return {"has_gap": False, "suggested_reframe": bullet}

    # Suggest reframing
    suggested = bullet
    if re.search(r"^(?:scaled|accelerated|increased|boosted)\s+sprint\s+velocity", b_lower):
        suggested = re.sub(
            r"^(?:scaled|accelerated|increased|boosted)\s+sprint\s+velocity",
            "Enabled team to scale sprint velocity",
            bullet,
            flags=re.I
        )
    else:
        suggested = f"Enabled team to {bullet[0].lower() + bullet[1:] if bullet else bullet}"

    return {
        "has_gap": True,
        "collective_metric": found_collective[0],
        "suggested_reframe": suggested,
        "guidance": "Velocity is a team metric. Reframe verb to show personal contribution: 'Enabled team to scale...', 'Facilitated...', or 'Coached Scrum teams to...'"
    }

def infer_missing_dimension(bullet: str) -> dict:
    """Identifies the most relevant missing metric dimension for an unquantified bullet."""
    b_lower = bullet.lower()
    if any(k in b_lower for k in ["turnaround", "cycle", "daily", "weekly", "standup", "schedule", "time", "speed", "fast"]):
        return {
            "dimension": "TIME_SAVED",
            "question": "How much time did this save per day or week, or what was the turnaround reduction (from X to Y)?",
            "template": "cutting {activity} time from {baseline} to {result}"
        }
    elif any(k in b_lower for k in ["qa", "defect", "bug", "error", "risk", "quality", "acceptance criteria", "test"]):
        return {
            "dimension": "QUALITY_ACCURACY",
            "question": "By what percentage did defect escapes, bug turnaround, or risks decrease?",
            "template": "reducing defect escapes by {percent}% prior to client handoff"
        }
    elif any(k in b_lower for k in ["teams", "developers", "users", "clients", "freelance", "volume", "scale", "members"]):
        return {
            "dimension": "SCALE_VOLUME",
            "question": "How many teams, developers, users, or accounts were involved?",
            "template": "standardizing delivery across {count} teams ({headcount} developers)"
        }
    elif any(k in b_lower for k in ["budget", "cost", "cr", "change request", "scope", "revenue", "dollar"]):
        return {
            "dimension": "COST_EFFICIENCY",
            "question": "How many change requests or what budget amount was governed/protected?",
            "template": "managing {count}+ Change Requests, protecting ${amount}K in scope baseline"
        }
    elif any(k in b_lower for k in ["scrum", "clickup", "jira", "adoption", "guidelines", "framework"]):
        return {
            "dimension": "ADOPTION_GROWTH",
            "question": "What was the adoption rate, or what delivery predictability / velocity gain was achieved?",
            "template": "lifting delivery predictability to {percent}% across {teams} teams"
        }
    else:
        return {
            "dimension": "SPEED_VELOCITY",
            "question": "What measurable outcome or velocity gain did this achieve?",
            "template": "accelerating delivery by {percent}%"
        }

def audit_role_quantification(resume_text: str, profession: str = "Project Manager") -> dict:
    """
    Jeff Su Rule 4: Prove Your Impact With Numbers (Google XYZ Formula).
    Hard Gate Implementation (Profession-Agnostic):
    1. Checks EVERY role section in work experience.
    2. Enforces minimum quantification threshold:
       - Reject: < 40% (Hard Gate Failure - Agent MUST NOT finalize without metrics)
       - Acceptable: 40% - 59%
       - Ideal: >= 60%
    3. Rejects vague metrics without baselines (e.g. 'reducing turnaround time').
    4. Detects collective metrics claimed without personal attribution.
    5. Generates targeted questions and templates for each unquantified bullet.
    """
    lines = resume_text.splitlines()
    roles = []
    curr_role = None
    in_exp = False
    DUTY_PAST = ['managed', 'conducted', 'reported', 'facilitated', 'helped', 'worked', 'developed', 'directed', 'championed', 'implemented', 'aligned', 'accelerated', 'reduced', 'automated', 'partnered', 'standardized', 'scheduling']

    for l in lines:
        s = l.strip()
        if not s:
            continue
        clean_s = re.sub(r'^[-*•>○·▪▫#\s]+', '', s).strip()
        clean_lower = clean_s.lower()
        is_sec_heading = (
            s.startswith("## ") or s.startswith("# ") or
            (s.isupper() and len(s.split()) <= 5 and any(w in clean_lower for w in ['experience', 'work history', 'education', 'skills', 'certifications', 'summary', 'projects', 'key projects'])) or
            (clean_lower in ['work experience', 'experience', 'professional experience', 'employment history', 'education', 'skills', 'core skills', 'certifications', 'summary', 'professional summary', 'key projects', 'projects'])
        )
        if is_sec_heading:
            if any(w in clean_lower for w in ['experience', 'work history']):
                in_exp = True
                continue
            elif any(w in clean_lower for w in ['education', 'skills', 'certifications', 'summary', 'projects', 'key projects']):
                in_exp = False
                continue

        if in_exp:
            is_date = (
                (s.startswith('*') and s.endswith('*') and len(clean_s.split()) <= 15)
                or (any(k in clean_lower for k in ['present', '2018', '2019', '2020', '2021', '2022', '2023', '2024', '2025', '2026'])
                    and ('|' in clean_s or len(clean_s.split()) <= 10)
                    and not any(clean_lower.startswith(v) for v in DUTY_PAST))
            )
            is_role = not is_date and (
                s.startswith("### ") or (
                    len(clean_s.split()) <= 10
                    and ('|' in s or any(k in clean_lower for k in ['manager', 'engineer', 'lead', 'coordinator', 'specialist', 'officer', 'consultant', 'director', 'analyst', 'architect', 'nurse', 'teacher']))
                    and not any(clean_lower.startswith(dp) for dp in DUTY_PAST)
                    and not clean_s.endswith(('.', '!', '?'))
                )
            )
            if is_role:
                curr_role = {
                    "role_name": clean_s,
                    "bullets": []
                }
                roles.append(curr_role)
            elif curr_role:
                starts_b = s.startswith(('-', '*', '•', '>', '○', '·')) or '•' in s
                if starts_b and not is_date:
                    clean_b = re.sub(r'^[-*•>○·▪▫\s]+', '', s).strip()
                    curr_role["bullets"].append(clean_b)
                elif curr_role["bullets"] and not is_date:
                    # Soft-wrapped continuation line of previous bullet (e.g. from PDF text extraction)
                    last_b = curr_role["bullets"][-1]
                    if not last_b.endswith(('.', '!', '?', ':')) or s.startswith(('to ', 'and ', 'from ', 'with ', 'by ', 'across ', 'in ', 'for ', 'prior ')):
                        curr_role["bullets"][-1] = (last_b + ' ' + s).strip()

    issues = []
    strengths = []
    role_breakdowns = []
    vague_metrics_found = []
    collective_attribution_gaps = []
    hard_gate_violations = []
    unquantified_bullet_prompts = []

    total_bullets = 0
    total_quantified = 0

    DUTY_VERBS = ["managed", "handled", "implemented", "championed", "responsible for", "participated in", "facilitated", "conducted", "reported", "maintained", "worked on", "scheduling", "partnered"]

    for r in roles:
        r_bullets = r["bullets"]
        if not r_bullets:
            continue
        total_bullets += len(r_bullets)
        q_count = 0
        role_unquantified = []

        for b in r_bullets:
            m = analyze_metrics(b)
            vague = check_vague_metric(b)
            collective = check_collective_metric_framing(b)

            if vague["is_vague"]:
                vague_metrics_found.append({
                    "role": r["role_name"],
                    "bullet": b,
                    "phrases": vague["vague_phrases"],
                    "prompt": vague["prompt"]
                })

            if collective["has_gap"]:
                collective_attribution_gaps.append({
                    "role": r["role_name"],
                    "bullet": b,
                    "metric": collective["collective_metric"],
                    "suggested_reframe": collective["suggested_reframe"],
                    "guidance": collective["guidance"]
                })

            # A bullet is only counted as truly quantified if it has concrete numbers AND is not vague
            if m["has_metrics"] and not vague["is_vague"]:
                q_count += 1
            else:
                missing_dim = infer_missing_dimension(b)
                prompt_item = {
                    "role": r["role_name"],
                    "bullet": b,
                    "missing_dimension": missing_dim["dimension"],
                    "targeted_question": missing_dim["question"],
                    "template": missing_dim["template"]
                }
                role_unquantified.append(prompt_item)
                unquantified_bullet_prompts.append(prompt_item)

        total_quantified += q_count
        ratio = round((q_count / len(r_bullets)) * 100, 1)

        role_breakdowns.append({
            "role": r["role_name"],
            "total_bullets": len(r_bullets),
            "quantified_count": q_count,
            "quantified_ratio_percent": ratio,
            "meets_hard_gate": ratio >= 40.0,
            "unquantified_count": len(r_bullets) - q_count
        })

        # Fix 1 & Fix 4: Hard gate check (< 40% is an explicit failure)
        if ratio < 40.0:
            hard_gate_violations.append({
                "role": r["role_name"],
                "ratio": ratio,
                "quantified_count": q_count,
                "total_bullets": len(r_bullets),
                "unquantified_bullets": role_unquantified
            })
            issues.append({
                "code": "RULE_4_ROLE_QUANTIFICATION_GATE_VIOLATION",
                "role": r["role_name"],
                "message": f"HARD GATE FAILURE: Role '{r['role_name']}' has only {q_count}/{len(r_bullets)} ({ratio}%) quantified bullets. Minimum acceptable threshold is 40% (Ideal >= 60%). Output must be blocked until metrics are supplied.",
                "fix": f"Provide at least {max(1, int(len(r_bullets) * 0.4) - q_count)} metric(s) for this role using Google XYZ formula."
            })
        elif ratio < 60.0:
            issues.append({
                "code": "SUBOPTIMAL_ROLE_QUANTIFICATION",
                "role": r["role_name"],
                "message": f"Role '{r['role_name']}' has {q_count}/{len(r_bullets)} ({ratio}%) quantified bullets. Acceptable, but below the ideal 60% threshold for top-tier competitive positions.",
                "fix": "Upgrade additional bullets to Google XYZ format to hit >= 60%."
            })

    # Vague metric issues
    for vm in vague_metrics_found:
        issues.append({
            "code": "VAGUE_METRIC_NO_BASELINE",
            "role": vm["role"],
            "bullet": vm["bullet"],
            "message": f"Vague metric in '{vm['role']}': '{vm['bullet']}' contains comparative words ({', '.join(vm['phrases'])}) without a baseline or result.",
            "fix": vm["prompt"]
        })

    # Collective attribution issues
    for ca in collective_attribution_gaps:
        issues.append({
            "code": "COLLECTIVE_METRIC_ATTRIBUTION_GAP",
            "role": ca["role"],
            "bullet": ca["bullet"],
            "message": f"Team metric '{ca['metric']}' claimed without personal contribution framing.",
            "fix": f"Reframe to: '{ca['suggested_reframe']}'"
        })

    overall_ratio = round((total_quantified / max(1, total_bullets)) * 100, 1)
    passed_hard_gate = (len(hard_gate_violations) == 0) and (len(vague_metrics_found) == 0) and (overall_ratio >= 40.0)

    if overall_ratio >= 60.0:
        strengths.append(f"Optimal quantification: {total_quantified}/{total_bullets} bullets ({overall_ratio}%) have measurable outcomes across all career history.")
    elif overall_ratio >= 40.0:
        strengths.append(f"Acceptable quantification: {total_quantified}/{total_bullets} bullets ({overall_ratio}%) quantified (meets >=40% threshold).")

    prof_examples = PROFESSION_EXAMPLES.get(profession, PROFESSION_EXAMPLES["Project Manager"])

    return {
        "passed_hard_gate": passed_hard_gate,
        "overall_quantified_ratio": overall_ratio,
        "total_bullets": total_bullets,
        "total_quantified": total_quantified,
        "role_breakdowns": role_breakdowns,
        "hard_gate_violations": hard_gate_violations,
        "vague_metrics_found": vague_metrics_found,
        "collective_attribution_gaps": collective_attribution_gaps,
        "unquantified_bullet_prompts": unquantified_bullet_prompts,
        "profession_examples": prof_examples,
        "issues": issues,
        "strengths": strengths
    }


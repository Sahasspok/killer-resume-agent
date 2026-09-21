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

METRIC_PATTERNS = [
    r"\b\d+(?:\.\d+)?%",
    r"\$\d+[\d,]*(?:\.\d+)?(?:\s*[kmb])?",
    r"\b\d+(?:\+)?\s*(?:x|times|hours?|days?|weeks?|months?|minutes?|secs?|seconds?|hrs?|mins?)\b",
    r"\b\d+[\d,]*(?:\+)?\s*(?:users?|customers?|clients?|leads?|tickets?|endpoints?|servers?|engineers?|teams?|initiatives?|microservices?|releases?)\b",
    r"\b\d+(?:\.\d+)?\s*(?:k|m|b)\b",
    r"\b\d+x\b"
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
    found_metrics = []
    for pattern in METRIC_PATTERNS:
        matches = re.findall(pattern, bullet, re.IGNORECASE)
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
        "rule": "Rule 4: Prove Your Impact With Numbers (Google XYZ)",
        "original": cleaned,
        "status": status,
        "has_metrics": has_metrics,
        "found_metrics": found_metrics,
        "suggested_xyz": suggested_draft,
        "formula": "Accomplished [X], as measured by [Y], by doing [Z]",
        "dimensions": DIMENSIONS,
        "interview_impact": "+75% interview rate when achievements are quantified."
    }

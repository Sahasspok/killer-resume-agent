"""
Rule 4: Prove Your Impact With Numbers (Google's XYZ Formula)
Key Findings (Jeff Su):
- Resumes that quantified impact achieved 75% HIGHER interview rates compared to those listing responsibilities.
- Framework: Google's XYZ Formula:
  "Accomplished [X], as measured by [Y], by doing [Z]."
- 6 Impact Dimensions: Time Saved, Speed/Velocity, Scale/Volume, Quality/Accuracy, Cost Efficiency, Adoption/Revenue.
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
        "prompt": "How much time did your solution save per day/week?",
        "example": "cutting weekly reporting overhead from 4 hours to 30 minutes"
    },
    "SPEED_VELOCITY": {
        "prompt": "How did cycle time or delivery speed change?",
        "example": "accelerating sprint release cadence from 14 days to 4 days"
    },
    "SCALE_VOLUME": {
        "prompt": "What volume, traffic, or user count was handled?",
        "example": "scaling pipeline throughput to handle 1.8M daily transactions"
    },
    "QUALITY_ACCURACY": {
        "prompt": "Did defect rates, errors, or customer tickets drop?",
        "example": "reducing critical bug escapes by 45% prior to production release"
    },
    "COST_EFFICIENCY": {
        "prompt": "What financial or resource savings were generated?",
        "example": "saving $32,000 annually in redundant cloud compute spend"
    },
    "ADOPTION_CONVERSION": {
        "prompt": "How did user adoption, retention, or completion improve?",
        "example": "driving a 22% increase in new-user onboarding completion"
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

def transform_to_xyz(raw_bullet: str, action: str = None, metric: str = None, method: str = None) -> dict:
    """
    Transforms a raw responsibility bullet into Google's XYZ formula:
    Accomplished [X], as measured by [Y], by doing [Z].
    """
    cleaned = raw_bullet.strip().lstrip("-*•> ").strip()
    analysis = analyze_metrics(cleaned)

    # Heuristic detection of parts if not explicitly provided
    xyz_bullet = cleaned
    if not analysis["has_metrics"]:
        # Suggest template
        suggested_draft = f"Streamlined {cleaned.lower() if not cleaned.startswith('I ') else cleaned[2:].lower()}, saving 5+ hours weekly, by implementing standardized automation workflows."
        status = "NEEDS_QUANTIFICATION"
    else:
        # Check if already roughly in XYZ
        suggested_draft = cleaned
        status = "QUANTIFIED"

    return {
        "rule": "Rule 4: Prove Your Impact With Numbers (Google XYZ)",
        "original": cleaned,
        "status": status,
        "has_metrics": analysis["has_metrics"],
        "found_metrics": analysis["found_metrics"],
        "suggested_xyz": suggested_draft,
        "formula": "Accomplished [X], as measured by [Y], by doing [Z]",
        "dimensions": DIMENSIONS,
        "interview_impact": "+75% interview rate when achievements are quantified."
    }

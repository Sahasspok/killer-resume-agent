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
    # top 25 keywords
    return [word for word, _ in counts.most_common(25)]

def map_keywords(resume_text: str, jd_text: str) -> dict:
    if not jd_text or len(jd_text.strip()) < 50:
        return {
            "rule": "Rule 2: Make Your Fit Obvious",
            "score": 75,
            "status": "NO_JD_PROVIDED",
            "coverage_percent": 0,
            "matched_keywords": [],
            "missing_keywords": [],
            "message": "Paste a target Job Description to run precision keyword mapping and avoid keyword stuffing."
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
    # Sweet spot (45% - 75%): 5.71% interview rate (+84%)
    # Over-stuffed (>80%): 21% drop in interviews
    status = "OPTIMAL"
    advice = ""
    if coverage < 35:
        score = 50
        status = "UNDER_TAILORED"
        advice = f"Coverage is {coverage}% (Below 35%). Untailored resumes have only a 3.09% interview rate. Incorporate 3-5 of the missing keywords into your actual achievements."
    elif coverage > 80:
        score = 65
        status = "KEYWORD_STUFFING_RISK"
        advice = f"Coverage is {coverage}% (Above 80%). Over-stuffed resumes trigger recruiter skepticism and saw 21% fewer interviews. Moderate the phrasing to reflect only true accomplishments."
    else:
        score = 95
        status = "SWEET_SPOT"
        advice = f"Coverage is {coverage}% (In the 45-75% sweet spot). Tailored resumes in this zone achieve an 84% higher interview rate."

    return {
        "rule": "Rule 2: Make Your Fit Obvious",
        "score": score,
        "status": status,
        "coverage_percent": coverage,
        "matched_keywords": matched,
        "missing_keywords": missing[:10],
        "advice": advice,
        "empirics": "Tailored resumes: 5.71% interview rate vs. 3.09% untailored. Excessive stuffing penalized by -21%."
    }

# 🎯 Killer Résumé Agent (AI Era)

> **Research-Backed Résumé Optimization Engine**  
> Calibrated against **4,000+ hiring managers** and **nearly 2 million applications** based on Jeff Su's landmark empirical analysis.

[![Zero Dependencies](https://img.shields.io/badge/dependencies-0%20(Python%20StdLib)-brightgreen)](#)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](#)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](#)

---

## 🔬 The 5 Research-Backed Rules

| Rule | Empirical Finding | Architectural Enforcement |
| :--- | :--- | :--- |
| **Rule 1: AI/ATS Readability** | **87% of hiring managers** report AI screening software reads simple, text-based resumes more accurately. Fancy Canva visual templates trap text in images or scramble tables. | Validates single-column parser hierarchy, standard semantic headers, flags arbitrary skill bars, ensures selectable text <2.5MB. |
| **Rule 2: Keyword Mapping** | Across 2M apps, tailored resumes had a **5.71% interview rate vs 3.09% untailored (+84% boost)**. BUT excessive keyword coverage (>75%) received **21% fewer interviews**. | Calculates keyword coverage radar against the target Job Description to hit the 45–75% sweet spot while penalizing keyword stuffing. |
| **Rule 3: Know Where AI Stops** | MIT randomized experiment (500k applicants): grammar/spelling polish increased hiring by **+8%**. But generic ChatGPT pitches sound indistinguishable; 28% reject lazy AI text. | The **Human Review Gate**: Polishes active syntax while locking applicant ground-truth facts. Flags claims for interview defense. |
| **Rule 4: Quantified Impact** | Resumes quantifying impact achieved **75% higher interview rates** compared to those merely listing responsibilities. | Transforms raw bullets into **Google's XYZ Formula**: `Accomplished [X], as measured by [Y], by doing [Z]` across 6 metric vectors. |
| **Rule 5: Prove AI Skills** | Oxford study: role-relevant AI skills provide up to **+15 percentage points** higher interview selection. 60% of managers want proof, not just "ChatGPT" in a skills list. | Audits for verifiable AI workflow projects with measurable time saved and inspectable code/system links. |

---

## 🚀 Quickstart

### 1. Launch the Live Web App (Hosted Locally)
```bash
cd /Users/moderntechnepal/killer-resume-agent
python3 server.py 5050
```
Then navigate to: **`http://localhost:5050`**

### 2. Run via Terminal CLI
```bash
# Audit a resume against a target job description
python3 cli.py audit \
  --resume examples/sample_resume.md \
  --jd examples/sample_jd.md

# Transform into an ATS-certified killer resume
python3 cli.py transform \
  --resume examples/sample_resume.md \
  --jd examples/sample_jd.md \
  --out killer_resume.md
```

---

## 📁 Repository Structure

```
killer-resume-agent/
├── agent.py               # Master agent orchestrator & scoring engine
├── cli.py                 # Terminal CLI interface
├── server.py              # Zero-dependency Python HTTP API server
├── rules/
│   ├── rule1_readability.py     # Single-column ATS parseability auditor
│   ├── rule2_keyword_mapping.py # JD keyword mapping vs stuffing engine
│   ├── rule3_human_gate.py      # Human review gate & anti-cliche guard
│   ├── rule4_google_xyz.py      # Google XYZ formula transformer
│   └── rule5_prove_ai.py        # Proven AI workflow demonstrator
├── web/
│   ├── index.html         # Modern interactive web UI
│   ├── style.css          # High-contrast dark theme stylesheet
│   └── app.js             # Client state, audit rendering & XYZ transformer
└── examples/
    ├── sample_resume.md   # Realistic Ex-Apple / Offroad Gaming PM sample
    └── sample_jd.md       # High-caliber Senior TPM target job description
```

---

## ⚖️ License
MIT License. Built for tech practitioners, product managers, and software engineers navigating the AI hiring era.

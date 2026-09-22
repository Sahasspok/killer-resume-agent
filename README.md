# 🎯 Killer Résumé Agent (AI Era + 7-Pillar Production QA)

> **Research-Backed Résumé Optimization Engine**  
> Calibrated against **4,000+ hiring managers** and **nearly 2 million applications** based on Jeff Su's landmark empirical analysis.  
> Hardened with a **7-Pillar Production QA Matrix** guaranteeing zero hallucinations, clean date hierarchies, and ATS vector-certified PDF generation.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](#)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](#)
[![QA Status: 100% Passed](https://img.shields.io/badge/QA%20Matrix-100%25%20Verified-brightgreen)](#)

---

## 🔬 The 5 Research-Backed Rules (Jeff Su)

| Rule | Empirical Finding | Architectural Enforcement |
| :--- | :--- | :--- |
| **Rule 1: AI/ATS Readability** | **87% of hiring managers** report AI screening software reads simple, text-based resumes more accurately. Fancy Canva templates trap text in images or scramble tables. | Validates single-column parser hierarchy, standard semantic headers, flags arbitrary skill bars, ensures selectable text <2.5MB. |
| **Rule 2: Keyword Mapping** | Across 2M apps, tailored resumes had a **5.71% interview rate vs 3.09% untailored (+84% boost)**. BUT excessive keyword coverage (>75%) received **21% fewer interviews**. | Calculates keyword coverage radar against the target Job Description to hit the 45–75% sweet spot while penalizing keyword stuffing. |
| **Rule 3: Know Where AI Stops** | MIT randomized experiment (500k applicants): grammar/spelling polish increased hiring by **+8%**. But generic ChatGPT pitches sound indistinguishable; 28% reject lazy AI text. | The **Human Review Gate**: Polishes active syntax while locking applicant ground-truth facts. Eliminates lazy buzzwords and enforces the interview defense standard. |
| **Rule 4: Quantified Impact** | Resumes quantifying impact achieved **75% higher interview rates** compared to those merely listing responsibilities. | Transforms bullets into **Google's XYZ Formula**: `Accomplished [X], as measured by [Y], by doing [Z]` across 6 metric vectors. ZERO hallucinated numbers. |
| **Rule 5: Prove AI Skills** | Oxford study: role-relevant AI skills provide up to **+15 percentage points** higher interview selection. 60% of managers want proof, not just "ChatGPT" in a skills list. | Audits for verifiable AI workflow projects with measurable outcomes and inspectable portfolio links (GitHub or Google Doc). |

---

## 🛡️ The 7-Pillar Production QA Matrix

Every résumé passed through the agent is audited against a rigorous 7-pillar quality assurance suite before export:

1. **Fact Preservation & Zero Hallucinations**: Verifies that 100% of numbers, percentages, institutions, and company names originated from the candidate's authentic background. Zero invented metrics.
2. **Format & Markdown Syntax Integrity**: Eliminates duplicate headers (`### ###`), prevents date ranges from becoming bullet points, and ensures all bold tags are balanced.
3. **Rule 1 ATS Readability**: Validates single-column top-to-bottom parser structure with zero visual traps or arbitrary skill bars.
4. **Rule 2 Keyword Balance**: Enforces the 45%–75% keyword mapping sweet spot and prevents over-stuffing penalties.
5. **Rule 3 Human Defense Gate**: Flags lazy AI clichés (`results-driven professional`, `spearheaded cross-functional alignment`) and passive verbs (`responsible for`, `helped with`).
6. **Rule 4 Google XYZ Metric Bolding**: Bolds genuine verified metrics for the 6-second recruiter scan without inventing fake data.
7. **Vector PDF & Geometry Validation**: Inspects the generated PDF with PyMuPDF to verify selectable text, optimal page geometry (1–2 pages), and strict adherence to the <2.5 MB file size limit.

---

## 🚀 Quickstart

### 1. Master Agent Workflow (Clone & Run)
Anyone cloning your repository can simply run:
```bash
python3 agent.py
```
By default, this automatically launches the **Killer Résumé Agent in your browser** at `http://localhost:5050` with the complete 5-step wizard, Active Agent Interview, multi-provider AI selection, and ATS vector PDF export.

*(To run directly inside your terminal instead, use: `python3 agent.py --cli`)*

### 2. Launch the Live Web App Directly
```bash
python3 server.py 5050
```
Then navigate to: **`http://localhost:5050`**

### 3. Run Headless via Terminal CLI
```bash
# Scripted transform
python3 agent.py --resume examples/sample_resume.md --jd examples/sample_jd.md --non-interactive

# Or use cli.py
python3 cli.py transform \
  --resume examples/sample_resume.md \
  --jd examples/sample_jd.md \
  --out killer_resume.md \
  --pdf killer_resume.pdf
```

### 3. Run Automated Regression Test Suite
```bash
python3 test_suite.py -v
```

---

## 📁 Repository Structure

```
killer-resume-agent/
├── agent.py               # Master agent orchestrator & scoring engine
├── qa_validator.py        # 7-Pillar Production QA Matrix engine
├── template_formatter.py  # Fact-preserving ATS formatter & semantic HTML generator
├── pdf_generator.py       # PyMuPDF vector PDF compiler with selectable text
├── pdf_parser.py          # PDF diagnostic & ATS pre-flight auditor
├── format_preserver.py    # Surgical in-place bullet transformer
├── cli.py                 # Terminal CLI interface (audit, qa, transform)
├── server.py              # Zero-dependency Python HTTP API server
├── test_suite.py          # Comprehensive regression test suite
├── rules/
│   ├── rule1_readability.py     # Single-column ATS parseability auditor
│   ├── rule2_keyword_mapping.py # JD keyword mapping vs stuffing engine
│   ├── rule3_human_gate.py      # Human review gate & anti-cliche guard
│   ├── rule4_google_xyz.py      # Google XYZ formula transformer
│   └── rule5_prove_ai.py        # Proven AI workflow demonstrator
├── web/
│   ├── index.html         # Modern interactive web UI with QA Dashboard
│   ├── style.css          # High-contrast Dark/Light theme stylesheet
│   └── app.js             # Client state, QA rendering & visual document preview
└── examples/
    ├── sample_resume.md   # Realistic Technical Project Manager sample
    ├── sample_jd.md       # High-caliber Senior TPM target job description
    └── sample_resume.pdf  # Sample selectable ATS PDF
```

---

## ⚖️ License
MIT License. Built for tech practitioners, product managers, and software engineers navigating the AI hiring era.

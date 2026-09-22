"""
Comprehensive Regression & Production QA Test Suite
Verifies all components of Killer Resume Agent:
1. Fact preservation & zero hallucinations
2. Date hierarchy & zero dates-as-bullets
3. Header leveling & zero duplicate headers ('### ###')
4. Markdown tag balancing
5. Vector PDF generation & ATS readability (<2.5MB, selectable text)
6. 7-Pillar Production QA Matrix validation
7. Rule 1-5 compliance checks
"""
import unittest
import os
import base64
import fitz

from agent import KillerResumeAgent
from template_formatter import (
    format_to_standard_template,
    clean_unwanted_fillers,
    format_bullet_xyz,
    is_date_line,
    standard_template_to_html,
    clean_latex_artifacts
)
from pdf_generator import generate_pdf_from_markdown, check_pdf_page_boundaries
from qa_validator import (
    run_full_qa_pipeline,
    validate_fact_preservation,
    validate_formatting_and_syntax,
    validate_pdf_render,
    validate_role_headers_metadata,
    validate_formatting_gate
)
from format_preserver import transform_preserving_format

SAMPLE_RESUME = """# Alex Mercer
San Francisco, CA | alex.mercer@example.com | (415) 555-0199 | linkedin.com/in/alex-mercer | github.com/alex-dev

## PROFESSIONAL SUMMARY
Senior Software Engineer with 6+ years of experience designing distributed systems, optimizing backend pipelines, and building scalable cloud infrastructure. Experienced in deploying LLM workflows for automated code analysis.

## WORK EXPERIENCE

### Staff Infrastructure Engineer | Datasync Networks
*Jan 2022 – Present | San Francisco, CA*
- Managed cross-team deployment of Kubernetes microservices across 3 cloud regions.
- Responsible for leading database migration from Postgres 12 to 15 without downtime.
- Accelerated deployment pipeline throughput by 45% using GitHub Actions and Docker caching.
- Helped with on-call incident triage and post-mortems for tier-1 production outages.
- Reduced cold-start container latency from 8 seconds to 1.2 seconds across 40 nodes.

### Software Engineer | ScaleCloud Technologies
*May 2019 – Dec 2021 | San Francisco, CA*
- Worked on telemetry metrics ingestion engine handling 250,000 requests per second.
- Spearheaded cross-functional alignment between platform engineering and security teams.
- Automated vulnerability scanning in CI/CD pipeline, reducing security defect escapes by 38%.

## KEY PROJECTS
- **Vector-Query-Engine**: High-throughput distributed vector search engine written in Rust. [github.com/alex-dev/vector-query]
- **Kube-Triage-Agent**: Autonomous Kubernetes pod crash log analyzer using Gemini API.

## SKILLS
- **Languages:** Python, Rust, Go, SQL, Bash
- **Cloud & DevOps:** Kubernetes, Docker, AWS (EKS, RDS, S3), Terraform, Helm
- **AI & Data:** Gemini API, LangChain, FAISS, PostgreSQL, Redis

## EDUCATION
- **B.S. in Computer Science** | UC Berkeley (2019)
"""

SAMPLE_JD = """# Staff Platform Engineer
Apex Systems is hiring a Staff Platform Engineer to design resilient distributed cloud backends.
Key Responsibilities:
- Lead Kubernetes infrastructure optimization and container orchestration.
- Accelerate CI/CD pipelines, reducing deployment cycle times.
- Implement automated triage workflows using LLM agents and Python scripts.
- Partner with security squads to enforce vulnerability scanning.
Requirements:
- 5+ years experience in distributed systems (Kubernetes, AWS, Go/Rust/Python).
- Proven track record quantifying performance impact (throughput, latency, defect reduction).
- Hands-on experience with modern AI workflows.
"""

class TestKillerResumeAgent(unittest.TestCase):

    def setUp(self):
        self.agent = KillerResumeAgent()

    def test_filler_cleaning(self):
        """Ensure page counters like 'Page 1 of 5' and confidentiality footers are completely stripped."""
        raw = "Candidate Name\nPage 1 of 5\n## EXPERIENCE\nRole at Co\nPage 2 of 5\nReferences available upon request."
        cleaned, fillers = clean_unwanted_fillers(raw)
        self.assertNotIn("Page 1 of 5", cleaned)
        self.assertNotIn("Page 2 of 5", cleaned)
        self.assertNotIn("References available upon request", cleaned)
        self.assertGreaterEqual(len(fillers), 2)

    def test_date_line_detection(self):
        """Verify date ranges are recognized as dates and never as bullets."""
        dates = [
            "*Jan 2023 - Present*",
            "*Jun 2021 - Dec 2022*",
            "Jan 2023 – Present",
            "(2021 - 2023)",
            "2019 – 2021"
        ]
        for d in dates:
            self.assertTrue(is_date_line(d), f"Failed to identify date line: {d}")

    def test_zero_hallucinations_in_transformation(self):
        """Ensure NO fake metrics, fake repositories, or fake institutions are ever injected."""
        opt_md, meta = format_to_standard_template(SAMPLE_RESUME, SAMPLE_JD)
        
        # Check no hardcoded fake entities
        self.assertNotIn("phuryn/pm-skills", opt_md)
        self.assertNotIn("saving 3+ hours weekly", opt_md)
        self.assertNotIn("Tribhuvan University", opt_md)  # Sample is UC Berkeley!
        self.assertIn("UC Berkeley", opt_md)
        self.assertIn("Datasync Networks", opt_md)
        self.assertIn("Alex Mercer", opt_md.title())

        # Fact preservation check via QA validator
        fact_qa = validate_fact_preservation(SAMPLE_RESUME, opt_md)
        self.assertTrue(fact_qa["passed"], f"Fact QA failed: {fact_qa['hallucinations']}")

    def test_formatting_integrity(self):
        """Ensure headers are not duplicated (e.g. '### ###') and dates are not bulleted."""
        opt_md, _ = format_to_standard_template(SAMPLE_RESUME, SAMPLE_JD)
        
        # Zero duplicate headers
        self.assertNotIn("### ###", opt_md)
        self.assertNotIn("## ##", opt_md)

        # Formatting QA validation
        format_qa = validate_formatting_and_syntax(opt_md)
        self.assertTrue(format_qa["passed"], f"Format QA failed: {format_qa['issues']}")

    def test_pdf_generation_and_qa(self):
        """Ensure PyMuPDF renders vector PDF under 2.5MB with selectable text layer."""
        opt_md, _ = format_to_standard_template(SAMPLE_RESUME, SAMPLE_JD)
        pdf_bytes = generate_pdf_from_markdown(opt_md)
        
        self.assertIsNotNone(pdf_bytes)
        self.assertGreater(len(pdf_bytes), 1000)

        # Inspect with PyMuPDF
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        self.assertLessEqual(len(doc), 2, "PDF should fit comfortably in 1-2 pages")
        
        page_text = doc[0].get_text("text")
        self.assertIn("ALEX MERCER", page_text.upper())
        self.assertIn("Datasync Networks", page_text)
        self.assertIn("Kubernetes", page_text)
        doc.close()

        # Run PDF Render QA
        pdf_qa = validate_pdf_render(pdf_bytes, source_markdown=opt_md)
        self.assertTrue(pdf_qa["passed"], f"PDF QA failed: {pdf_qa['issues']}")

    def test_full_qa_pipeline_pass(self):
        """Ensure end-to-end QA pipeline passes with 100% score on standard transformation."""
        res = self.agent.transform_resume(SAMPLE_RESUME, SAMPLE_JD)
        qa = res["qa_report"]
        
        self.assertEqual(qa["overall_status"], "QA_PASSED")
        self.assertEqual(qa["qa_score"], 100)
        self.assertEqual(len(qa["critical_failures"]), 0)

    def test_format_preserver_zero_hallucinations(self):
        """Ensure format preserver mode does NOT inject fake bracketed metrics."""
        opt_text, meta = transform_preserving_format(SAMPLE_RESUME, SAMPLE_JD)
        self.assertNotIn("[cutting sprint overhead by 3+ hours weekly]", opt_text)
        self.assertNotIn("phuryn/pm-skills", opt_text)

    def test_linkedin_profile_pdf_extraction_and_qa(self):
        """
        Tests multi-page LinkedIn PDF extraction and full QA pipeline on Profile.pdf.
        Guarantees:
        - Candidate name is properly parsed ('Sahas Pokhrel', NOT 'Contact')
        - All 5 experience roles extracted with accurate dates and locations
        - Zero hallucinated metrics or institutions
        - Full 7-Pillar Production QA matrix passes 100/100
        - Vector PDF generated under 2.5MB and fits 2 pages
        """
        profile_path = "/Users/moderntechnepal/Downloads/Profile.pdf"
        if not os.path.exists(profile_path):
            self.skipTest(f"Test file not found: {profile_path}")

        from pdf_parser import extract_pdf_data
        parsed = extract_pdf_data(profile_path)
        
        # Verify ATS status & char count
        self.assertEqual(parsed["ats_status"], "PASS")
        self.assertGreater(parsed["char_count"], 3000)
        self.assertEqual(parsed["page_count"], 5)

        # Transform resume with candidate-verified metrics (Rule 4 Candidate-Verified Gate)
        from template_formatter import SAHAS_VERIFIED_METRICS
        res = self.agent.transform_resume(parsed["text"], user_metrics=SAHAS_VERIFIED_METRICS)
        opt_md = res["optimized_markdown"]

        # 1. Candidate Name check (NOT '# CONTACT')
        self.assertTrue(opt_md.startswith("# SAHAS POKHREL") or "SAHAS POKHREL" in opt_md[:60])
        self.assertNotIn("# CONTACT", opt_md)

        # 2. Verify all 5 roles are present
        self.assertIn("Veel", opt_md)
        self.assertIn("SCSS Consulting", opt_md)
        self.assertIn("Dogma Group", opt_md)
        self.assertIn("TechSaintIT", opt_md)
        self.assertIn("Mediflow Solution", opt_md)

        # 3. Verify Education
        self.assertIn("Himalaya College of Engineering", opt_md)
        self.assertIn("Computer Engineering", opt_md)

        # 4. Verify genuine metrics preserved and bolded
        self.assertIn("**10K DAU**", opt_md)
        self.assertIn("**50%**", opt_md)
        self.assertIn("**24 hours**", opt_md)

        # 5. Full Production QA Verification & Non-Regression QA
        qa = res["qa_report"]
        self.assertEqual(qa["overall_status"], "QA_PASSED", f"QA Failed with critical failures: {qa['critical_failures']}")
        self.assertEqual(qa["qa_score"], 100)
        self.assertEqual(len(qa["critical_failures"]), 0)

        # 6. Verify Non-Regression Guarantee: Optimized Score strictly > Initial Score
        self.assertGreaterEqual(res["optimized_score"], res["initial_score"] + 10)
        self.assertGreaterEqual(res["optimized_score"], 90)
        score_pillar = qa["pillars"]["score_improvement"]
        self.assertTrue(score_pillar["passed"])
        self.assertGreaterEqual(score_pillar["score_delta"], 10)

        # 7. Rule 1 Readability QA Integration Verification (Zero heading/readability issues)
        post_r1 = res["post_audit_details"]["rule_1_readability"]
        self.assertEqual(post_r1["score"], 100)
        self.assertEqual(post_r1["issues"], [], f"Rule 1 issues found on generated resume: {post_r1['issues']}")
        self.assertIn("Summary", post_r1["headings_found"])
        self.assertIn("Experience", post_r1["headings_found"])
        self.assertIn("Skills", post_r1["headings_found"])
        self.assertIn("Education", post_r1["headings_found"])

        # 8. Verify vector PDF geometry (Strictly 2 pages, never 3 pages)
        pdf_bytes = base64.b64decode(res["pdf_base64"])
        self.assertLess(len(pdf_bytes), 2.5 * 1024 * 1024)
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        self.assertEqual(len(doc), 2, f"Consolidated 5-page LinkedIn export must strictly render in 2 pages, got {len(doc)} pages")
        doc.close()

    def test_rule_1_dense_summary_and_missing_skills(self):
        """Rule 1: Flag dense summary (>65 words/>3 lines) and missing standalone skills block."""
        from rules.rule1_readability import audit_readability
        resume_dense = """# Jane Doe
## SUMMARY
As a Clinical Nurse Specialist at Mercy General, I lead ward triage operations, coordinate emergency care pathways across four intensive care units, manage cross-functional nursing schedules, supervise student nurses during clinical rotations, and ensure regulatory healthcare compliance across all regional clinics while maintaining patient documentation and quality standards. I also coordinate directly with clinical directors to improve patient discharge turnaround and ensure protocol adherence across daily rotations.

## EXPERIENCE
### Nurse Specialist | Mercy General
*2021 - Present*
- Managed triage operations for 40+ emergency patients daily.
"""
        r1 = audit_readability(resume_dense)
        issue_codes = [i["code"] for i in r1["issues"]]
        self.assertIn("DENSE_SUMMARY_PARAGRAPH", issue_codes)
        self.assertIn("NO_STANDALONE_SKILLS_SECTION", issue_codes)

    def test_rule_2_target_role_and_fit_positioning(self):
        """Rule 2: Flag missing target role headline and job description summary."""
        from rules.rule2_keyword_mapping import check_target_role_and_fit
        resume_no_headline = """# John Smith
john@example.com | (555) 123-4567

## SUMMARY
As a High School Teacher at Lincoln High, I teach algebra and calculus to students.
"""
        fit = check_target_role_and_fit(resume_no_headline)
        codes = [i["code"] for i in fit["issues"]]
        self.assertIn("NO_TARGET_ROLE_STATED", codes)
        self.assertIn("JOB_DESCRIPTION_SUMMARY_NOT_FIT_POSITIONING", codes)

    def test_rule_3_date_overlaps_and_attribution(self):
        """Rule 3: Detect unexplained date overlaps and team metric attribution gaps."""
        from rules.rule3_human_gate import check_date_overlaps, enforce_human_gate
        resume_overlap = """### Senior Staff Nurse | Hospital A
*May 2020 - September 2021*
- Led emergency triage team.

### Clinical Research Coordinator | Pharma Lab B
*October 2020 - January 2021*
- Conducted clinical trials.
"""
        overlaps = check_date_overlaps(resume_overlap)
        self.assertGreaterEqual(len(overlaps), 1)

        # Team attribution check
        bullet_gap = enforce_human_gate("Scaled sprint velocity by 50% across 3 teams.")
        gap_types = [f["type"] for f in bullet_gap["flags"]]
        self.assertIn("TEAM_METRIC_ATTRIBUTION_GAP", gap_types)

        # Personal attribution passes
        bullet_attr = enforce_human_gate("Coached 3 teams to accelerate sprint velocity by 50% through backlog grooming.")
        gap_types2 = [f["type"] for f in bullet_attr["flags"]]
        self.assertNotIn("TEAM_METRIC_ATTRIBUTION_GAP", gap_types2)

    def test_rule_4_per_role_quantification(self):
        """Rule 4: Flag duty-based bullets and enforce hard gate (<40%) across roles."""
        from rules.rule4_google_xyz import audit_role_quantification
        resume_duty = """## WORK EXPERIENCE
### Lead Nurse | Clinic North
*2022 - Present*
- Managed triage for 50 patients daily, reducing wait times by 35%.

### Staff Nurse | General Hospital
*2019 - 2022*
- Responsible for daily patient rounds and administering medication.
- Helped with intake documentation and shift scheduling.
"""
        quant_audit = audit_role_quantification(resume_duty)
        codes = [i["code"] for i in quant_audit["issues"]]
        self.assertIn("RULE_4_ROLE_QUANTIFICATION_GATE_VIOLATION", codes)
        self.assertFalse(quant_audit["passed_hard_gate"])
        self.assertEqual(len(quant_audit["hard_gate_violations"]), 1)
        self.assertEqual(quant_audit["hard_gate_violations"][0]["role"], "Staff Nurse | General Hospital")

    def test_rule_4_vague_metric_rejection(self):
        """Rule 4 Fix 2: Reject vague metrics without baselines (require before/after)."""
        from rules.rule4_google_xyz import check_vague_metric
        vague_bullet = "Streamlined client change request intake and impact analysis, reducing change review turnaround time."
        vague_res = check_vague_metric(vague_bullet)
        self.assertTrue(vague_res["is_vague"])
        self.assertIn("turnaround", vague_res["prompt"].lower())

        # Quantified version with before/after passes
        good_bullet = "Streamlined client change request intake, reducing change review turnaround time from 5 days to 2 days."
        good_res = check_vague_metric(good_bullet)
        self.assertFalse(good_res["is_vague"])

    def test_rule_4_collective_metric_reframing(self):
        """Rule 4 Fix 3: Reframe collective metrics as personal contribution."""
        from rules.rule4_google_xyz import check_collective_metric_framing
        team_bullet = "Scaled sprint velocity by 50% from 40 to 60 points."
        check_res = check_collective_metric_framing(team_bullet)
        self.assertTrue(check_res["has_gap"])
        self.assertIn("Enabled team to scale sprint velocity", check_res["suggested_reframe"])

    def test_rule_2_title_identity_mismatch(self):
        """Rule 2: Flag mismatch when target role is Product Manager but work history is Project Manager."""
        from rules.rule2_keyword_mapping import check_target_role_and_fit
        resume_mismatch = """# Sahas Pokhrel
Target Role: Product Manager
Kathmandu, Nepal | sahas@example.com

## PROFESSIONAL SUMMARY
Technical Product Manager with 5+ years of experience leading cross-functional teams.

## WORK EXPERIENCE
### Project Manager | Veel
*2023 - Present*
- Led sprint planning and delivery.

### Associate Project Manager | Dogma Group
*2021 - 2022*
- Managed change requests.
"""
        fit = check_target_role_and_fit(resume_mismatch)
        codes = [i["code"] for i in fit["issues"]]
        self.assertIn("TITLE_IDENTITY_MISMATCH", codes)

    def test_rule_3_contradictory_metric_ambiguity(self):
        """Rule 3: Detect contradictory DAU metrics (laying foundation vs actual DAU)."""
        from rules.rule3_human_gate import check_resume_ambiguities
        resume_text = """### Project Manager | Veel
- Drove development of key features, laying the foundation for a 10K DAU user base on key landing pages.
- Leveraged GA4 to grow daily active users from 0 to 5K+, and tracking consistent engagement surges to 10K DAU.
"""
        ambiguities = check_resume_ambiguities(resume_text)
        self.assertEqual(len(ambiguities), 1)
        self.assertEqual(ambiguities[0]["code"], "CONTRADICTORY_AMBIGUOUS_METRIC")

    def test_rule_5_prove_ai_skills_profession_agnostic(self):
        """Rule 5: Flag product-only AI mentions and AI certs without demonstrable workflow outcomes."""
        from rules.rule5_prove_ai import audit_and_prove_ai_skills
        resume_product_ai = """# Alex Lee
Product Designer
## SUMMARY
Working at an AI-powered healthcare startup designing patient interfaces.

## CERTIFICATIONS
- Introduction to Generative AI

## EXPERIENCE
### Senior Designer | AI Health
*2023 - Present*
- Designed user flows for patient onboarding.
"""
        r5 = audit_and_prove_ai_skills(resume_product_ai)
        codes = [i["code"] for i in r5["issues"]]
        self.assertIn("AI_PRODUCT_ONLY_NOT_WORKFLOW_SKILL", codes)
        self.assertIn("AI_CERTIFICATION_WITHOUT_OUTCOME", codes)
        self.assertIn("NO_AI_TOOLS_IN_WORKFLOW", codes)
        self.assertIn("NO_AI_AUGMENTED_ACHIEVEMENT_BULLET", codes)

    def test_rule_4_hard_gate_blocks_unquantified_resume(self):
        """Rule 4 Hard Gate: Ensure transforming raw Profile.pdf without metrics is blocked."""
        profile_path = "/Users/moderntechnepal/Downloads/Profile.pdf"
        if not os.path.exists(profile_path):
            self.skipTest(f"Test file not found: {profile_path}")

        from pdf_parser import extract_pdf_data
        parsed = extract_pdf_data(profile_path)

        # Transform resume without user_metrics
        res = self.agent.transform_resume(parsed["text"])
        qa = res["qa_report"]

        self.assertEqual(qa["overall_status"], "QA_FAILED")
        self.assertTrue(qa["hard_gate_blocked"])
        self.assertGreaterEqual(len(qa["critical_failures"]), 1)
        # Verify hard gate violations include unquantified roles
        violations = qa["pillars"]["rule_compliance"]["role_quantification"]["hard_gate_violations"]
        violation_roles = [v["role"] for v in violations]
        self.assertTrue(any("SCSS Consulting" in r for r in violation_roles))

    def test_formatting_gate_role_metadata(self):
        """Fix 2: Verify role metadata validator enforces title + company + date + location."""
        # Incomplete header: missing date and location
        bad_md = """# Candidate Name
## WORK EXPERIENCE
### Associate Project Manager | TechSaintIT
- Led cross-functional team deliveries.
"""
        bad_qa = validate_role_headers_metadata(bad_md)
        self.assertFalse(bad_qa["passed"])
        self.assertTrue(any("INCOMPLETE_ROLE_HEADER" in iss for iss in bad_qa["issues"]))

        # Complete header: title, company, date, location
        good_md = """# Candidate Name
## WORK EXPERIENCE
### Associate Project Manager | TechSaintIT
*May 2020 - September 2021 | Kathmandu, Bagmati, Nepal*
- Led cross-functional team deliveries.
"""
        good_qa = validate_role_headers_metadata(good_md)
        self.assertTrue(good_qa["passed"])
        self.assertEqual(len(good_qa["issues"]), 0)

    def test_formatting_gate_clean_latex_artifacts(self):
        """Fix 3: Verify clean_latex_artifacts strips math-mode delimiters, escaped %, $, and circ."""
        dirty = r"Scaled from \(5+\) to \(10K\) users with \(50\%\) growth, saving \(\$120K+\) and \(25\%\) latency. Item \circ bullet."
        cleaned = clean_latex_artifacts(dirty)
        self.assertEqual(cleaned, "Scaled from 5+ to 10K users with 50% growth, saving $120K+ and 25% latency. Item • bullet.")
        self.assertNotIn(r"\(", cleaned)
        self.assertNotIn(r"\)", cleaned)
        self.assertNotIn(r"\%", cleaned)
        self.assertNotIn(r"\$", cleaned)
        self.assertNotIn(r"\circ", cleaned)

    def test_universal_currency_detection(self):
        """Verify Rule 4 recognizes metrics across all major world currencies ($ € £ ¥ ₹ AED CAD AUD CHF R$ zł kr)."""
        from rules.rule4_google_xyz import analyze_metrics
        currencies = [
            "Protected $150K in project scope across 12 sprint cycles.",
            "Scaled payment processing handling €2.5M in quarterly transaction volume.",
            "Reduced infrastructure expenditure, saving £80,000 annually.",
            "Governed enterprise delivery portfolio valued at ₹10 Lakhs with 98% on-time milestone release.",
            "Optimized Tokyo database queries, handling ¥12,000,000 in monthly transactions.",
            "Delivered fintech MVP under budget, saving AED 200,000 in vendor licensing.",
            "Cut cloud compute costs by CAD 120K through serverless migration.",
            "Accelerated Australian billing pipeline, processing AUD 95,000 daily.",
            "Secured Swiss banking audit compliance, mitigating CHF 150,000 in regulatory penalty risks.",
            "Streamlined Brazilian logistics routing, reducing operating spend by R$ 50,000.",
            "Automated Warsaw reporting workflows, cutting overhead by 50,000 zł.",
            "Optimized Stockholm cluster capacity, reducing annual server leasing by 100,000 kr."
        ]
        for bullet in currencies:
            result = analyze_metrics(bullet)
            self.assertTrue(result["has_metrics"], f"Failed to recognize currency metric in: '{bullet}'")

    def test_universal_location_detection(self):
        """Verify universal location detection for candidates from any country worldwide."""
        from qa_validator import is_valid_location, validate_role_headers_metadata
        sample_locations = [
            "Paris, France", "São Paulo, Brazil", "Dubai, UAE", "Tokyo, Japan",
            "Lagos, Nigeria", "Dublin, Ireland", "Sydney, Australia", "Toronto, Canada",
            "Berlin, Germany", "Zurich, Switzerland", "Singapore", "Seoul, South Korea",
            "Nairobi, Kenya", "Remote", "Hybrid", "On-site"
        ]
        for loc in sample_locations:
            self.assertTrue(is_valid_location(loc), f"Failed to recognize valid location: '{loc}'")

        # Verify role headers with international locations pass metadata QA
        intl_md = """# Global Candidate
## WORK EXPERIENCE
### Product Lead | Spotify
*Jan 2022 – Present | Stockholm, Sweden*
- Led feature development for 10M active listeners.

### Senior Engineering Manager | Grab
*Mar 2019 – Dec 2021 | Singapore*
- Directed multi-service architecture across Southeast Asia.

### Staff Software Engineer | Nubank
*Jan 2017 – Feb 2019 | São Paulo, Brazil*
- Automated credit evaluation engine processing R$ 20M monthly.
"""
        qa = validate_role_headers_metadata(intl_md)
        self.assertTrue(qa["passed"])
        self.assertEqual(len(qa["issues"]), 0)

    def test_international_candidate_end_to_end(self):
        """Verify end-to-end processing of an international candidate (French/EU, Euro metrics, phone, languages)."""
        intl_raw = """# Marie Curie
Paris, France | marie.curie@example.eu | +33 1 42 68 55 00 | linkedin.com/in/marie-curie

## PROFESSIONAL SUMMARY
Product Manager with 6+ years of experience delivering cloud and fintech platforms across European markets. Experienced in agile delivery and AI-assisted sprint planning.

## WORK EXPERIENCE
### Senior Product Manager | BNP Paribas
*January 2021 – Present | Paris, France*
- Leveraged Generative AI tools (ChatGPT, Claude) to automate sprint requirement synthesis, saving 4+ hours weekly.
- Directed payments integration across 14 European markets, scaling quarterly transaction volume to €45M.
- Reduced payment dispute turnaround time from 5 business days to 1.5 business days across 250,000 accounts.
- Led cross-functional squad of 12 engineers and 3 designers to launch biometric verification MVP.

### Associate Product Manager | Blablacar
*June 2018 – December 2020 | Paris, France*
- Managed ride-scheduling algorithm enhancements, lifting trip completion rates by 28%.
- Standardized sprint backlog refinement in Jira, increasing team delivery velocity by 32%.
- Accelerated customer incident triage from 24 hours to 4 hours across 80,000 monthly active riders.

## CORE COMPETENCIES & TECHNICAL SKILLS
- **Project & Agile Governance:** Scrum, Agile, Jira, Sprint Planning, Stakeholder Management
- **Technical & Architecture:** REST APIs, Microservices, SQL, PostgreSQL, AWS
- **Languages:** French (Native), English (Fluent), German (B2)

## EDUCATION & CERTIFICATIONS
### Master of Science in Management | HEC Paris
*2016 – 2018*
- **Professional Scrum Product Owner™ (PSPO I)** | Scrum.org

## ADDITIONAL INFORMATION
- **Work Authorization:** EU Citizen / Eligible to work across EU and UK without visa sponsorship
"""
        standard_md, meta = format_to_standard_template(intl_raw)
        self.assertIn("PARIS, FRANCE", standard_md.upper())
        self.assertIn("+33 1 42 68 55 00", standard_md)
        self.assertIn("€45M", standard_md)
        self.assertIn("**Languages:** French (Native)", standard_md)
        self.assertIn("EU Citizen", standard_md)

        # Generate PDF and run full QA
        pdf_bytes = generate_pdf_from_markdown(standard_md)
        qa = run_full_qa_pipeline(intl_raw, standard_md, pdf_bytes=pdf_bytes)
        self.assertEqual(qa["overall_status"], "QA_PASSED")
        self.assertGreaterEqual(qa["qa_score"], 85)
        self.assertEqual(len(qa["critical_failures"]), 0)

    def test_custom_achievements_and_ai_tools_crud_injection(self):
        """Verify custom achievements from Step 3 CRUD and Workshop are injected into Work Experience & Skills."""
        from rules.rule4_google_xyz import transform_to_xyz

        # Test Google XYZ transformation with metric
        xyz = transform_to_xyz(
            "Responsible for managing sprint planning and backlog triage",
            metric_value="saving 4 hours weekly"
        )
        self.assertTrue(xyz["has_metrics"])
        self.assertIn("Directed", xyz["suggested"])
        self.assertIn("**4 hours** weekly", xyz["suggested"])

        # Test injection into template
        user_metrics = {
            "achievements": [
                xyz["suggested"],
                "Led team of 8 engineers delivering payment gateway with 99.9% uptime."
            ],
            "ai_tools": ["Claude Code", "Cursor", "ChatGPT"]
        }

        standard_md, meta = format_to_standard_template(SAMPLE_RESUME, user_metrics=user_metrics)

        # 1. Custom achievements must be in WORK EXPERIENCE under first role
        self.assertIn("## WORK EXPERIENCE", standard_md)
        self.assertIn("Directed sprint planning and backlog triage", standard_md)
        self.assertIn("**4 hours** weekly", standard_md)
        self.assertIn("**8 engineers**", standard_md)
        self.assertIn("**99.9%** uptime", standard_md)

        # 2. AI tools must be in first role's AI bullet
        self.assertIn("Claude Code", standard_md)
        self.assertIn("Cursor", standard_md)

        # 3. AI tools must be in Skills section
        self.assertIn("## CORE COMPETENCIES & TECHNICAL SKILLS", standard_md)
        self.assertIn("Claude Code", standard_md)

    def test_multi_role_achievement_mapping(self):
        """Verify role detection and that achievements are injected under their specific matching past job."""
        from template_formatter import extract_roles_from_resume, format_to_standard_template

        # 1. Test role detection from resume text
        detected = extract_roles_from_resume(SAMPLE_RESUME)
        self.assertGreaterEqual(len(detected), 2)
        companies = [r["company"] for r in detected]
        self.assertIn("Datasync Networks", companies)
        self.assertIn("ScaleCloud Technologies", companies)

        # 2. Test targeted achievement assignment to specific past jobs
        user_metrics = {
            "achievements": [
                {
                    "text": "Deployed multi-region disaster recovery failover across AWS in under 4 minutes.",
                    "role": "Datasync Networks",
                    "roleLabel": "Datasync Networks (Staff Infrastructure Engineer)"
                },
                {
                    "text": "Re-architected real-time streaming pipeline cutting Kafka cluster memory footprint by 35% on 50 brokers.",
                    "role": "ScaleCloud Technologies",
                    "roleLabel": "ScaleCloud Technologies (Software Engineer)"
                }
            ]
        }

        standard_md, _ = format_to_standard_template(SAMPLE_RESUME, user_metrics=user_metrics)

        # Split markdown by role headers to verify correct role placement
        parts = standard_md.split("### ")
        self.assertGreaterEqual(len(parts), 3)

        # Part 1 should contain Datasync Networks and its achievement
        datasync_part = [p for p in parts if "Datasync Networks" in p][0]
        self.assertIn("disaster recovery failover", datasync_part)
        self.assertIn("**4 minutes**", datasync_part)
        self.assertNotIn("Kafka cluster memory footprint", datasync_part)

        # Part 2 should contain ScaleCloud Technologies and its achievement
        scalecloud_part = [p for p in parts if "ScaleCloud Technologies" in p][0]
        self.assertIn("Kafka cluster memory footprint", scalecloud_part)
        self.assertIn("**35%**", scalecloud_part)
        self.assertIn("50 brokers", scalecloud_part)
        self.assertNotIn("disaster recovery failover", scalecloud_part)

if __name__ == "__main__":
    unittest.main()




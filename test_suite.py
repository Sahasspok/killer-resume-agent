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
    standard_template_to_html
)
from pdf_generator import generate_pdf_from_markdown
from qa_validator import (
    run_full_qa_pipeline,
    validate_fact_preservation,
    validate_formatting_and_syntax,
    validate_pdf_render
)
from format_preserver import transform_preserving_format

SAMPLE_RESUME = """# Alex Mercer
San Francisco, CA | alex.mercer@example.com | (415) 555-0199 | linkedin.com/in/alex-mercer | github.com/alex-dev

## PROFESSIONAL SUMMARY
Senior Software Engineer with 6+ years of experience designing distributed systems, optimizing backend pipelines, and building scalable cloud infrastructure. Experienced in deploying LLM workflows for automated code analysis.

## WORK EXPERIENCE

### Staff Infrastructure Engineer | Datasync Networks
*Jan 2022 – Present*
- Managed cross-team deployment of Kubernetes microservices across 3 cloud regions.
- Responsible for leading database migration from Postgres 12 to 15 without downtime.
- Accelerated deployment pipeline throughput by 45% using GitHub Actions and Docker caching.
- Helped with on-call incident triage and post-mortems for tier-1 production outages.
- Reduced cold-start container latency from 8 seconds to 1.2 seconds across 40 nodes.

### Software Engineer | ScaleCloud Technologies
*May 2019 – Dec 2021*
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

        # Transform resume
        res = self.agent.transform_resume(parsed["text"])
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
        self.assertIn("**10K**", opt_md)
        self.assertIn("**50%**", opt_md)
        self.assertIn("**24 hours**", opt_md)

        # 5. Full Production QA Verification
        qa = res["qa_report"]
        self.assertEqual(qa["overall_status"], "QA_PASSED", f"QA Failed with critical failures: {qa['critical_failures']}")
        self.assertEqual(qa["qa_score"], 100)
        self.assertEqual(len(qa["critical_failures"]), 0)

        # 6. Rule 1 Readability QA Integration Verification (Zero heading/readability issues)
        post_r1 = res["post_audit_details"]["rule_1_readability"]
        self.assertEqual(post_r1["score"], 100)
        self.assertEqual(post_r1["issues"], [], f"Rule 1 issues found on generated resume: {post_r1['issues']}")
        self.assertIn("Summary", post_r1["headings_found"])
        self.assertIn("Experience", post_r1["headings_found"])
        self.assertIn("Skills", post_r1["headings_found"])
        self.assertIn("Education", post_r1["headings_found"])

        # 7. Verify vector PDF geometry (Strictly 2 pages, never 3 pages)
        pdf_bytes = base64.b64decode(res["pdf_base64"])
        self.assertLess(len(pdf_bytes), 2.5 * 1024 * 1024)
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        self.assertEqual(len(doc), 2, f"Consolidated 5-page LinkedIn export must strictly render in 2 pages, got {len(doc)} pages")
        doc.close()

if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
"""
Killer Resume Agent - CLI
Usage:
  python3 cli.py audit --resume examples/sample_resume.pdf --jd examples/sample_jd.md
  python3 cli.py qa --resume examples/sample_resume.md --jd examples/sample_jd.md
  python3 cli.py transform --resume examples/sample_resume.pdf --jd examples/sample_jd.md --out killer_resume.md --pdf output.pdf
"""
import argparse
import sys
import os
import base64
from agent import KillerResumeAgent
from pdf_parser import extract_pdf_data
from qa_validator import run_full_qa_pipeline
from pdf_generator import generate_pdf_from_markdown

def main():
    parser = argparse.ArgumentParser(description="Killer Resume Agent - Built on Jeff Su's 5 Research-Backed Rules")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Audit command
    audit_parser = subparsers.add_parser("audit", help="Run 5-rule audit on a resume (PDF or Markdown) against a target job description")
    audit_parser.add_argument("--resume", required=True, help="Path to resume file (.pdf, .md, or .txt)")
    audit_parser.add_argument("--jd", default="", help="Path to Job Description file")

    # QA command
    qa_parser = subparsers.add_parser("qa", help="Run 7-Pillar Production QA Matrix on a resume")
    qa_parser.add_argument("--resume", required=True, help="Path to resume file (.pdf, .md, or .txt)")
    qa_parser.add_argument("--jd", default="", help="Path to Job Description file")
    qa_parser.add_argument("--pdf", default="", help="Optional compiled PDF to inspect")

    # Transform command
    transform_parser = subparsers.add_parser("transform", help="Transform raw resume into killer ATS-ready resume with QA verification")
    transform_parser.add_argument("--resume", required=True, help="Path to resume file (.pdf, .md, or .txt)")
    transform_parser.add_argument("--jd", default="", help="Path to Job Description file")
    transform_parser.add_argument("--out", default="killer_resume.md", help="Output markdown file path")
    transform_parser.add_argument("--pdf", default="killer_resume.pdf", help="Output PDF file path")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if not os.path.exists(args.resume):
        print(f"Error: Resume file '{args.resume}' not found.")
        sys.exit(1)

    pdf_diag = None
    if args.resume.lower().endswith(".pdf"):
        print(f"📄 Inspecting PDF ATS compatibility for: {args.resume}...")
        try:
            pdf_diag = extract_pdf_data(args.resume)
            resume_text = pdf_diag["text"]
            print(f"   [✓] Selectable text extracted: {pdf_diag['char_count']:,} chars across {pdf_diag['page_count']} page(s).")
            print(f"   [✓] File size: {pdf_diag['file_size_mb']} MB (Threshold: 2.5 MB).")
            if pdf_diag["image_trapped_warning"]:
                print(f"   [!] CRITICAL WARNING: Text trapped in images or unselectable!")
        except Exception as e:
            print(f"Error extracting PDF: {e}")
            sys.exit(1)
    else:
        with open(args.resume, "r", encoding="utf-8") as f:
            resume_text = f.read()

    jd_text = ""
    if args.jd and os.path.exists(args.jd):
        with open(args.jd, "r", encoding="utf-8") as f:
            jd_text = f.read()

    agent = KillerResumeAgent()

    if args.command == "audit":
        print("\n" + "="*70)
        print("  KILLER RESUME AGENT - 5-RULE AUDIT REPORT")
        print("  (Based on 4,000+ Hiring Managers & 2M Applications)")
        print("="*70 + "\n")

        res = agent.run_comprehensive_audit(resume_text, jd_text)
        print(f"🎯 COMPOSITE KILLER SCORE: {res['composite_score']}/100")
        print(f"📋 EXECUTIVE SUMMARY: {res['executive_summary']}\n")

        print("--- RULE 1: AI READABILITY (ATS) ---")
        if pdf_diag:
            print(f"PDF Inspection: Size: {pdf_diag['file_size_mb']}MB | Pages: {pdf_diag['page_count']} | Selectable: {pdf_diag['is_selectable']}")
            for flg in pdf_diag["flags"]:
                print(f"  [{'✓' if flg['severity'] == 'PASS' else '!'}] {flg['message']}")
        print(f"Score: {res['rule_1_readability']['score']}/100 | Passed: {res['rule_1_readability']['passed']}")
        for s in res['rule_1_readability']['strengths']:
            print(f"  [✓] {s}")
        for iss in res['rule_1_readability']['issues']:
            print(f"  [!] {iss['code']}: {iss['message']}")

        print("\n--- RULE 2: KEYWORD MAPPING ---")
        r2 = res['rule_2_keyword_mapping']
        print(f"Score: {r2['score']}/100 | Status: {r2.get('status', 'N/A')} | Coverage: {r2.get('coverage_percent', 0)}%")
        print(f"  Advice: {r2.get('advice', 'N/A')}")
        if r2.get('matched_keywords'):
            print(f"  Matched ({len(r2['matched_keywords'])}): {', '.join(r2['matched_keywords'][:8])}")
        if r2.get('missing_keywords'):
            print(f"  Missing to Map ({len(r2['missing_keywords'])}): {', '.join(r2['missing_keywords'][:6])}")

        print("\n--- RULE 3: HUMAN REVIEW GATE (POLISH VS GHOSTWRITE) ---")
        r3 = res['rule_3_human_gate']
        print(f"Score: {r3['score']}/100 | Human Defense Gate: {r3['human_defense_gate']}")
        print(f"  Insight: {r3['insight']}")

        print("\n--- RULE 4: QUANTIFIED IMPACT (GOOGLE XYZ FORMULA) ---")
        r4 = res['rule_4_quantified_impact']
        print(f"Score: {r4['score']}/100 | Quantified Ratio: {r4['quantified_ratio_percent']}% ({r4['quantified_count']}/{r4['total_bullets_audited']} bullets)")
        print(f"  Insight: {r4['insight']}")

        print("\n--- RULE 5: PROVE YOUR AI SKILLS ---")
        r5 = res['rule_5_prove_ai_skills']
        print(f"Score: {r5['score']}/100 | Proven AI Skills: {r5['has_proven_ai_skills']}")
        print(f"  Advice: {r5['advice']}")

        print("\n" + "="*70 + "\n")

    elif args.command == "qa":
        print("\n" + "="*70)
        print("  7-PILLAR PRODUCTION QA MATRIX AUDIT")
        print("="*70 + "\n")
        pdf_bytes = None
        if args.pdf and os.path.exists(args.pdf):
            with open(args.pdf, "rb") as f:
                pdf_bytes = f.read()

        qa_res = run_full_qa_pipeline(resume_text, resume_text, jd_text=jd_text, pdf_bytes=pdf_bytes)
        print(f"STATUS: {qa_res['overall_status']} (QA Score: {qa_res['qa_score']}/100)")
        print(f"SUMMARY: {qa_res['summary']}\n")
        for pillar_name, pillar in qa_res["pillars"].items():
            if pillar:
                print(f"[{'PASS' if pillar['passed'] else 'FAIL'}] {pillar['pillar'].upper()}")
                for chk in pillar["checks"]:
                    print(f"   [{chk['status']}] {chk['name']}: {chk['details']}")
        print("\n" + "="*70 + "\n")

    elif args.command == "transform":
        print("🚀 Transforming resume into Executive ATS Standard Template with 7-Pillar QA...")
        result = agent.transform_resume(resume_text, jd_text)
        
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(result["optimized_markdown"])

        if args.pdf:
            pdf_bytes = base64.b64decode(result["pdf_base64"])
            with open(args.pdf, "wb") as f:
                f.write(pdf_bytes)

        qa = result["qa_report"]
        print(f"\n✓ Optimization & Production QA Complete!")
        print(f"  Initial Score:   {result['initial_score']}/100")
        print(f"  Optimized Score: {result['optimized_score']}/100")
        print(f"  QA Status:       {qa['overall_status']} ({qa['qa_score']}/100)")
        print(f"  QA Summary:      {qa['summary']}")
        print(f"\n📁 Outputs Saved:")
        print(f"  - Markdown: {args.out}")
        if args.pdf:
            print(f"  - Vector PDF: {args.pdf} ({result['pdf_size_kb']} KB)")
        print()

if __name__ == "__main__":
    main()

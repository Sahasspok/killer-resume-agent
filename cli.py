#!/usr/bin/env python3
"""
Killer Resume Agent - CLI
Usage:
  python3 cli.py audit --resume examples/sample_resume.md --jd examples/sample_jd.md
  python3 cli.py transform --resume examples/sample_resume.md --jd examples/sample_jd.md --out killer_resume.md
"""
import argparse
import sys
import os
from agent import KillerResumeAgent

def main():
    parser = argparse.ArgumentParser(description="Killer Resume Agent - Built on Jeff Su's 5 Research-Backed Rules")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Audit command
    audit_parser = subparsers.add_parser("audit", help="Run 5-rule audit on a resume against a target job description")
    audit_parser.add_argument("--resume", required=True, help="Path to resume file (Markdown or TXT)")
    audit_parser.add_argument("--jd", default="", help="Path to Job Description file")

    # Transform command
    transform_parser = subparsers.add_parser("transform", help="Transform raw resume into killer ATS-ready resume")
    transform_parser.add_argument("--resume", required=True, help="Path to resume file")
    transform_parser.add_argument("--jd", default="", help="Path to Job Description file")
    transform_parser.add_argument("--out", default="killer_resume.md", help="Output file path")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if not os.path.exists(args.resume):
        print(f"Error: Resume file '{args.resume}' not found.")
        sys.exit(1)

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

    elif args.command == "transform":
        print("Transforming resume with 5-Rule Optimization Engine...")
        result = agent.transform_resume(resume_text, jd_text)
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(result["optimized_markdown"])
        print(f"\nOptimization Complete!")
        print(f"Initial Score:   {result['initial_score']}/100")
        print(f"Optimized Score: {result['optimized_score']}/100")
        print(f"Saved ATS-certified killer resume to: {args.out}\n")

if __name__ == "__main__":
    main()

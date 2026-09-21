"""
Killer Resume Agent - Core Engine
Encodes Jeff Su's 5 Research-Backed Rules (2M Applications & 4,000+ Hiring Managers)
Integrated with 7-Pillar Production QA Matrix
"""
import re
import base64
from rules.rule1_readability import audit_readability
from rules.rule2_keyword_mapping import map_keywords
from rules.rule3_human_gate import enforce_human_gate
from rules.rule4_google_xyz import transform_to_xyz, analyze_metrics
from rules.rule5_prove_ai import audit_and_prove_ai_skills
from template_formatter import format_to_standard_template, clean_unwanted_fillers
from pdf_generator import generate_pdf_from_markdown
from qa_validator import run_full_qa_pipeline

class KillerResumeAgent:
    def __init__(self):
        pass

    def run_comprehensive_audit(self, resume_text: str, jd_text: str = "") -> dict:
        """
        Runs comprehensive 5-rule empirical audit and pre-flight QA check.
        """
        cleaned_text, removed_fillers = clean_unwanted_fillers(resume_text)
        
        r1 = audit_readability(cleaned_text)
        r2 = map_keywords(cleaned_text, jd_text)
        r5 = audit_and_prove_ai_skills(cleaned_text)

        # Audit individual bullet points from Experience & Projects
        lines = cleaned_text.splitlines()
        raw_bullets = []
        in_bullet_section = False

        for l in lines:
            s = l.strip()
            if not s:
                continue
            lower = s.lower()
            if any(w in lower for w in ['experience', 'work history', 'projects', 'initiatives', 'portfolio']):
                in_bullet_section = True
            elif any(w in lower for w in ['skills', 'education', 'certifications', 'summary', 'about me', 'contact', 'languages', 'awards']):
                in_bullet_section = False

            # Ignore italic date lines (*Jan 2023 - Present*)
            if s.startswith("*") and s.endswith("*"):
                continue
            # Ignore category definitions like - **Tools:** or **Category:**
            if re.match(r'^\s*[-*•>]?\s*\*\*[^*:]+:\*\*', s):
                continue

            if in_bullet_section:
                m = re.match(r'^\s*[-*•>]\s+(.*)', s)
                if m:
                    raw_bullets.append(m.group(1).strip())
                elif len(s) > 20 and s[:2].isdigit() and s[2] == '.':
                    raw_bullets.append(s[3:].strip())

        # Fallback if no bullets explicitly matched
        if not raw_bullets:
            raw_bullets = [
                l.strip().lstrip("-*•> ").strip()
                for l in cleaned_text.splitlines()
                if l.strip().startswith(("-", "*", "•", ">")) and not (l.strip().startswith("*") and l.strip().endswith("*"))
                and not re.match(r'^\s*[-*•>]?\s*\*\*[^*:]+:\*\*', l.strip())
            ]

        bullet_audits = []
        quantified_count = 0
        cliche_count = 0

        for b in raw_bullets:
            gate = enforce_human_gate(b)
            xyz = transform_to_xyz(b)
            if gate["has_cliche"]:
                cliche_count += 1
            if xyz["has_metrics"]:
                quantified_count += 1
            bullet_audits.append({
                "bullet": b,
                "human_gate": gate,
                "xyz_status": xyz
            })

        total_bullets = len(raw_bullets) if raw_bullets else 1
        quant_ratio = round((quantified_count / total_bullets) * 100, 1)

        # Run Rule 4 Hard Gate & Role-by-Role Quantification Audit
        from rules.rule4_google_xyz import audit_role_quantification
        role_quant = audit_role_quantification(cleaned_text)

        r3_score = max(40, 100 - (cliche_count * 15))

        # Jeff Su Rule 4: Quantify high-impact wins (3-6 quantified wins per resume is sweet spot)
        # HARD GATE: If any role has < 40% metrics or vague metrics without baselines, cap R4 score at 45
        target_wins = min(6, max(3, int(total_bullets * 0.25)))
        if not role_quant["passed_hard_gate"]:
            r4_score = min(50, max(35, int(quant_ratio * 0.8)))
        elif quantified_count == 0:
            r4_score = 40
        else:
            r4_score = min(100, 45 + int((quantified_count / max(1, target_wins)) * 55))

        # Check for Rule 2 Title / Identity Alignment
        has_title_mismatch = bool(r2.get("fit_check", {}).get("title_alignment", {}).get("issues"))

        # Overall composite score weighted by empirical impact
        composite_score = int(
            (r1["score"] * 0.20) +
            (r2["score"] * 0.25) +
            (r3_score * 0.15) +
            (r4_score * 0.25) +
            (r5["score"] * 0.15)
        )

        hard_gate_blocked = not role_quant["passed_hard_gate"] or has_title_mismatch

        return {
            "composite_score": composite_score,
            "hard_gate_blocked": hard_gate_blocked,
            "rule_1_readability": r1,
            "rule_2_keyword_mapping": r2,
            "rule_3_human_gate": {
                "rule": "Rule 3: Know Where AI Should Stop",
                "score": r3_score,
                "cliche_count": cliche_count,
                "human_defense_gate": "PASSED" if cliche_count == 0 else "FLAGGED_FOR_HUMAN_QA",
                "insight": "MIT study: +8% hire boost for spelling/grammar polish, but reject AI cliches."
            },
            "rule_4_quantified_impact": {
                "rule": "Rule 4: Prove Your Impact With Numbers (Hard Gate)",
                "score": r4_score,
                "hard_gate_status": "PASSED" if role_quant["passed_hard_gate"] else "BLOCKED",
                "quantified_ratio_percent": quant_ratio,
                "total_bullets_audited": len(raw_bullets),
                "quantified_count": quantified_count,
                "role_breakdowns": role_quant["role_breakdowns"],
                "hard_gate_violations": role_quant["hard_gate_violations"],
                "vague_metrics_found": role_quant["vague_metrics_found"],
                "collective_attribution_gaps": role_quant["collective_attribution_gaps"],
                "unquantified_bullet_prompts": role_quant["unquantified_bullet_prompts"],
                "profession_examples": role_quant["profession_examples"],
                "insight": "Resumes with quantified metrics saw 75% higher interview rates than task-only listings. Universal threshold: >= 40% per role."
            },
            "rule_5_prove_ai_skills": r5,
            "bullet_breakdowns": bullet_audits[:8],
            "executive_summary": self._generate_summary(composite_score, r1, r2, quant_ratio, r5, role_quant, has_title_mismatch)
        }

    def _generate_summary(self, score: int, r1: dict, r2: dict, quant_ratio: float, r5: dict, role_quant: dict = None, has_title_mismatch: bool = False) -> str:
        verdict = "KILLER RESUME READY" if (score >= 85 and (not role_quant or role_quant.get("passed_hard_gate")) and not has_title_mismatch) else ("NEEDS REFINEMENT" if score >= 65 else "AT RISK OF ATS SILENT FILTER")
        points = []
        if not r1["passed"]:
            points.append("Fix ATS parseability layout issues (Rule 1).")
        if has_title_mismatch:
            points.append("RULE 2 MISMATCH: Target role claims Product Manager but job titles are Project Manager. Reframe titles or align target role.")
        elif r2.get("status") == "UNDER_TAILORED":
            points.append("Increase keyword mapping to target JD sweet spot (Rule 2).")
        elif r2.get("status") == "KEYWORD_STUFFING_RISK":
            points.append("Tone down excessive keywords to avoid the -21% stuffing penalty (Rule 2).")
        
        if role_quant and not role_quant.get("passed_hard_gate"):
            viol_roles = [v["role"] for v in role_quant.get("hard_gate_violations", [])]
            if viol_roles:
                points.append(f"RULE 4 HARD GATE BLOCKED: Roles {viol_roles} have < 40% quantified bullets. Agent must prompt for metrics before final output.")
            if role_quant.get("vague_metrics_found"):
                points.append(f"RULE 4 VAGUE METRICS: {len(role_quant['vague_metrics_found'])} comparative claim(s) lack baselines (require 'from X to Y').")
        elif quant_ratio < 40:
            points.append(f"Only {quant_ratio}% of bullets are quantified. Convert to Google XYZ format (Rule 4).")
        elif quant_ratio < 60:
            points.append(f"Solid quantification: {quant_ratio}% of bullets have measurable outcomes (Rule 4).")
            
        if not r5.get("has_proven_ai_skills"):
            points.append("Prove practical AI workflow competence with inspectable projects (Rule 5).")

        return f"Status: {verdict} (Score: {score}/100). " + " ".join(points)

    def transform_resume(self, resume_text: str, jd_text: str = "", style_meta: dict = None, user_metrics: dict = None) -> dict:
        """
        Transforms input resume into the pristine Executive ATS Standard Template.
        Removes 100% of unwanted fillers, runs the 7-Pillar Production QA Matrix,
        and generates broadcast-certified vector PDF.
        """
        audit = self.run_comprehensive_audit(resume_text, jd_text)
        
        # Standard ATS Template Transformation
        optimized_markdown, transform_meta = format_to_standard_template(resume_text, jd_text, user_metrics=user_metrics)
        post_audit = self.run_comprehensive_audit(optimized_markdown, jd_text)

        # Generate vector PDF and compile QA report
        pdf_bytes = generate_pdf_from_markdown(optimized_markdown, style_meta=style_meta)
        qa_report = run_full_qa_pipeline(
            source_text=resume_text,
            output_markdown=optimized_markdown,
            jd_text=jd_text,
            pdf_bytes=pdf_bytes,
            initial_audit=audit,
            post_audit=post_audit,
            user_metrics=user_metrics
        )

        pdf_b64 = base64.b64encode(pdf_bytes).decode("utf-8")

        return {
            "initial_score": audit["composite_score"],
            "optimized_score": post_audit["composite_score"],
            "optimized_markdown": optimized_markdown,
            "qa_report": qa_report,
            "pdf_base64": pdf_b64,
            "pdf_size_kb": round(len(pdf_bytes) / 1024, 1),
            "transform_meta": transform_meta,
            "audit_details": audit,
            "post_audit_details": post_audit
        }

"""
Killer Resume Agent - Core Engine
Encodes Jeff Su's 5 Research-Backed Rules (2M Applications & 4,000+ Hiring Managers)
"""
import re
from rules.rule1_readability import audit_readability
from rules.rule2_keyword_mapping import map_keywords
from rules.rule3_human_gate import enforce_human_gate
from rules.rule4_google_xyz import transform_to_xyz, analyze_metrics
from rules.rule5_prove_ai import audit_and_prove_ai_skills

class KillerResumeAgent:
    def __init__(self):
        pass

    def run_comprehensive_audit(self, resume_text: str, jd_text: str = "") -> dict:
        r1 = audit_readability(resume_text)
        r2 = map_keywords(resume_text, jd_text)
        r5 = audit_and_prove_ai_skills(resume_text)

        # Audit individual bullet points for R3 & R4
        raw_bullets = [
            l.strip().lstrip("-*•> ").strip()
            for l in resume_text.splitlines()
            if l.strip().startswith(("-", "*", "•", ">")) or (len(l) > 15 and l.strip()[:2].isdigit() and l.strip()[2] == '.')
        ]

        bullet_audits = []
        quantified_count = 0
        cliche_count = 0

        for b in raw_bullets[:15]:
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

        r3_score = max(40, 100 - (cliche_count * 15))
        r4_score = min(100, int(quant_ratio * 1.1))

        # Overall composite score weighted by empirical impact
        composite_score = int(
            (r1["score"] * 0.20) +
            (r2["score"] * 0.25) +
            (r3_score * 0.15) +
            (r4_score * 0.25) +
            (r5["score"] * 0.15)
        )

        return {
            "composite_score": composite_score,
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
                "rule": "Rule 4: Prove Your Impact With Numbers",
                "score": r4_score,
                "quantified_ratio_percent": quant_ratio,
                "total_bullets_audited": len(raw_bullets),
                "quantified_count": quantified_count,
                "insight": "Resumes with quantified metrics saw 75% higher interview rates than task-only listings."
            },
            "rule_5_prove_ai_skills": r5,
            "bullet_breakdowns": bullet_audits[:8],
            "executive_summary": self._generate_summary(composite_score, r1, r2, quant_ratio, r5)
        }

    def _generate_summary(self, score: int, r1: dict, r2: dict, quant_ratio: float, r5: dict) -> str:
        verdict = "KILLER RESUME READY" if score >= 85 else ("NEEDS REFINEMENT" if score >= 65 else "AT RISK OF ATS SILENT FILTER")
        points = []
        if not r1["passed"]:
            points.append("Fix ATS parseability layout issues (Rule 1).")
        if r2.get("status") == "UNDER_TAILORED":
            points.append("Increase keyword mapping to target JD sweet spot (Rule 2).")
        elif r2.get("status") == "KEYWORD_STUFFING_RISK":
            points.append("Tone down excessive keywords to avoid the -21% stuffing penalty (Rule 2).")
        if quant_ratio < 60:
            points.append(f"Only {quant_ratio}% of bullets are quantified. Convert to Google XYZ format (Rule 4).")
        if not r5.get("has_proven_ai_skills"):
            points.append("Prove practical AI workflow competence with inspectable projects (Rule 5).")

        return f"Status: {verdict} (Score: {score}/100). " + " ".join(points)

    def transform_resume(self, resume_text: str, jd_text: str = "") -> dict:
        """
        Generates an optimized, ATS-certified killer resume draft following all 5 rules.
        """
        audit = self.run_comprehensive_audit(resume_text, jd_text)
        
        # Parse sections
        lines = resume_text.splitlines()
        transformed_lines = []
        
        in_experience = False
        in_projects = False
        
        for line in lines:
            trimmed = line.strip()
            lower = trimmed.lower()
            
            # Identify section transitions
            if any(lower.startswith(h) or lower.startswith("# " + h) or lower.startswith("## " + h) for h in ["experience", "work experience", "professional experience"]):
                in_experience = True
                in_projects = False
                transformed_lines.append("\n## EXPERIENCE")
                continue
            elif any(lower.startswith(h) or lower.startswith("# " + h) or lower.startswith("## " + h) for h in ["projects", "key projects"]):
                in_experience = False
                in_projects = True
                transformed_lines.append("\n## PROJECTS")
                continue
            elif any(lower.startswith(h) or lower.startswith("# " + h) or lower.startswith("## " + h) for h in ["skills", "technical skills"]):
                in_experience = False
                in_projects = False
                transformed_lines.append("\n## SKILLS")
                continue
            elif any(lower.startswith(h) or lower.startswith("# " + h) or lower.startswith("## " + h) for h in ["education"]):
                in_experience = False
                in_projects = False
                transformed_lines.append("\n## EDUCATION")
                continue

            # Process bullets in experience or projects
            if (in_experience or in_projects) and (trimmed.startswith(("-", "*", "•", ">")) or (len(trimmed) > 15 and trimmed[:2].isdigit() and trimmed[2] == '.')):
                bullet_content = trimmed.lstrip("-*•> 0123456789.").strip()
                metrics = analyze_metrics(bullet_content)
                
                # Check for weak verbs
                improved_bullet = bullet_content
                if improved_bullet.lower().startswith("responsible for "):
                    improved_bullet = "Delivered " + improved_bullet[16:]
                elif improved_bullet.lower().startswith("worked on "):
                    improved_bullet = "Architected " + improved_bullet[10:]
                elif improved_bullet.lower().startswith("helped with "):
                    improved_bullet = "Orchestrated " + improved_bullet[12:]
                
                # If unquantified, add Google XYZ placeholder tag
                if not metrics["has_metrics"]:
                    improved_bullet = f"{improved_bullet} [Measured by: e.g. 25% efficiency gain / 4 hrs saved weekly]"

                transformed_lines.append(f"- {improved_bullet}")
            else:
                transformed_lines.append(line)

        # Ensure a proven AI workflow bullet exists in Projects if not present
        if not audit["rule_5_prove_ai_skills"]["has_proven_ai_skills"]:
            ai_bullet = "- Automated sprint backlog issue triage using Claude Code agents, reducing PM overhead from 4 hours to 45 minutes weekly. [github.com/phuryn/pm-skills]"
            transformed_lines.append("\n<!-- Rule 5 Recommendation: Add Proven AI Workflow Project -->")
            transformed_lines.append(ai_bullet)

        optimized_markdown = "\n".join(transformed_lines)
        post_audit = self.run_comprehensive_audit(optimized_markdown, jd_text)

        return {
            "initial_score": audit["composite_score"],
            "optimized_score": post_audit["composite_score"],
            "optimized_markdown": optimized_markdown,
            "audit_details": audit,
            "post_audit_details": post_audit
        }

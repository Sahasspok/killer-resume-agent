"""
Killer Resume Agent - Rule Modules
Based on Jeff Su's 2026 Research on 4,000+ Hiring Managers & 2M Applications
"""
from .rule1_readability import audit_readability
from .rule2_keyword_mapping import map_keywords
from .rule3_human_gate import enforce_human_gate
from .rule4_google_xyz import transform_to_xyz
from .rule5_prove_ai import audit_and_prove_ai_skills

__all__ = [
    "audit_readability",
    "map_keywords",
    "enforce_human_gate",
    "transform_to_xyz",
    "audit_and_prove_ai_skills",
]

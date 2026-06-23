"""Protected regulatory terms — must never be altered by any pipeline stage."""
from __future__ import annotations

PROTECTED_TERMS: list[str] = [
    # Regulatory obligation verbs
    "demonstrate", "demonstrates", "demonstrated", "demonstrating",
    "ensure", "ensures", "ensured", "ensuring",
    "shall", "must", "may", "should",
    "verify", "validates", "verified",
    "validate", "validated",
    "document", "documents", "documented", "documenting",
    "constitute", "constitutes", "constituted",
    "implement", "implements", "implemented",
    "comply", "complies", "complied",
    "justify", "justifies", "justified",
    # ISO 14971 defined terms
    "hazard", "hazardous situation", "harm", "risk", "residual risk",
    "risk control", "risk management", "risk analysis", "risk assessment",
    "risk evaluation", "risk estimation", "benefit-risk", "risk-benefit",
    "severity", "probability", "foreseeable misuse", "intended use",
    "intended purpose", "state of the art", "safety",
    # ISO 13485 / IEC 62304 terms
    "verification", "validation", "traceability", "conformity",
    "in accordance with", "pursuant to", "in compliance with",
    "significant", "substantial", "critical",
    # Document names
    "risk management file", "risk management plan", "risk management report",
    "technical documentation", "post-market surveillance",
    # Inflected forms
    "constituting", "implementing", "complying", "justifying",
    "verifies", "verifying", "validating",
    "maintains", "maintaining", "maintained",
    "establishes", "establishing", "established",
    # Modal verb compounds
    "shall not", "must not", "may not", "should not",
    # Additional regulatory noun forms
    "verifications", "validations", "implementations",
    "non-conformity", "non-conformities",
]

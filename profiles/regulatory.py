"""Regulatory profile for TextHumanize.

Configures the pipeline for use on regulated professional documents such as
EU MDR technical documentation, ISO 13485 QMS records, IEC 62304 software
documentation, risk management files, and clinical evaluation reports.

Safe stages kept:
  - watermark: removes invisible Unicode watermarks, safe for all documents
  - typography: normalises quotes, dashes, ellipses — cosmetic only
  - grammar: fixes obvious grammatical errors without changing meaning
  - structure / repetitions: run at very low intensity under 'formal' profile
  - readability: light sentence-length reshaping only at low intensity

Disabled / suppressed stages:
  - debureaucratization: rewrites formal phrases — dangerous for regulatory text
  - liveliness: adds colloquial markers — already zero in 'formal' profile
  - paraphrasing / syntax_rewriting / naturalization: capped by max_change_ratio
  - coherence insertion: low intensity prevents unsolicited transitions

Protected terms below must never be altered by any stage.  Protection is
applied via two layers:

  1. _patch_formal_profile() (below) monkey-patches texthumanize.core.humanize
     to inject these terms as keep_keywords whenever profile='formal' is used.
     This patch fires when this module is imported — guaranteed when you call
     humanize() after importing from profiles.regulatory.

  2. pipeline.py reverts any paragraph where TextHumanize dropped a protected
     term even after the patch (defensive safety net).
"""

from __future__ import annotations
import logging

from texthumanize import HumanizeOptions

_LOG = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Protected terms
# ---------------------------------------------------------------------------
# Words and phrases that must never be touched by any pipeline stage.
# The QualityValidator will roll back any change that removes these.

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
    # Inflected forms of existing protected verbs
    "constituting",
    "implementing",
    "complying",
    "justifying",
    "verifies", "verifying",
    "validating",
    "maintains", "maintaining", "maintained",
    "establishes", "establishing", "established",
    # Modal verb compounds
    "shall not", "must not", "may not", "should not",
    # Additional regulatory noun forms
    "verifications", "validations", "implementations",
    "non-conformity", "non-conformities",
]


# ---------------------------------------------------------------------------
# Regulatory options factory
# ---------------------------------------------------------------------------

def _patch_formal_profile() -> None:
    """Patch texthumanize.core.humanize so profile='formal' auto-applies PROTECTED_TERMS.

    The lazy-import mechanism in texthumanize/__init__.py resolves the humanize
    function from texthumanize.core at import time. If this patch runs first
    (guaranteed when profiles.regulatory is imported before texthumanize), the
    patched version is what callers receive. This avoids modifying core source files.
    """
    try:
        import texthumanize.core as _core
        _orig = _core.humanize

        def _protected(text, *, profile: str = "web", constraints=None, **kw):
            if profile == "formal":
                c = dict(constraints) if constraints else {}
                c.setdefault("keep_keywords", PROTECTED_TERMS)
                constraints = c
            return _orig(text, profile=profile, constraints=constraints, **kw)

        _core.humanize = _protected
    except Exception as exc:
        _LOG.warning("[_patch_formal_profile] patch failed: %s — pipeline.py revert layer is still active", exc)


_patch_formal_profile()

# Extracted from get_regulatory_options to satisfy NASA ≤40-line rule.
_REGULATORY_PRESERVE = {
    "code_blocks": True, "urls": True, "emails": True, "hashtags": True,
    "mentions": True, "markdown": True, "html": True, "numbers": True,
    "dates": True, "prices": True, "identifiers": True, "quoted_text": True,
    "named_entities": True, "domain_terms": True,
    "domains": ["medical", "regulatory", "legal"], "brand_terms": [],
}
_REGULATORY_CONSTRAINTS = {
    "min_sentence_length": 5,
    "keep_keywords": PROTECTED_TERMS,
    "max_change_ratio": 0.05,
    "max_detection_loops": 0,
}


def get_regulatory_options(seed: int | None = 42) -> HumanizeOptions:
    """Return HumanizeOptions for regulated professional documents.

    Uses profile='formal', intensity=15, max_change_ratio=0.05,
    keep_keywords=PROTECTED_TERMS, max_detection_loops=0.
    Seed defaults to 42 for reproducible output.
    """
    return HumanizeOptions(
        lang="en",
        profile="formal",
        intensity=15,
        preserve=_REGULATORY_PRESERVE,
        constraints=_REGULATORY_CONSTRAINTS,
        seed=seed,
    )

"""Detects whether a text is a regulated document (ISO, EU MDR, IEC 62304, etc.)."""
from __future__ import annotations
import re

_REGULATED_KEYWORDS = [
    "iso 13485", "iso 14971", "iso 62304", "iec 62304", "en 62366",
    "eu mdr", "2017/745", "93/42/eec", "mdr",
    "notified body", "risk management plan", "risk management report",
    "clinical evaluation", "post-market surveillance", "post market surveillance",
    "intended purpose", "intended use",
    "fmea", "qms", "quality management system",
    "annex i", "annex ii", "annex iii", "annex ix", "annex x", "annex xiv",
    "vigilance", "eudamed",
    r"\biso\b", r"\biec\b",
]

_KEYWORD_RES = [re.compile(kw, re.IGNORECASE) for kw in _REGULATED_KEYWORDS]

# "shall" alone is kept separate — it's a strong signal but common in general writing too
_SHALL_RE = re.compile(r"\bshall\b", re.IGNORECASE)

_THRESHOLD = 2  # ≥2 keyword matches → regulated


def _count_matches(text: str) -> int:
    """Count distinct keyword patterns that match in text."""
    count = 0
    for pattern in _KEYWORD_RES:
        if pattern.search(text):
            count += 1
    if _SHALL_RE.search(text):
        count += 1
    return count


def is_regulated_document(text: str) -> bool:
    """Return True if text contains ≥2 regulated-document keyword matches."""
    if not text or not text.strip():
        return False
    return _count_matches(text) >= _THRESHOLD

"""Detects 9 Claude writing patterns in text."""
from __future__ import annotations
import logging
import re
import statistics

_LOG = logging.getLogger(__name__)
_NLP = None
_SPACY_CHAR_LIMIT = 5000  # truncate before spaCy to keep inference fast

_CONNECTORS = re.compile(
    r"^(Furthermore|Additionally|Moreover|In addition|It is important to note|"
    r"It should be noted|In conclusion|Ultimately)",
    re.IGNORECASE,
)
_NOMINAL = re.compile(r"\b\w+(?:tion|ment|ance|ence|ity)\b", re.IGNORECASE)


def _get_nlp():
    global _NLP
    if _NLP is None:
        import spacy
        _NLP = spacy.load("en_core_web_sm")
    return _NLP


def _count_connectors(text: str) -> int:
    """Count sentences starting with formulaic AI connectors."""
    return sum(1 for line in text.split(". ") if _CONNECTORS.match(line.strip()))


def _burstiness_score(text: str) -> float:
    """Coefficient of variation of sentence lengths (stddev/mean). Lower = more uniform = more AI."""
    nlp = _get_nlp()
    try:
        doc = nlp(text[:_SPACY_CHAR_LIMIT])
        lengths = [len(list(s)) for s in doc.sents if len(list(s)) > 1]
    except Exception as exc:
        _LOG.warning("[_burstiness_score] spaCy failed: %s — falling back to simple split", exc)
        lengths = [len(s.split()) for s in text.split(". ") if s.strip()]
    if len(lengths) < 2:
        return 0.0
    mean = statistics.mean(lengths)
    if mean == 0:
        return 0.0
    return round(statistics.stdev(lengths) / mean, 3)  # coefficient of variation


def _nominalisation_ratio(text: str) -> float:
    """Fraction of words that are nominalisations (-tion/-ment etc)."""
    words = text.split()
    if not words:
        return 0.0
    nominals = len(_NOMINAL.findall(text))
    return round(nominals / len(words), 3)


_PASSIVE_RE = re.compile(
    r'\b(is|are|was|were|been|being)\s+\w+ed\b', re.IGNORECASE
)


def _passive_voice_density(text: str) -> float:
    """Fraction of sentences containing passive voice constructions."""
    sentences = [s.strip() for s in re.split(r'[.!?]+', text) if len(s.strip().split()) > 3]
    if not sentences:
        return 0.0
    passive = sum(1 for s in sentences if _PASSIVE_RE.search(s))
    return round(passive / len(sentences), 3)


def _known_new_violations(paragraphs: list[str]) -> int:
    """Count paragraph pairs with no known-new dependency."""
    try:
        from known_new_contract_checker import check_known_new
        pairs = check_known_new(paragraphs)
        return sum(1 for p in pairs if p.get("reorderable", False))
    except Exception as exc:
        _LOG.warning("[_known_new_violations] failed: %s", exc)
        return 0


def _is_low_burstiness(para: str) -> bool:
    """True if sentence lengths are suspiciously uniform (an AI writing tell)."""
    sentences = [s.strip() for s in para.split(". ") if s.strip()]
    if len(sentences) < 2:
        return False
    lengths = [len(s.split()) for s in sentences]
    return max(lengths) - min(lengths) < 5


def _flag_paragraphs(paragraphs: list[str], threshold: int = 2) -> list[int]:
    """Return indices of paragraphs with >= threshold pattern signals (mirrors _count_signals)."""
    flagged = []
    for i, para in enumerate(paragraphs):
        signals = 0
        if _CONNECTORS.match(para.strip()):
            signals += 1
        if _NOMINAL.search(para):
            signals += 1
        if _is_low_burstiness(para):
            signals += 1
        if _passive_voice_density(para) > 0.2:
            signals += 1
        if signals >= threshold:
            flagged.append(i)
    return flagged


def detect_patterns(text: str, threshold: int = 2) -> dict:
    """Detect Claude writing patterns. Returns pattern_counts and flagged_paragraphs.

    threshold controls the minimum signal count for a paragraph to appear in
    flagged_paragraphs. Pass the same value used in run_pipeline_v2's
    intensity_threshold to get a consistent diagnostic view.
    """
    text = text.replace("\r\n", "\n")
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    return {
        "pattern_counts": {
            "formulaic_connectors": _count_connectors(text),
            "burstiness_score": _burstiness_score(text),
            "nominalisation_ratio": _nominalisation_ratio(text),
            "known_new_violations": _known_new_violations(paragraphs),
            "passive_voice_density": _passive_voice_density(text),
        },
        "flagged_paragraphs": _flag_paragraphs(paragraphs, threshold=threshold),
    }

"""Known-New Contract checker: identifies additive paragraph structure using spaCy."""
from __future__ import annotations
import logging

_LOG = logging.getLogger(__name__)
_NLP: object = None
_MIN_PARA_WORDS = 4


def _get_nlp() -> object:
    """Lazy-load spaCy English model."""
    global _NLP
    if _NLP is None:
        import spacy
        _NLP = spacy.load("en_core_web_sm")
    return _NLP


def _last_noun_chunk(para: str) -> str:
    """Return the last noun chunk in a paragraph as a string."""
    nlp = _get_nlp()
    doc = nlp(para)
    chunks = list(doc.noun_chunks)
    if chunks:
        return chunks[-1].text
    content = [t for t in doc if t.is_alpha and not t.is_stop]
    return content[-1].text if content else ""


def _first_noun_chunk(para: str) -> str:
    """Return the first noun chunk in a paragraph as a string."""
    nlp = _get_nlp()
    doc = nlp(para)
    chunks = list(doc.noun_chunks)
    if chunks:
        return chunks[0].text
    content = [t for t in doc if t.is_alpha and not t.is_stop]
    return content[0].text if content else ""


def _share_root_tokens(concept_a: str, concept_b: str) -> bool:
    """True if both concepts share at least one lemmatised content word."""
    nlp = _get_nlp()
    lemmas_a = {t.lemma_.lower() for t in nlp(concept_a) if t.is_alpha and not t.is_stop}
    lemmas_b = {t.lemma_.lower() for t in nlp(concept_b) if t.is_alpha and not t.is_stop}
    return bool(lemmas_a & lemmas_b)


def check_known_new(paragraphs: list[str]) -> list[dict]:
    """Identify paragraph pairs where P(N+1) does not echo P(N)'s ending concept.

    reorderable=True means the two paragraphs share no known-new dependency —
    they could be swapped without losing logical continuity. This is the structural
    AI-writing tell: additive rather than serial paragraph flow.
    """
    results = []
    valid = [p for p in paragraphs if len(p.split()) >= _MIN_PARA_WORDS]
    for i in range(len(valid) - 1):
        ending = _last_noun_chunk(valid[i])
        opening = _first_noun_chunk(valid[i + 1])
        shared = _share_root_tokens(ending, opening)
        results.append({
            "pair_index": i,
            "p_n_ending_concept": ending,
            "p_n1_opening_concept": opening,
            "reorderable": not shared,
        })
    return results

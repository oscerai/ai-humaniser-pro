"""Known-new contract fixer: rewrites paragraph N+1 openings to chain from paragraph N."""
from __future__ import annotations
import logging

from proxy_client import call_proxy

_LOG = logging.getLogger(__name__)
_MAX_TOKENS = 300

_SYSTEM_PROMPT = (
    "You are a regulatory document editor. You will receive an ENDING CONCEPT and paragraph 2. "
    "Prepend EXACTLY ONE of these patterns to the start of paragraph 2:\n"
    "  - 'This [ending concept]...' (if singular)\n"
    "  - 'These [ending concept]...' (if plural)\n"
    "  - 'Such [ending concept]...' (if fits)\n"
    "Use ONLY the exact words given as the ENDING CONCEPT. Do not use any other words. "
    "Do not change, add to, or remove anything else in paragraph 2. "
    "If the ending concept cannot fit as 'This/These/Such [concept]' naturally, return paragraph 2 UNCHANGED. "
    "Return ONLY the complete second paragraph with the prepended phrase."
)


def _call_proxy(para_n: str, para_n1: str, ending_concept: str) -> str:
    """Build request body and call Heidi proxy to rewrite para_n1 opening."""
    user_msg = (
        f"ENDING CONCEPT OF PARAGRAPH 1 (use these exact words in the new opening): "
        f"'{ending_concept}'\n\n"
        f"PARAGRAPH 1:\n{para_n}\n\n"
        f"PARAGRAPH 2 (rewrite its opening sentence to reference '{ending_concept}'):\n{para_n1}"
    )
    body = {
        "model": "claude-haiku-4-5-20251001",
        "max_tokens": _MAX_TOKENS,
        "temperature": 0,
        "system": [{"type": "text", "text": _SYSTEM_PROMPT, "cache_control": {"type": "ephemeral"}}],
        "messages": [{"role": "user", "content": user_msg}],
    }
    return call_proxy(body)


def _terms_dropped(original: str, rewritten: str) -> list[str]:
    """Return protected terms present in original but absent from rewritten."""
    from profiles.regulatory import PROTECTED_TERMS
    return [
        t for t in PROTECTED_TERMS
        if t.lower() in original.lower() and t.lower() not in rewritten.lower()
    ]


_MAX_LENGTH_GROWTH = 1.25  # revert if rewritten para is >25% longer than original (hallucination signal)


def _fix_pair(para_n: str, para_n1: str, ending_concept: str) -> str:
    """Rewrite para_n1 to open with the exact ending concept from para_n."""
    try:
        result = _call_proxy(para_n, para_n1, ending_concept).strip()
    except Exception as exc:
        _LOG.warning("[_fix_pair] proxy failed: %s — reverting", exc)
        return para_n1
    if not result:
        return para_n1
    # Length guard: revert if result is significantly longer (hallucination signal)
    orig_words = len(para_n1.split())
    result_words = len(result.split())
    if orig_words > 0 and result_words / orig_words > _MAX_LENGTH_GROWTH:
        _LOG.info("[_fix_pair] result %d words vs original %d (>25%% growth) — reverting", result_words, orig_words)
        return para_n1
    dropped = _terms_dropped(para_n1, result)
    if dropped:
        _LOG.info("[_fix_pair] protected terms dropped %s — reverting", dropped)
        return para_n1
    return result


def fix_known_new(paragraphs: list[str]) -> list[str]:
    """Fix known-new violations: rewrite paragraph openings to chain from the previous.

    Uses check_known_new to find reorderable pairs, then rewrites para N+1 opening
    to reference para N's ending concept. Reverts any rewrite that drops a protected term.
    """
    if len(paragraphs) < 2:
        return list(paragraphs)
    try:
        from known_new_contract_checker import check_known_new
    except ImportError:
        _LOG.warning("[fix_known_new] known_new_contract_checker unavailable — skipping")
        return list(paragraphs)
    pairs = check_known_new(paragraphs)
    # pair_index from check_known_new indexes into valid[] (≥4-word paras), not paragraphs[].
    # Build the mapping so we modify the correct paragraphs.
    valid_idxs = [i for i, p in enumerate(paragraphs) if len(p.split()) >= 4]
    result = list(paragraphs)
    for pair in pairs:
        if not pair.get("reorderable", False):
            continue
        vi = pair["pair_index"]  # index into valid[]
        if vi + 1 >= len(valid_idxs):
            continue
        n_idx = valid_idxs[vi]        # real index in result[]
        n1_idx = valid_idxs[vi + 1]   # real index in result[]
        ending = pair["p_n_ending_concept"]
        if not ending:
            _LOG.info("[fix_known_new] pair %d skipped — empty ending concept", vi)
            continue
        _LOG.info("[fix_known_new] fixing para %d→%d: echo '%s'", n_idx, n1_idx, ending)
        result[n1_idx] = _fix_pair(result[n_idx], result[n1_idx], ending)
    return result

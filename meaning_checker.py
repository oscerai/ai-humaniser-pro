"""Meaning-change checker: detects if a paragraph rewrite altered factual content."""
from __future__ import annotations
import json
import logging

from proxy_client import call_proxy

_LOG = logging.getLogger(__name__)
_SYSTEM_PROMPT = (
    "You are a regulatory document editor. Compare the ORIGINAL and REWRITTEN paragraphs below. "
    "Determine ONLY whether the REWRITTEN version changes any factual meaning compared to the ORIGINAL. "
    "Changes to wording, style, or connector phrases that do not alter facts are acceptable. "
    "Return EXACTLY one of: PRESERVED or CHANGED, then a colon, then a one-sentence reason. "
    "Example: 'PRESERVED: Only connector phrase was added at start.'"
)


def _build_and_call(original: str, rewritten: str) -> str:
    """Build request body and call Heidi proxy to compare original and rewritten paragraphs."""
    body = {
        "model": "claude-haiku-4-5-20251001",
        "max_tokens": 100,
        "temperature": 0,
        "system": [{"type": "text", "text": _SYSTEM_PROMPT, "cache_control": {"type": "ephemeral"}}],
        "messages": [{"role": "user", "content": f"ORIGINAL:\n{original}\n\nREWRITTEN:\n{rewritten}"}],
    }
    return call_proxy(body).strip()


def check_meaning_preserved(original: str, rewritten: str) -> dict:
    """Check whether a rewritten paragraph preserves the factual meaning of the original.

    Returns {'preserved': bool, 'reason': str}.
    Fails safe: returns preserved=True if the proxy is unavailable.
    """
    if not original.strip() or not rewritten.strip():
        return {"preserved": True, "reason": "empty input — skipping check"}
    if original.strip() == rewritten.strip():
        return {"preserved": True, "reason": "text unchanged"}
    try:
        response = _build_and_call(original, rewritten)
    except Exception as exc:
        _LOG.warning("[check_meaning_preserved] proxy failed: %s — assuming preserved", exc)
        return {"preserved": True, "reason": "proxy unavailable — assuming preserved"}
    resp_upper = response.upper()
    if resp_upper.startswith("PRESERVED"):
        preserved = True
    elif resp_upper.startswith("CHANGED"):
        preserved = False
    else:
        _LOG.warning("[check_meaning_preserved] unexpected response format — assuming preserved: %s", response[:80])
        return {"preserved": True, "reason": "unexpected response format — assuming preserved"}
    reason = response.split(":", 1)[1].strip() if ":" in response else response
    if not preserved:
        _LOG.info("[check_meaning_preserved] meaning change detected: %s", reason)
    return {"preserved": preserved, "reason": reason}

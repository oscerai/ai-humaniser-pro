"""Claude API paragraph rewriter via Heidi proxy — targets 9 Claude writing patterns."""
from __future__ import annotations
import logging

from proxy_client import call_proxy

_LOG = logging.getLogger(__name__)
_MAX_TOKENS = 1024

_SYSTEM_PROMPT = (
    "You are a regulatory document editor. Rewrite the paragraph below to sound like "
    "a confident human expert wrote it. Apply these specific changes where present:\n"
    "- Remove or replace formulaic connectors at sentence starts: Furthermore, Additionally, "
    "Moreover, In addition, It is important to note, It should be noted\n"
    "- Vary sentence length: if sentences are all similar length, break one into two short "
    "sentences or merge two short ones\n"
    "- Reverse nominalisations: 'the implementation of X' -> 'implementing X', "
    "'the utilization of' -> 'using', 'the establishment of' -> 'establishing'\n"
    "- If context_before is given and this paragraph does not echo its ending concept, "
    "rewrite the opening to create a logical link\n"
    "Rules:\n"
    "- Preserve all factual content and regulatory meaning exactly\n"
    "- Never remove or paraphrase protected regulatory terms (shall, must, demonstrate, "
    "verify, validate, risk management, etc.)\n"
    "- Return ONLY the rewritten paragraph — no explanation, no preamble"
)


def _call_proxy(system_prompt: str, user_message: str) -> str:
    """Build request body and call Heidi proxy. Returns response text."""
    body = {
        "model": "claude-haiku-4-5-20251001",
        "max_tokens": _MAX_TOKENS,
        "temperature": 0,
        "system": [{"type": "text", "text": system_prompt, "cache_control": {"type": "ephemeral"}}],
        "messages": [{"role": "user", "content": user_message}],
    }
    return call_proxy(body)


def _protected_terms_dropped(original: str, rewritten: str) -> list[str]:
    """Return list of protected terms present in original but absent from rewritten."""
    from profiles.regulatory import PROTECTED_TERMS
    return [
        t for t in PROTECTED_TERMS
        if t.lower() in original.lower() and t.lower() not in rewritten.lower()
    ]


def rewrite_paragraph(para: str, context_before: str = "") -> str:
    """Rewrite para to remove Claude patterns. Reverts if protected terms dropped."""
    if not para or not para.strip():
        return para
    if context_before:
        user_msg = f"context_before: {context_before}\n\nparagraph: {para}"
    else:
        user_msg = para
    try:
        result = _call_proxy(_SYSTEM_PROMPT, user_msg).strip()
    except Exception as exc:
        _LOG.warning("[rewrite_paragraph] proxy call failed: %s — reverting", exc)
        return para
    dropped = _protected_terms_dropped(para, result)
    if dropped:
        _LOG.info("[rewrite_paragraph] protected terms dropped %s — reverting", dropped)
        return para
    return result

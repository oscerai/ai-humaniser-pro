"""RCA test: 3 prompt variants for known-new fixer, measured on 5 regulatory para pairs."""
from __future__ import annotations
import json
import logging
import re

from proxy_client import call_proxy

_LOG = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(message)s")
_KNOWN_NEW_SYSTEM_A = (
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
_KNOWN_NEW_SYSTEM_B = (
    _KNOWN_NEW_SYSTEM_A + "\n\n"
    "CRITICAL: Your output MUST NOT contain any word, phrase, or sentence that does not "
    "appear verbatim in either PARAGRAPH 1 or PARAGRAPH 2 as given above. "
    "If a natural connector cannot be formed using only words already present, "
    "return PARAGRAPH 2 UNCHANGED."
)
_KNOWN_NEW_SYSTEM_C = (
    "Return EXACTLY the following and nothing else: "
    "'This [ending_concept] ' followed by PARAGRAPH 2 verbatim. "
    "Do not change any other character. "
    "If [ending_concept] does not fit grammatically, return PARAGRAPH 2 unchanged."
)
_VARIANTS = {"Variant A": _KNOWN_NEW_SYSTEM_A, "Variant B": _KNOWN_NEW_SYSTEM_B, "Variant C": _KNOWN_NEW_SYSTEM_C}


def _call_variant(system: str, para_n: str, para_n1: str, ending: str) -> str:
    """Build request body and call proxy with a given system prompt. temperature=0 for determinism."""
    user_msg = (
        f"ENDING CONCEPT OF PARAGRAPH 1 (use these exact words): '{ending}'\n\n"
        f"PARAGRAPH 1:\n{para_n}\n\n"
        f"PARAGRAPH 2:\n{para_n1}"
    )
    body = {
        "model": "claude-haiku-4-5-20251001",
        "max_tokens": 300,
        "temperature": 0,
        "system": [{"type": "text", "text": system, "cache_control": {"type": "ephemeral"}}],
        "messages": [{"role": "user", "content": user_msg}],
    }
    return call_proxy(body).strip()


def _hallucination_rate(n: str, n1: str, rewritten: str) -> float:
    """Fraction of output words not present in either input paragraph."""
    def words(text: str) -> set:
        return set(re.sub(r"[^a-z0-9 ]", "", text.lower()).split()) - {""}
    allowed = words(n) | words(n1)
    out_words = words(rewritten)
    if not out_words:
        return 0.0
    return round(len(out_words - allowed) / len(out_words), 3)


def _ending_concept(para: str) -> str:
    """Last 3 content words as ending concept approximation."""
    content_words = [w for w in para.rstrip(".!?").split() if len(w) > 2]
    return " ".join(content_words[-3:]) if len(content_words) >= 3 else " ".join(content_words)


def _run_variant(name: str, system: str, pairs: list[tuple[str, str]]) -> dict:
    """Run one variant on all pairs. Return aggregate hallucination metrics."""
    h_rates, growth_ratios, reversions = [], [], []
    for para_n, para_n1 in pairs:
        ending = _ending_concept(para_n)
        try:
            result = _call_variant(system, para_n, para_n1, ending)
        except Exception as exc:
            _LOG.warning("[%s] proxy failed: %s — counting as reversion", name, exc)
            reversions.append(1)
            h_rates.append(0.0)
            growth_ratios.append(1.0)
            continue
        orig_words = len(para_n1.split())
        result_words = len(result.split())
        growth = result_words / orig_words if orig_words else 1.0
        reverted = growth > 1.25 or result == para_n1
        reversions.append(1 if reverted else 0)
        h_rates.append(_hallucination_rate(para_n, para_n1, result))
        growth_ratios.append(growth)
        _LOG.info("[%s] hallucination=%.3f growth=%.2f reverted=%s", name, h_rates[-1], growth, reverted)
    mean_h = round(sum(h_rates) / len(h_rates), 3) if h_rates else 0.0
    max_g = round(max(growth_ratios), 3) if growth_ratios else 1.0
    rev_rate = round(sum(reversions) / len(reversions), 3) if reversions else 0.0
    return {"name": name, "mean_hallucination": mean_h, "max_growth": max_g,
            "reversion_rate": rev_rate, "safe": mean_h < 0.02 and rev_rate < 0.5}


def _write_results(results: list[dict]) -> None:
    """Write rca-results and decision files."""
    safe_variants = [r["name"] for r in results if r["safe"]]
    verdict = "FIXABLE" if safe_variants else "KEEP DISABLED"
    with open("rca-results-2026-06-22.txt", "w") as f:
        f.write("RCA Results — Known-New Fixer Hallucination Test — 2026-06-22\n" + "=" * 60 + "\n\n")
        for r in results:
            f.write(f"{r['name']}\n  Mean hallucination: {r['mean_hallucination']}\n"
                    f"  Max growth: {r['max_growth']}\n  Reversion rate: {r['reversion_rate']}\n"
                    f"  Verdict: {'SAFE' if r['safe'] else 'HALLUCINATION RISK'}\n\n")
        f.write(f"Overall: {verdict}\n")
    with open("known_new_fixer_decision.md", "w") as f:
        f.write(f"# Known-New Fixer Decision — 2026-06-22\n\nVERDICT: {verdict}\n\n## Basis\n\n")
        for r in results:
            f.write(f"- {r['name']}: hallucination={r['mean_hallucination']} reversion={r['reversion_rate']} "
                    f"— {'SAFE' if r['safe'] else 'RISK'}\n")
        note = f"\nSafe variants: {', '.join(safe_variants)}\n" if safe_variants else \
               "\nNo variant produced <2% hallucination. Fixer must remain disabled.\n"
        f.write(note)


def main() -> None:
    txt = open("test-regulatory-extract.txt").read()
    paras = [p.strip() for p in txt.split("\n\n") if p.strip()]
    pairs = [(paras[i], paras[i + 1]) for i in range(min(5, len(paras) - 1))]
    results = [_run_variant(name, system, pairs) for name, system in _VARIANTS.items()]
    _write_results(results)
    print("\n=== RCA COMPLETE ===")
    for r in results:
        print(f"{r['name']}: hallucination={r['mean_hallucination']} reversion={r['reversion_rate']} safe={r['safe']}")
    safe = [r["name"] for r in results if r["safe"]]
    print(f"VERDICT: {'FIXABLE — ' + ', '.join(safe) if safe else 'KEEP DISABLED'}")


if __name__ == "__main__":
    main()

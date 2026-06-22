"""AI Humaniser Pro v2 pipeline: pattern-detect then Claude-API rewrite."""
from __future__ import annotations
import logging
from concurrent.futures import ThreadPoolExecutor

_LOG = logging.getLogger(__name__)
_DEFAULT_THRESHOLD = 2
_DEFAULT_MAX_WORKERS = 4  # concurrent rewrite calls; keeps Heidi proxy load manageable


def _split_paragraphs(text: str) -> list[str]:
    """Split text on double newlines; normalise Windows line endings first."""
    return [p.strip() for p in text.replace("\r\n", "\n").split("\n\n") if p.strip()]


_PASSIVE_SIGNAL_THRESHOLD = 0.2  # fraction of sentences that must be passive to count as a signal


def _count_signals(para: str) -> int:
    """Count how many pattern signals fire for one paragraph (max 4)."""
    from pattern_detector import _CONNECTORS, _NOMINAL, _is_low_burstiness, _passive_voice_density
    count = 0
    if _CONNECTORS.match(para.strip()):
        count += 1
    if _NOMINAL.search(para):
        count += 1
    if _is_low_burstiness(para):
        count += 1
    if _passive_voice_density(para) > _PASSIVE_SIGNAL_THRESHOLD:
        count += 1
    return count


def _process_paragraph(para: str, prev: str, threshold: int, check_meaning: bool = False) -> str:
    """Rewrite paragraph if it has enough pattern signals; optionally check meaning is preserved."""
    if _count_signals(para) < threshold:
        return para
    from rewriter import rewrite_paragraph
    rewritten = rewrite_paragraph(para, context_before=prev)
    if check_meaning:
        from meaning_checker import check_meaning_preserved
        result = check_meaning_preserved(para, rewritten)
        if not result["preserved"]:
            _LOG.warning("[_process_paragraph] meaning change detected — reverting. Reason: %s", result["reason"])
            return para
    return rewritten


def _process_paragraphs_parallel(
    paragraphs: list[str], threshold: int, max_workers: int, check_meaning: bool = False
) -> list[str]:
    """Process paragraphs concurrently; I/O-bound rewriting is safe to parallelise."""
    def _process_one(item: tuple) -> str:
        i, para = item
        prev = paragraphs[i - 1] if i > 0 else ""
        return _process_paragraph(para, prev, threshold, check_meaning=check_meaning)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        return list(executor.map(_process_one, enumerate(paragraphs)))


def _apply_known_new_fix(paragraphs: list[str]) -> list[str]:
    """Apply known-new contract fix as a second humanisation pass."""
    try:
        from known_new_fixer import fix_known_new
        result = fix_known_new(paragraphs)
        _LOG.info("[_apply_known_new_fix] known-new fix applied to %d paragraphs", len(result))
        return result
    except ImportError as exc:
        _LOG.warning("[_apply_known_new_fix] known_new_fixer unavailable: %s — skipping", exc)
        return paragraphs
    except Exception as exc:
        _LOG.warning("[_apply_known_new_fix] failed: %s — returning unmodified", exc)
        return paragraphs


def run_pipeline_v2(
    text: str,
    intensity_threshold: int = _DEFAULT_THRESHOLD,
    max_workers: int = _DEFAULT_MAX_WORKERS,
    apply_known_new: bool = False,
    check_meaning: bool = True,
) -> str:
    """Humanise text: parallel pattern-detect → rewrite → optional known-new chain.

    apply_known_new is OFF by default for regulatory documents.
    check_meaning is ON by default: reverts any rewrite that changes factual content.

    Note: for regulated documents (ISO, EU MDR, IEC 62304, etc.), check_meaning is
    forced to True and apply_known_new to False regardless of what you pass — these
    settings cannot be overridden for regulated content. Pass check_meaning=False only
    for non-regulatory text where meaning verification is not required.
    """
    if not text or not text.strip():
        return text
    from regulatory_classifier import is_regulated_document
    if is_regulated_document(text):
        _LOG.info(
            "[run_pipeline_v2] Regulatory document detected — meaning check enabled, known-new fixer disabled"
        )
        apply_known_new = False
        check_meaning = True
    paragraphs = _split_paragraphs(text)
    processed = _process_paragraphs_parallel(
        paragraphs, intensity_threshold, max_workers, check_meaning=check_meaning
    )
    if apply_known_new:
        processed = _apply_known_new_fix(processed)
    return "\n\n".join(processed)

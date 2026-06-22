"""DistilGPT-2 perplexity scorer — replaces HC3 for Claude-era text detection."""
from __future__ import annotations
import logging
import math

_LOG = logging.getLogger(__name__)
_MODEL_CACHE: dict = {}
_MODEL_LOAD_FAILED: set = set()  # prevents retry storms on persistent failures
_MIN_WORDS = 5
_MAX_TOKEN_LENGTH = 512  # DistilGPT-2 input token limit


def _load_model(model_name: str = "distilgpt2") -> tuple:
    """Lazy-load DistilGPT-2 and cache it."""
    if model_name not in _MODEL_CACHE:
        import torch
        from transformers import GPT2Tokenizer, GPT2LMHeadModel
        tokenizer = GPT2Tokenizer.from_pretrained(model_name)
        model = GPT2LMHeadModel.from_pretrained(model_name)
        model.eval()
        if torch.backends.mps.is_available():
            device = torch.device("mps")
        else:
            device = torch.device("cpu")
        model.to(device)
        _MODEL_CACHE[model_name] = (tokenizer, model, device)
    return _MODEL_CACHE[model_name]


def _compute_perplexity(text: str) -> float:
    """Return perplexity via DistilGPT-2. Higher = more human (less predictable)."""
    if len(text.split()) < _MIN_WORDS:
        return 50.0
    model_name = "distilgpt2"
    if model_name in _MODEL_LOAD_FAILED:
        return 50.0  # skip retry; model previously failed to load
    try:
        import torch
        tokenizer, model, device = _load_model(model_name)
        enc = tokenizer(text, return_tensors="pt", truncation=True, max_length=_MAX_TOKEN_LENGTH)
        input_ids = enc["input_ids"].to(device)
        with torch.no_grad():
            outputs = model(input_ids, labels=input_ids)
        return round(math.exp(outputs.loss.item()), 2)
    except Exception as exc:
        _MODEL_LOAD_FAILED.add(model_name)
        _LOG.warning("[_compute_perplexity] failed: %s — returning 50.0 (further calls skipped)", exc)
        return 50.0


def _structural_score(paragraphs: list[str]) -> float:
    """Return fraction of paragraph pairs with no known-new dependency."""
    if len(paragraphs) < 2:
        return 0.0
    try:
        from known_new_contract_checker import check_known_new
    except ImportError:
        _LOG.warning("[_structural_score] known_new_contract_checker unavailable")
        return 0.0
    pairs = check_known_new(paragraphs)
    if not pairs:
        return 0.0
    reorderable = sum(1 for p in pairs if p.get("reorderable", False))
    return round(reorderable / len(pairs), 3)


def score_document_v2(text: str) -> dict:
    """Score document for AI-ness. Higher perplexity = more human."""
    text = text.replace("\r\n", "\n")
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    return {
        "perplexity": _compute_perplexity(text),
        "structural_score": _structural_score(paragraphs),
    }

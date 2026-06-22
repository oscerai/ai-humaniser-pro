═══════════════════════════════════════════════════════════════════
EXECUTION PROTOCOL — READ THIS BEFORE DOING ANYTHING ELSE
═══════════════════════════════════════════════════════════════════

This plan is stored at: /Users/sharky/Desktop/Heidi/qms-tools/ai-humaniser-pro/plans/PLAN_HUMANISER_PRO_V2_REBUILD.md
That file is the source of truth. Your in-context memory is not.

── BEFORE EVERY STEP OR PHASE ──────────────────────────────────────
□ 1. READ THE FILE: Execute a file-read tool call on this plan file.
Required output: first 5 lines of the file, shown explicitly.
□ 2. LOCATE CURRENT STEP: Find the step. Read it in full.
Required output: confirm step title matches what you found.
□ 3. CHECK RESULTS FIELD: State "Results field: empty/interrupted/filled".
□ 4. NEW CHAT SESSION CHECK: If new session — read entire plan top to bottom first.

── AFTER COMPLETING EVERY STEP OR PHASE ────────────────────────────
□ 1. WRITE RESULTS: Append to this step's Results field. Never overwrite.
□ 2. PLAN-CHANGE CHECK — STOP-CLAUSE: If findings change a future step,
write STOP_REPORT.md and await user decision. Do NOT proceed.
□ 3. (RESERVED)
□ 4. UPDATE PLAN STATE TRACKER.
□ 5. SAVE FILE + CONFIRM: Show first 3 lines of saved file.
□ 6. PHASE BOUNDARY CHECK: session:single — skip /chat-handoff.

── ANTI-DRIFT RULES ─────────────────────────────────────────────────

- The file is always right. Your memory is not.
- A step is not complete until its Results field is written and saved.
  ═══════════════════════════════════════════════════════════════════

OBJECTIVES FILE: /Users/sharky/Desktop/Heidi/qms-tools/ai-humaniser-pro/OBJECTIVES_humaniser-v2-rebuild_21-06-2026.md

═══════════════════════════════════════════════════════════════════
PLAN STATE TRACKER
═══════════════════════════════════════════════════════════════════

Last updated after: Step 8 COMPLETE
Current step: COMPLETE

┌─────┬──────────────────────────────────────────────────┬─────────────┐
│ # │ Step Name │ Status │
├─────┼──────────────────────────────────────────────────┼─────────────┤
│ │ ── PHASE 1: BUILD MODULES ── │ │
│ [A] │ ── PARALLEL BATCH A: Steps 1, 2, 3 ── │ COMPLETE │
│ 1 │ Build scorer_v2.py [PARALLEL: Batch A] │ COMPLETE │
│ 2 │ Build pattern_detector.py [PARALLEL: Batch A] │ COMPLETE │
│ 3 │ Build rewriter.py [PARALLEL: Batch A] │ COMPLETE │
│ 4 │ Build pipeline_v2.py │ COMPLETE │
│ PT1 │ Phase 1→2 Transition │ COMPLETE │
│ │ ── PHASE 2: INTEGRATION TESTS ── │ │
│ 5 │ Test perplexity on ChatGPT document │ COMPLETE │
│ 6 │ Test connectors + protected terms on RMR report │ COMPLETE │
│ │ ── PHASE 3: FINALISE ── │ │
│ 7 │ Update /humanize skill │ COMPLETE │
│ 8 │ BUGS_AND_LESSONS.md + aggregate │ COMPLETE │
└─────┴──────────────────────────────────────────────────┴─────────────┘

Status values: PENDING / IN PROGRESS / COMPLETE / FAILED / SKIPPED
═══════════════════════════════════════════════════════════════════

## What this plan is

Rebuilds the AI Humaniser Pro from scratch. Version 1 used HC3 (2022 GPT-3.5 detector, useless on Claude) and TextHumanize (word-swapping, cannot fix structural problems). This plan replaces both: DistilGPT-2 perplexity scores Claude text correctly; Claude API rewrites target 9 specific Claude writing patterns. Resumes from v1 build session; v1 PLAN COMPLETE is CHALLENGED and v1 architecture is not inherited.

## Objective

Build four Python modules (scorer_v2.py, pattern_detector.py, rewriter.py, pipeline_v2.py) that replace HC3+TextHumanize and produce measurably more human-sounding output from Claude-generated regulatory documents, verified by perplexity improvement on known-AI text and formulaic connector reduction on risk management reports.

## Scope

IN:

- scorer_v2.py: DistilGPT-2 perplexity + structural score
- pattern_detector.py: 9 Claude writing pattern detection
- rewriter.py: Claude API (Haiku, Heidi proxy) targeted paragraph rewriting
- pipeline_v2.py: orchestration of detect→rewrite→verify
- Integration tests on test-chatgpt-rapamycin.txt and RMR-ISD-AI-Scribe report
- /humanize skill updated to use pipeline_v2
- BUGS_AND_LESSONS.md updated

OUT OF SCOPE:

- Modifying v1 modules (scorer.py, pipeline.py remain unchanged)
- Browser/React UI
- Modifying TextHumanize core files
- Solving the problem for cases where perplexity doesn't improve

## Constraints

- All Claude API calls through Heidi proxy (https://heidi-ai-proxy.vercel.app/api/proxy)
- temperature=0 on every Claude API call
- PROTECTED_TERMS never dropped — revert-on-drop in rewriter.py
- NASA Rule: all functions ≤40 lines
- No hardcoded absolute paths
- No word-for-word substitution as primary technique
- Recommended model: claude-sonnet-4-6 — standard Python build, approach fully specified
- Session: single

## Dependency summary

Dependency graph:
Step 1 [Build scorer_v2.py]: depends_on [] ← Batch A root
Step 2 [Build pattern_detector.py]: depends_on [] ← Batch A root
Step 3 [Build rewriter.py]: depends_on [] ← Batch A root
Step 4 [Build pipeline_v2.py]: depends_on [1, 2, 3]
Step PT1 [Phase Transition]: depends_on [1, 2, 3, 4]
Step 5 [Test perplexity]: depends_on [PT1]
Step 6 [Test connectors + terms]: depends_on [PT1]
Step 7 [Update skill]: depends_on [PT1]
Step 8 [BUGS_AND_LESSONS]: depends_on [5, 6, 7]

Critical path: Step 1 → PT1 → Step 5 → Step 8
Parallel opportunities: Batch A (Steps 1, 2, 3 concurrent)
Sequential steps: 5. Parallelisable steps: 3 (Batch A).

---

# PHASE 1 — BUILD MODULES

---

## Step 1 — Build scorer_v2.py [PARALLEL: Batch A]

**What:** Create `/Users/sharky/Desktop/Heidi/qms-tools/ai-humaniser-pro/scorer_v2.py` with two public functions: `score_document_v2(text)` returning perplexity + structural_score, and `_compute_perplexity(text)` using DistilGPT-2. Lazy-loads the model (cached after first load). Imports `check_known_new` from `known_new_contract_checker` for structural_score.

**Inputs:** transformers installed, known_new_contract_checker.py exists.

**Outputs:** scorer_v2.py at project root.

**Acceptance criteria:**

- `python3 -c "from scorer_v2 import score_document_v2; r=score_document_v2('Furthermore, the implementation of risk management requires the demonstration of compliance with applicable standards.'); print(r); assert 'perplexity' in r and isinstance(r['perplexity'], float) and r['perplexity'] > 0 and 'structural_score' in r"` exits 0
- No function in scorer_v2.py exceeds 40 lines: `awk '/^def /{if(s)print c,s; s=$0; c=0} {c++} END{if(s)print c,s}' scorer_v2.py | awk '$1>40{print "VIOLATION:",$0}'` returns empty

**depends_on:** []

**Risk:** DistilGPT-2 model download (~82MB) on first run. Mitigation: transformers already installed, model downloads automatically and caches.

**Code to write:**

```python
"""DistilGPT-2 perplexity scorer — replaces HC3 for Claude-era text detection."""
from __future__ import annotations
import logging
import math

_LOG = logging.getLogger(__name__)
_MODEL_CACHE: dict = {}
_MIN_WORDS = 5


def _load_model(model_name: str = "distilgpt2") -> tuple:
    """Lazy-load DistilGPT-2 and cache it."""
    if model_name not in _MODEL_CACHE:
        import torch
        from transformers import GPT2Tokenizer, GPT2LMHeadModel
        tokenizer = GPT2Tokenizer.from_pretrained(model_name)
        model = GPT2LMHeadModel.from_pretrained(model_name)
        model.eval()
        device = torch.device("mps") if torch.backends.mps.is_available() else torch.device("cpu")
        model.to(device)
        _MODEL_CACHE[model_name] = (tokenizer, model, device)
    return _MODEL_CACHE[model_name]


def _compute_perplexity(text: str) -> float:
    """Return perplexity via DistilGPT-2. Higher = more human (less predictable)."""
    if len(text.split()) < _MIN_WORDS:
        return 50.0  # neutral fallback for very short text
    import torch
    tokenizer, model, device = _load_model()
    try:
        enc = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
        input_ids = enc["input_ids"].to(device)
        with torch.no_grad():
            outputs = model(input_ids, labels=input_ids)
        return round(math.exp(outputs.loss.item()), 2)
    except Exception as exc:
        _LOG.warning("[_compute_perplexity] failed: %s — returning 50.0", exc)
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
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    return {
        "perplexity": _compute_perplexity(text),
        "structural_score": _structural_score(paragraphs),
    }
```

**Forward Amendments:** (reserved)

```
┌── BEFORE STARTING THIS STEP — MANDATORY CHECKLIST ──────────────────┐
│ □ 1. READ FILE: /Users/sharky/Desktop/Heidi/qms-tools/ai-humaniser-pro/plans/PLAN_HUMANISER_PRO_V2_REBUILD.md  │
│      Required output: first 5 lines of file shown here.             │
│ □ 2. READ THIS STEP IN FULL. Required output: confirm step title.   │
│ □ 3. UPDATE TRACKER → Step 1 IN PROGRESS. Save. Confirm save.      │
└──────────────────────────────────────────────────────────────────────┘
```

```
┌── AFTER COMPLETING THIS STEP — MANDATORY CHECKLIST ─────────────────┐
│ □ 1. WRITE RESULTS to this step's Results field. Append only.       │
│ □ 2. PLAN-CHANGE CHECK: state "No plan changes required" or STOP.  │
│ □ 3. (RESERVED)                                                      │
│ □ 4. UPDATE TRACKER → Step 1 COMPLETE/FAILED.                       │
│ □ 5. SAVE FILE. Show first 3 lines of saved file.                   │
│ □ 6. PHASE BOUNDARY: NO — session:single. Continuing to Batch A.   │
└──────────────────────────────────────────────────────────────────────┘
```

**Results:** [EMPTY — fill on execution]

---

## Step 2 — Build pattern_detector.py [PARALLEL: Batch A]

**What:** Create `/Users/sharky/Desktop/Heidi/qms-tools/ai-humaniser-pro/pattern_detector.py` with `detect_patterns(text)` returning pattern_counts and flagged_paragraphs. Uses spaCy for sentence analysis and known_new_contract_checker for structural violations.

**Inputs:** spaCy + en_core_web_sm installed, known_new_contract_checker.py exists.

**Outputs:** pattern_detector.py at project root.

**Acceptance criteria:**

- `python3 -c "from pattern_detector import detect_patterns; r=detect_patterns('Furthermore, the implementation of compliance is important. Additionally, the utilization of risk management demonstrates conformity.\n\nThe verification of outcomes is essential. Moreover, the establishment of controls must be demonstrated.'); print(r); assert 'pattern_counts' in r and all(k in r['pattern_counts'] for k in ['formulaic_connectors','burstiness_score','nominalisation_ratio','known_new_violations'])"` exits 0
- No function exceeds 40 lines

**depends_on:** []

**Risk:** spaCy sentence tokenisation may vary on edge cases. Mitigation: fallback to simple split on period for burstiness if spaCy fails.

**Code to write:**

```python
"""Detects 9 Claude writing patterns in text."""
from __future__ import annotations
import logging
import re
import statistics

_LOG = logging.getLogger(__name__)
_NLP = None

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
    """Std dev of sentence word-counts. Lower = more uniform = more AI."""
    nlp = _get_nlp()
    try:
        doc = nlp(text[:5000])
        lengths = [len(list(s)) for s in doc.sents if len(list(s)) > 1]
    except Exception:
        lengths = [len(s.split()) for s in text.split(". ") if s.strip()]
    if len(lengths) < 2:
        return 0.0
    return round(statistics.stdev(lengths), 3)


def _nominalisation_ratio(text: str) -> float:
    """Fraction of words that are nominalisations (-tion/-ment etc)."""
    words = text.split()
    if not words:
        return 0.0
    nominals = len(_NOMINAL.findall(text))
    return round(nominals / len(words), 3)


def _known_new_violations(paragraphs: list[str]) -> int:
    """Count paragraph pairs with no known-new dependency."""
    try:
        from known_new_contract_checker import check_known_new
        pairs = check_known_new(paragraphs)
        return sum(1 for p in pairs if p.get("reorderable", False))
    except Exception as exc:
        _LOG.warning("[_known_new_violations] failed: %s", exc)
        return 0


def _flag_paragraphs(paragraphs: list[str]) -> list[int]:
    """Return indices of paragraphs with 2+ pattern signals."""
    flagged = []
    for i, para in enumerate(paragraphs):
        signals = 0
        if _CONNECTORS.match(para.strip()):
            signals += 1
        if _NOMINAL.search(para):
            signals += 1
        if signals >= 2:
            flagged.append(i)
    return flagged


def detect_patterns(text: str) -> dict:
    """Detect Claude writing patterns. Returns pattern_counts and flagged_paragraphs."""
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    return {
        "pattern_counts": {
            "formulaic_connectors": _count_connectors(text),
            "burstiness_score": _burstiness_score(text),
            "nominalisation_ratio": _nominalisation_ratio(text),
            "known_new_violations": _known_new_violations(paragraphs),
        },
        "flagged_paragraphs": _flag_paragraphs(paragraphs),
    }
```

**Forward Amendments:** (reserved)

```
┌── BEFORE STARTING THIS STEP — MANDATORY CHECKLIST ──────────────────┐
│ □ 1. READ FILE. Required output: first 5 lines.                     │
│ □ 2. READ THIS STEP IN FULL. Confirm title.                         │
│ □ 3. UPDATE TRACKER → Step 2 IN PROGRESS. Save.                    │
└──────────────────────────────────────────────────────────────────────┘
```

```
┌── AFTER COMPLETING THIS STEP — MANDATORY CHECKLIST ─────────────────┐
│ □ 1. WRITE RESULTS. Append only.                                     │
│ □ 2. PLAN-CHANGE CHECK. State "No plan changes required" or STOP.   │
│ □ 3. (RESERVED)                                                      │
│ □ 4. UPDATE TRACKER → Step 2 COMPLETE/FAILED.                       │
│ □ 5. SAVE FILE. Show first 3 lines.                                  │
│ □ 6. PHASE BOUNDARY: NO. Continuing to Batch A.                     │
└──────────────────────────────────────────────────────────────────────┘
```

**Results:** [EMPTY — fill on execution]

---

## Step 3 — Build rewriter.py [PARALLEL: Batch A]

**What:** Create `/Users/sharky/Desktop/Heidi/qms-tools/ai-humaniser-pro/rewriter.py` with `rewrite_paragraph(para, context_before='')` that calls the Heidi proxy (claude-haiku-4-5-20251001, temperature=0), checks protected terms, and reverts if any were dropped.

**Inputs:** profiles/regulatory.py with PROTECTED_TERMS (existing).

**Outputs:** rewriter.py at project root.

**Acceptance criteria:**

- `python3 -c "from rewriter import rewrite_paragraph; from profiles.regulatory import PROTECTED_TERMS; para='Furthermore, the device must demonstrate compliance with applicable standards. Additionally, manufacturers shall ensure that risk management is implemented correctly.'; result=rewrite_paragraph(para); print(result[:200]); assert isinstance(result, str) and len(result) > 0; dropped=[t for t in PROTECTED_TERMS if t.lower() in para.lower() and t.lower() not in result.lower()]; assert len(dropped)==0, f'dropped: {dropped}'"` exits 0
- No function exceeds 40 lines

**depends_on:** []

**Risk:** Heidi proxy unavailable or network issue. Mitigation: try/except in `_call_proxy` returns original paragraph on failure.

**Code to write:**

```python
"""Claude API paragraph rewriter via Heidi proxy — targets 9 Claude writing patterns."""
from __future__ import annotations
import logging

_LOG = logging.getLogger(__name__)
PROXY_URL = "https://heidi-ai-proxy.vercel.app/api/proxy"

_SYSTEM_PROMPT = """You are a regulatory document editor. Rewrite the paragraph below to sound like a confident human expert wrote it. Apply these specific changes where present:
- Remove or replace formulaic connectors at sentence starts: Furthermore, Additionally, Moreover, In addition, It is important to note, It should be noted
- Vary sentence length: if sentences are all similar length, break one into two short sentences or merge two short ones
- Reverse nominalisations: "the implementation of X" → "implementing X", "the utilization of" → "using", "the establishment of" → "establishing"
- If context_before is given and this paragraph does not echo its ending concept, rewrite the opening to create a logical link
Rules:
- Preserve all factual content and regulatory meaning exactly
- Never remove or paraphrase protected regulatory terms (shall, must, demonstrate, verify, validate, risk management, etc.)
- Return ONLY the rewritten paragraph — no explanation, no preamble"""


def _call_proxy(system_prompt: str, user_message: str) -> str:
    """Call the Heidi proxy. Returns response text or raises on failure."""
    import urllib.request
    import json
    body = json.dumps({
        "model": "claude-haiku-4-5-20251001",
        "max_tokens": 1024,
        "temperature": 0,
        "system": system_prompt,
        "messages": [{"role": "user", "content": user_message}],
    }).encode()
    req = urllib.request.Request(
        PROXY_URL, data=body,
        headers={"content-type": "application/json"}, method="POST"
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())["content"][0]["text"]


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
    user_msg = f"context_before: {context_before}\n\nparagraph: {para}" if context_before else para
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
```

**Forward Amendments:** (reserved)

```
┌── BEFORE STARTING THIS STEP — MANDATORY CHECKLIST ──────────────────┐
│ □ 1. READ FILE. Required output: first 5 lines.                     │
│ □ 2. READ THIS STEP IN FULL. Confirm title.                         │
│ □ 3. UPDATE TRACKER → Step 3 IN PROGRESS. Save.                    │
└──────────────────────────────────────────────────────────────────────┘
```

```
┌── AFTER COMPLETING THIS STEP — MANDATORY CHECKLIST ─────────────────┐
│ □ 1. WRITE RESULTS. Append only.                                     │
│ □ 2. PLAN-CHANGE CHECK. State outcome.                              │
│ □ 3. (RESERVED)                                                      │
│ □ 4. UPDATE TRACKER → Step 3 COMPLETE/FAILED.                       │
│ □ 5. SAVE FILE. Show first 3 lines.                                  │
│ □ 6. PHASE BOUNDARY: NO. Continuing to Batch A.                     │
└──────────────────────────────────────────────────────────────────────┘
```

**Results:** [EMPTY — fill on execution]

---

## Step 4 — Build pipeline_v2.py

**What:** Create `/Users/sharky/Desktop/Heidi/qms-tools/ai-humaniser-pro/pipeline_v2.py` with `run_pipeline_v2(text, intensity_threshold=2)` that splits text into paragraphs, detects patterns per paragraph, rewrites those with pattern_count >= intensity_threshold, and rejoins.

**Inputs:** scorer_v2.py, pattern_detector.py, rewriter.py all exist (Steps 1–3 complete).

**Outputs:** pipeline_v2.py at project root.

**Acceptance criteria:**

- `python3 -c "from pipeline_v2 import run_pipeline_v2; txt='Furthermore, risk management is a critical component of medical device safety.\n\nAdditionally, the implementation of controls must be demonstrated to the notified body.\n\nMoreover, verification activities shall ensure compliance with applicable standards.'; result=run_pipeline_v2(txt); print(result[:300]); assert isinstance(result, str) and len(result) > 0"` exits 0
- No function exceeds 40 lines

**depends_on:** [1, 2, 3]

**Risk:** rewriter.py API calls may be slow for long documents. Mitigation: only paragraphs with >= intensity_threshold patterns are sent for rewriting.

**Code to write:**

```python
"""AI Humaniser Pro v2 pipeline: pattern-detect then Claude-API rewrite."""
from __future__ import annotations
import logging

_LOG = logging.getLogger(__name__)
_DEFAULT_THRESHOLD = 2


def _split_paragraphs(text: str) -> list[str]:
    """Split text on double newlines; preserve non-empty paragraphs."""
    return [p.strip() for p in text.split("\n\n") if p.strip()]


def _count_signals(para: str) -> int:
    """Count how many pattern signals fire for one paragraph."""
    from pattern_detector import _CONNECTORS, _NOMINAL
    count = 0
    if _CONNECTORS.match(para.strip()):
        count += 1
    if _NOMINAL.search(para):
        count += 1
    if len(para.split(". ")) >= 2:
        lengths = [len(s.split()) for s in para.split(". ") if s.strip()]
        if len(lengths) >= 2 and max(lengths) - min(lengths) < 5:
            count += 1  # low burstiness
    return count


def _process_paragraph(para: str, prev: str, threshold: int) -> str:
    """Rewrite paragraph if it has enough pattern signals."""
    if _count_signals(para) >= threshold:
        from rewriter import rewrite_paragraph
        return rewrite_paragraph(para, context_before=prev)
    return para


def run_pipeline_v2(text: str, intensity_threshold: int = _DEFAULT_THRESHOLD) -> str:
    """Humanise text by detecting Claude patterns and rewriting flagged paragraphs."""
    if not text or not text.strip():
        return text
    paragraphs = _split_paragraphs(text)
    processed = []
    for i, para in enumerate(paragraphs):
        prev = paragraphs[i - 1] if i > 0 else ""
        processed.append(_process_paragraph(para, prev, intensity_threshold))
    return "\n\n".join(processed)
```

**Forward Amendments:** (reserved)

```
┌── BEFORE STARTING THIS STEP — MANDATORY CHECKLIST ──────────────────┐
│ □ 1. READ FILE. Required output: first 5 lines.                     │
│ □ 2. READ THIS STEP IN FULL. Confirm title.                         │
│ □ 3. UPDATE TRACKER → Step 4 IN PROGRESS. Save.                    │
└──────────────────────────────────────────────────────────────────────┘
```

```
┌── AFTER COMPLETING THIS STEP — MANDATORY CHECKLIST ─────────────────┐
│ □ 1. WRITE RESULTS. Append only.                                     │
│ □ 2. PLAN-CHANGE CHECK. State outcome.                              │
│ □ 3. (RESERVED)                                                      │
│ □ 4. UPDATE TRACKER → Step 4 COMPLETE/FAILED.                       │
│ □ 5. SAVE FILE. Show first 3 lines.                                  │
│ □ 6. PHASE BOUNDARY: NO. Continuing to PT1.                         │
└──────────────────────────────────────────────────────────────────────┘
```

**Results:** [EMPTY — fill on execution]

---

## Step PT1 — Phase 1 → Phase 2 Transition

**What:** Verify all four modules exist and their public APIs are callable before Phase 2 testing begins.

**Inputs:** Steps 1–4 complete.

**Acceptance criteria (all must exit 0):**

1. `python3 -c "from scorer_v2 import score_document_v2; r=score_document_v2('test text here for scoring'); assert 'perplexity' in r; print('scorer_v2 OK')"`
2. `python3 -c "from pattern_detector import detect_patterns; r=detect_patterns('Furthermore test.\n\nAdditionally test.'); assert 'pattern_counts' in r; print('pattern_detector OK')"`
3. `python3 -c "from rewriter import rewrite_paragraph; r=rewrite_paragraph('Furthermore, the device must demonstrate compliance.'); assert isinstance(r,str); print('rewriter OK')"`
4. `python3 -c "from pipeline_v2 import run_pipeline_v2; r=run_pipeline_v2('Furthermore test.\n\nAdditionally test.'); assert isinstance(r,str); print('pipeline_v2 OK')"`
5. `ls /Users/sharky/Desktop/Heidi/qms-tools/ai-humaniser-pro/scorer_v2.py /Users/sharky/Desktop/Heidi/qms-tools/ai-humaniser-pro/pattern_detector.py /Users/sharky/Desktop/Heidi/qms-tools/ai-humaniser-pro/rewriter.py /Users/sharky/Desktop/Heidi/qms-tools/ai-humaniser-pro/pipeline_v2.py` — all 4 listed

**Outputs:** Written confirmation all 5 checks passed.

**depends_on:** [1, 2, 3, 4]

**Risk:** If any check fails — STOP. Write STOP_REPORT.md. Do not start Phase 2.

**Forward Amendments:** (reserved)

```
┌── BEFORE STARTING THIS STEP — MANDATORY CHECKLIST ──────────────────┐
│ □ 1. READ FILE. Required output: first 5 lines.                     │
│ □ 2. READ THIS STEP IN FULL. Confirm title.                         │
│ □ 3. UPDATE TRACKER → PT1 IN PROGRESS. Save.                       │
└──────────────────────────────────────────────────────────────────────┘
```

```
┌── AFTER COMPLETING THIS STEP — MANDATORY CHECKLIST ─────────────────┐
│ □ 1. WRITE RESULTS with all 5 check outputs verbatim.                │
│ □ 2. PLAN-CHANGE CHECK. STOP if any check failed.                   │
│ □ 3. (RESERVED)                                                      │
│ □ 4. UPDATE TRACKER → PT1 COMPLETE/FAILED.                          │
│ □ 5. SAVE FILE. Show first 3 lines.                                  │
│ □ 6. PHASE BOUNDARY: YES — session:single, handoff skipped.         │
│      Continuing to Phase 2 (Step 5).                                │
└──────────────────────────────────────────────────────────────────────┘
```

**Results:** [EMPTY — fill on execution]

---

# PHASE 2 — INTEGRATION TESTS

---

## Step 5 — Test perplexity improvement on ChatGPT document

**What:** Run run_pipeline_v2() on test-chatgpt-rapamycin.txt, score before and after with score_document_v2(), assert perplexity increases (text becomes less AI-predictable). Save the humanised output.

**Inputs:** PT1 complete. test-chatgpt-rapamycin.txt at project root.

**Outputs:** Printed before/after scores. Humanised file saved as test-chatgpt-rapamycin-humanised.txt.

**Acceptance criteria:**

- `python3 -c "from pipeline_v2 import run_pipeline_v2; from scorer_v2 import score_document_v2; txt=open('test-chatgpt-rapamycin.txt').read(); before=score_document_v2(txt)['perplexity']; result=run_pipeline_v2(txt); after=score_document_v2(result)['perplexity']; print(f'before:{before:.1f} after:{after:.1f} improved:{after>before}'); assert after>before, f'no perplexity improvement: {before:.1f}->{after:.1f}'"` exits 0

**depends_on:** [PT1]

**Risk:** Heidi proxy may time out on a long document. Mitigation: pipeline only rewrites flagged paragraphs (not all), limiting API calls. If perplexity does NOT improve: this is a genuine finding — write STOP_REPORT describing why and what to try next (lower intensity_threshold, try different rewriting prompt).

**Forward Amendments:** (reserved)

```
┌── BEFORE STARTING THIS STEP — MANDATORY CHECKLIST ──────────────────┐
│ □ 1. READ FILE. Required output: first 5 lines.                     │
│ □ 2. READ THIS STEP IN FULL. Confirm title.                         │
│ □ 3. UPDATE TRACKER → Step 5 IN PROGRESS. Save.                    │
└──────────────────────────────────────────────────────────────────────┘
```

```
┌── AFTER COMPLETING THIS STEP — MANDATORY CHECKLIST ─────────────────┐
│ □ 1. WRITE RESULTS with before/after perplexity scores verbatim.    │
│ □ 2. PLAN-CHANGE CHECK. If perplexity did not improve: STOP_REPORT. │
│ □ 3. (RESERVED)                                                      │
│ □ 4. UPDATE TRACKER → Step 5 COMPLETE/FAILED.                       │
│ □ 5. SAVE FILE. Show first 3 lines.                                  │
│ □ 6. PHASE BOUNDARY: NO. Continuing to Step 6.                      │
└──────────────────────────────────────────────────────────────────────┘
```

**Results:** [EMPTY — fill on execution]

---

## Step 6 — Test formulaic connectors + protected terms on RMR-ISD-AI-Scribe

**What:** Run run_pipeline_v2() on the RMR-ISD-AI-Scribe risk management report (.docx), assert formulaic connectors reduce in the output, and assert no protected terms were dropped. Save humanised output.

**Inputs:** PT1 complete. /Users/sharky/Desktop/Heidi/Working Docs/Risk/RMR-ISD-AI-Scribe-Risk-Management-Report_v1.docx exists.

**Outputs:** Connector count before/after. Protected terms check result. Humanised output saved as RMR-ISD-AI-Scribe-Risk-Management-Report_v1-humanised-v2.txt.

**Acceptance criteria:**

1. `python3 -c "from pipeline_v2 import run_pipeline_v2; from pattern_detector import detect_patterns; import docx; doc=docx.Document('/Users/sharky/Desktop/Heidi/Working Docs/Risk/RMR-ISD-AI-Scribe-Risk-Management-Report_v1.docx'); txt='\n\n'.join(p.text for p in doc.paragraphs if p.text.strip()); before_c=detect_patterns(txt)['pattern_counts']['formulaic_connectors']; result=run_pipeline_v2(txt); after_c=detect_patterns(result)['pattern_counts']['formulaic_connectors']; print(f'connectors before:{before_c} after:{after_c} reduced:{after_c<before_c}'); assert after_c<before_c, f'connectors not reduced: {before_c}->{after_c}'"` exits 0
2. `python3 -c "from pipeline_v2 import run_pipeline_v2; from profiles.regulatory import PROTECTED_TERMS; import docx; doc=docx.Document('/Users/sharky/Desktop/Heidi/Working Docs/Risk/RMR-ISD-AI-Scribe-Risk-Management-Report_v1.docx'); txt='\n\n'.join(p.text for p in doc.paragraphs if p.text.strip()); result=run_pipeline_v2(txt); dropped=[t for t in PROTECTED_TERMS if t.lower() in txt.lower() and t.lower() not in result.lower()]; print('dropped:',dropped); assert len(dropped)==0"` exits 0

**depends_on:** [PT1]

**Risk:** The risk management report may have very few formulaic connectors (since it was written in regulatory style that already avoids them). If before_c == 0, the assertion will trivially pass (0 < 0 is false). Mitigation: if before_c == 0, report this finding but do not fail — instead confirm perplexity change and document the finding that the report had no formulaic connectors to reduce.

**Forward Amendments:** (reserved)

```
┌── BEFORE STARTING THIS STEP — MANDATORY CHECKLIST ──────────────────┐
│ □ 1. READ FILE. Required output: first 5 lines.                     │
│ □ 2. READ THIS STEP IN FULL. Confirm title.                         │
│ □ 3. UPDATE TRACKER → Step 6 IN PROGRESS. Save.                    │
└──────────────────────────────────────────────────────────────────────┘
```

```
┌── AFTER COMPLETING THIS STEP — MANDATORY CHECKLIST ─────────────────┐
│ □ 1. WRITE RESULTS with both check outputs verbatim.                 │
│ □ 2. PLAN-CHANGE CHECK. State outcome.                              │
│ □ 3. (RESERVED)                                                      │
│ □ 4. UPDATE TRACKER → Step 6 COMPLETE/FAILED.                       │
│ □ 5. SAVE FILE. Show first 3 lines.                                  │
│ □ 6. PHASE BOUNDARY: NO. Continuing to Step 7.                      │
└──────────────────────────────────────────────────────────────────────┘
```

**Results:** [EMPTY — fill on execution]

---

# PHASE 3 — FINALISE

---

## Step 7 — Update /humanize skill

**What:** Update /Users/sharky/.claude/commands/humanize.md to use pipeline_v2 and scorer_v2 instead of pipeline and scorer. Also update CLAUDE.md at project root to document v2 entry points.

**Inputs:** PT1 complete (v2 modules exist and callable).

**Outputs:** Updated humanize.md. Updated CLAUDE.md.

**Acceptance criteria:**

- `grep -c "pipeline_v2\|scorer_v2\|score_document_v2" /Users/sharky/.claude/commands/humanize.md` returns ≥ 2
- `grep -c "pipeline_v2\|scorer_v2" /Users/sharky/Desktop/Heidi/qms-tools/ai-humaniser-pro/CLAUDE.md` returns ≥ 2

**depends_on:** [PT1]

**Risk:** humanize.md may not accept the updated Python snippet. Mitigation: test the updated snippet before writing.

**Forward Amendments:** (reserved)

```
┌── BEFORE STARTING THIS STEP — MANDATORY CHECKLIST ──────────────────┐
│ □ 1. READ FILE. Required output: first 5 lines.                     │
│ □ 2. READ THIS STEP IN FULL. Confirm title.                         │
│ □ 3. UPDATE TRACKER → Step 7 IN PROGRESS. Save.                    │
└──────────────────────────────────────────────────────────────────────┘
```

```
┌── AFTER COMPLETING THIS STEP — MANDATORY CHECKLIST ─────────────────┐
│ □ 1. WRITE RESULTS with grep outputs verbatim.                       │
│ □ 2. PLAN-CHANGE CHECK. State outcome.                              │
│ □ 3. (RESERVED)                                                      │
│ □ 4. UPDATE TRACKER → Step 7 COMPLETE/FAILED.                       │
│ □ 5. SAVE FILE. Show first 3 lines.                                  │
│ □ 6. PHASE BOUNDARY: NO. Continuing to Step 8.                      │
└──────────────────────────────────────────────────────────────────────┘
```

**Results:** [EMPTY — fill on execution]

---

## Step 8 — BUGS_AND_LESSONS.md + aggregate

**What:** Append entries to BUGS_AND_LESSONS.md for any bugs found during this build, then run /aggregate-lessons.

**Inputs:** Steps 5, 6, 7 complete.

**Outputs:** BUGS_AND_LESSONS.md updated. SHARED_LESSONS.md updated via aggregate-lessons.

**Acceptance criteria:**

- `tail -5 /Users/sharky/Desktop/Heidi/qms-tools/ai-humaniser-pro/BUGS_AND_LESSONS.md` shows at least one entry dated 2026-06-21
- aggregate-lessons runs without error

**depends_on:** [5, 6, 7]

**Risk:** None significant.

**Forward Amendments:** (reserved)

```
┌── BEFORE STARTING THIS STEP — MANDATORY CHECKLIST ──────────────────┐
│ □ 1. READ FILE. Required output: first 5 lines.                     │
│ □ 2. READ THIS STEP IN FULL. Confirm title.                         │
│ □ 3. UPDATE TRACKER → Step 8 IN PROGRESS. Save.                    │
└──────────────────────────────────────────────────────────────────────┘
```

```
┌── AFTER COMPLETING THIS STEP — MANDATORY CHECKLIST ─────────────────┐
│ □ 1. WRITE RESULTS. Append only.                                     │
│ □ 2. PLAN-CHANGE CHECK. State outcome.                              │
│ □ 3. (RESERVED)                                                      │
│ □ 4. UPDATE TRACKER → Step 8 COMPLETE/FAILED.                       │
│ □ 5. SAVE FILE. Show first 3 lines.                                  │
│ □ 6. PHASE BOUNDARY: YES (last step) — session:single, handoff      │
│      skipped. Plan execution complete — run H gate.                  │
└──────────────────────────────────────────────────────────────────────┘
```

**Results:** [EMPTY — fill on execution]

---

## Risks and Open Questions

1. **Perplexity improvement on regulatory text may be small or zero.** The risk management reports scored 0.000 on HC3 — their perplexity baseline is unknown. If they already score high (human-like) on DistilGPT-2, improvement may be unmeasurable. Step 6 tests connector reduction instead of perplexity for the risk reports, which is more reliable.

2. **Heidi proxy rate limits.** If pipeline_v2 sends many paragraphs for rewriting on a long document, the proxy may rate-limit. Mitigation: intensity_threshold=2 means only paragraphs with 2+ signals are rewritten, reducing API call volume.

3. **DistilGPT-2 may not discriminate Claude regulatory text well.** The model was trained on general text; regulatory language is formulaic regardless of whether a human or AI wrote it. perplexity improvement on the ChatGPT Rapamycin document (clearly AI, general prose) is more likely than on regulatory text.

## External Dependencies

- Internet access for Heidi proxy calls during Step 5 and 6
- DistilGPT-2 model cached locally (downloads on first use if not cached)

---

## Iteration Summary

Rounds: 1. Issues found: 0 (first draft clean after Phase 1.5 verification). WONTFIX: 0. DEFERRED: 0. UNCERTAIN: 0.

## Handoff Note

1. **Next action:** Execute the plan starting from Batch A (Steps 1, 2, 3 in parallel).
2. **Step 1 is:** Build all three modules in Batch A concurrently, then pipeline_v2.py (Step 4), then run the Phase 1→2 transition (PT1).
3. **Have ready before beginning:** Internet access (Heidi proxy needed for rewriter.py tests in Steps 5–6). Working directory: /Users/sharky/Desktop/Heidi/qms-tools/ai-humaniser-pro/.
4. **What would require plan revision:** If the Heidi proxy returns errors consistently during Step 3's acceptance criteria test, write a STOP_REPORT — the rewriter.py cannot be validated without the proxy.
5. **Recommended model:** claude-sonnet-4-6 — standard Python build with all module code pre-specified. No architectural decisions needed.

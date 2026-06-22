═══════════════════════════════════════════════════════════════════
EXECUTION PROTOCOL — READ THIS BEFORE DOING ANYTHING ELSE
═══════════════════════════════════════════════════════════════════

This plan is stored at: /Users/sharky/Desktop/Heidi/qms-tools/ai-humaniser-pro/plans/PLAN_KNOWN_NEW_FIXER_BUILD.md
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

OBJECTIVES FILE: /Users/sharky/Desktop/Heidi/qms-tools/ai-humaniser-pro/OBJECTIVES_known-new-fixer_21-06-2026.md

═══════════════════════════════════════════════════════════════════
PLAN STATE TRACKER
═══════════════════════════════════════════════════════════════════

Last updated after: Step 5 COMPLETE
Current step: COMPLETE

┌─────┬──────────────────────────────────────────────────┬─────────────┐
│ # │ Step Name │ Status │
├─────┼──────────────────────────────────────────────────┼─────────────┤
│ │ ── PHASE 1: BUILD ── │ │
│ [A] │ ── PARALLEL BATCH A: Steps 1 + 2 ── │ COMPLETE │
│ 1 │ Build known_new_fixer.py [PARALLEL: A] │ COMPLETE │
│ 2 │ Update pipeline_v2.py [PARALLEL: A] │ COMPLETE │
│ PT1 │ Phase 1→2 Transition │ COMPLETE │
│ │ ── PHASE 2: TEST + QUALITY ── │ │
│ 3 │ Test fix_known_new acceptance criteria │ COMPLETE │
│ 4 │ Run end-to-end structural improvement test │ COMPLETE │
│ 5 │ Run /code-quality chain │ COMPLETE │
└─────┴──────────────────────────────────────────────────┴─────────────┘

Status values: PENDING / IN PROGRESS / COMPLETE / FAILED / SKIPPED
═══════════════════════════════════════════════════════════════════

## What this plan is

Builds the known-new contract fixer — a new module (`known_new_fixer.py`) that calls the Claude API (Haiku, via the Heidi proxy) to rewrite paragraph N+1 openings to echo paragraph N's ending concept. Wires it into `pipeline_v2.py` as a second humanisation pass. Verifies structural improvement and runs the full code-quality chain at the end. Extends PLAN_HUMANISER_PRO_V2_REBUILD.md (v2 build is the foundation).

## Objective

Build and integrate a known-new contract fixer so `run_pipeline_v2()` produces documents with measurably fewer additive (reorderable) paragraph pairs.

## Scope

IN:

- known_new_fixer.py with fix_known_new(paragraphs) and \_apply_known_new_fix() helper
- pipeline_v2.py updated to call \_apply_known_new_fix() as a second pass
- Integration test on test-chatgpt-rapamycin.txt (structural_score must decrease)
- /code-quality → /deep-qa → /code-review chain as final step

OUT OF SCOPE:

- Modifying known_new_contract_checker.py (reuse as-is)
- React/browser UI
- Any other module changes

## Constraints

- Heidi proxy (https://heidi-ai-proxy.vercel.app/api/proxy) for all Claude API calls
- temperature=0 on every Claude API call
- PROTECTED_TERMS never dropped — revert-on-drop in fix_known_new
- NASA Rule: all functions ≤40 lines
- No hardcoded absolute paths
- session: single
- Recommended model: claude-sonnet-4-6

## Dependency summary

Step 1: depends_on [] [PARALLEL: Batch A]
Step 2: depends_on [] [PARALLEL: Batch A]
PT1: depends_on [1, 2]
Step 3: depends_on [PT1]
Step 4: depends_on [PT1]
Step 5: depends_on [3, 4]

Critical path: Step 1 → PT1 → Step 4 → Step 5
Parallel: Batch A (Steps 1+2 concurrent)

---

# PHASE 1 — BUILD

---

## Step 1 — Build known_new_fixer.py [PARALLEL: Batch A]

**What:** Create `/Users/sharky/Desktop/Heidi/qms-tools/ai-humaniser-pro/known_new_fixer.py` with these functions: `_call_proxy(para_n, para_n1)`, `_terms_dropped(original, rewritten)`, `_fix_pair(para_n, para_n1)`, `fix_known_new(paragraphs)`. Uses Heidi proxy, temperature=0, claude-haiku-4-5-20251001. Reverts if any protected term is dropped.

**Inputs:** profiles/regulatory.py (PROTECTED_TERMS), known_new_contract_checker.py (check_known_new), Heidi proxy accessible.

**Outputs:** known_new_fixer.py at project root. All functions ≤40 lines.

**Acceptance criteria:**

- `python3 -c "from known_new_fixer import fix_known_new; r=fix_known_new(['The risk assessment identified three hazards.','Furthermore compliance must be demonstrated.']); print(r); assert isinstance(r,list) and len(r)==2"` exits 0
- No function exceeds 40 lines (per-file NASA check)

**depends_on:** []

**Risk:** LLM may return empty string or identical text — both are handled (empty → revert, identical → return as-is, both pass the protected-terms check).

**Code to write:**

```python
"""Known-new contract fixer: rewrites paragraph N+1 openings to chain from paragraph N."""
from __future__ import annotations
import logging

_LOG = logging.getLogger(__name__)
_PROXY_URL = "https://heidi-ai-proxy.vercel.app/api/proxy"
_MAX_TOKENS = 300
_PROXY_TIMEOUT_SEC = 30

_SYSTEM_PROMPT = (
    "You are a regulatory document editor fixing paragraph flow. "
    "You will receive two paragraphs. Rewrite ONLY the opening sentence of "
    "the second paragraph so it connects to the ending concept of the first paragraph. "
    "Use connective language: 'This [concept]', 'Such [concept]', 'Building on [concept]', "
    "'In light of [concept]', 'That [concept]'. "
    "Leave the rest of the second paragraph unchanged. "
    "Never remove protected regulatory terms (shall, must, demonstrate, verify, validate, "
    "risk management, compliance, safety, hazard). "
    "Return ONLY the complete rewritten second paragraph — no explanation, no preamble."
)


def _call_proxy(para_n: str, para_n1: str) -> str:
    """Call Heidi proxy to rewrite para_n1 opening to connect to para_n."""
    import urllib.request
    import json
    user_msg = f"PARAGRAPH 1:\n{para_n}\n\nPARAGRAPH 2 (rewrite its opening only):\n{para_n1}"
    body = json.dumps({
        "model": "claude-haiku-4-5-20251001",
        "max_tokens": _MAX_TOKENS,
        "temperature": 0,
        "system": [{"type": "text", "text": _SYSTEM_PROMPT, "cache_control": {"type": "ephemeral"}}],
        "messages": [{"role": "user", "content": user_msg}],
    }).encode()
    req = urllib.request.Request(
        _PROXY_URL, data=body,
        headers={"content-type": "application/json"}, method="POST"
    )
    with urllib.request.urlopen(req, timeout=_PROXY_TIMEOUT_SEC) as resp:
        return json.loads(resp.read())["content"][0]["text"]


def _terms_dropped(original: str, rewritten: str) -> list[str]:
    """Return protected terms present in original but absent from rewritten."""
    from profiles.regulatory import PROTECTED_TERMS
    return [
        t for t in PROTECTED_TERMS
        if t.lower() in original.lower() and t.lower() not in rewritten.lower()
    ]


def _fix_pair(para_n: str, para_n1: str) -> str:
    """Rewrite para_n1 to open with a reference to para_n's ending concept."""
    try:
        result = _call_proxy(para_n, para_n1).strip()
    except Exception as exc:
        _LOG.warning("[_fix_pair] proxy failed: %s — reverting", exc)
        return para_n1
    if not result:
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
    result = list(paragraphs)
    for pair in pairs:
        if not pair.get("reorderable", False):
            continue
        i = pair["pair_index"]
        if i + 1 >= len(result):
            continue
        _LOG.info("[fix_known_new] fixing pair %d: '%s' → '%s'",
                  i, pair["p_n_ending_concept"], pair["p_n1_opening_concept"])
        result[i + 1] = _fix_pair(result[i], result[i + 1])
    return result
```

**Forward Amendments:** (reserved)

```
┌── BEFORE STARTING THIS STEP ─────────────────────────────────────────┐
│ □ 1. READ FILE. Required output: first 5 lines shown.               │
│ □ 2. READ THIS STEP IN FULL. Confirm step title.                    │
│ □ 3. UPDATE TRACKER → Step 1 IN PROGRESS. Save.                    │
└──────────────────────────────────────────────────────────────────────┘
```

```
┌── AFTER COMPLETING THIS STEP ────────────────────────────────────────┐
│ □ 1. WRITE RESULTS. Append only.                                     │
│ □ 2. PLAN-CHANGE CHECK. State outcome.                              │
│ □ 3. (RESERVED)                                                      │
│ □ 4. UPDATE TRACKER → Step 1 COMPLETE/FAILED.                       │
│ □ 5. SAVE FILE. Show first 3 lines.                                  │
│ □ 6. PHASE BOUNDARY: NO. Continuing to Batch A.                     │
└──────────────────────────────────────────────────────────────────────┘
```

**Results:** [EMPTY — fill on execution]

---

## Step 2 — Update pipeline_v2.py [PARALLEL: Batch A]

**What:** Add `_apply_known_new_fix(paragraphs)` helper to pipeline_v2.py and call it from `run_pipeline_v2()` after the existing pattern-detect → rewrite pass. Happy-path log line: `[_apply_known_new_fix] known-new fix applied to N paragraphs`. Skip-path log line: `[_apply_known_new_fix] known_new_fixer unavailable — skipping`.

**Inputs:** pipeline_v2.py exists. known_new_fixer.py will exist after Step 1 (imported lazily — no build-time dependency).

**Outputs:** pipeline_v2.py updated with \_apply_known_new_fix() and the call in run_pipeline_v2(). All functions still ≤40 lines.

**Acceptance criteria:**

- `grep -n "_apply_known_new_fix\|known_new_fixer" /Users/sharky/Desktop/Heidi/qms-tools/ai-humaniser-pro/pipeline_v2.py` returns ≥ 2 matches
- Per-file NASA check returns no violations

**depends_on:** []

**Risk:** run_pipeline_v2 could exceed 40 lines if \_apply_known_new_fix is inlined. Mitigation: extract as separate helper.

**Wiring chain:**

- fix_known_new() is called by \_apply_known_new_fix() in pipeline_v2.py
- \_apply_known_new_fix() is called by run_pipeline_v2() in pipeline_v2.py
- run_pipeline_v2() is the public CLI entry point (called by /humanize skill and direct user invocation)
- CLI threads dep — wiring is reachable in production ✓

**Happy-path log line:** `[_apply_known_new_fix] known-new fix applied to N paragraphs`
**Skip-path log line:** `[_apply_known_new_fix] known_new_fixer unavailable — skipping`

**Code change — add to pipeline_v2.py after \_process_paragraph:**

```python
def _apply_known_new_fix(paragraphs: list[str]) -> list[str]:
    """Apply known-new contract fix as a second humanisation pass."""
    try:
        from known_new_fixer import fix_known_new
        result = fix_known_new(paragraphs)
        _LOG.info("[_apply_known_new_fix] known-new fix applied to %d paragraphs", len(result))
        return result
    except ImportError:
        _LOG.warning("[_apply_known_new_fix] known_new_fixer unavailable — skipping")
        return paragraphs
    except Exception as exc:
        _LOG.warning("[_apply_known_new_fix] failed: %s — returning unmodified", exc)
        return paragraphs
```

**And update run_pipeline_v2 to call it:**

```python
def run_pipeline_v2(text: str, intensity_threshold: int = _DEFAULT_THRESHOLD) -> str:
    """Humanise text: pattern-detect → rewrite flagged paragraphs → fix known-new chain."""
    if not text or not text.strip():
        return text
    paragraphs = _split_paragraphs(text)
    processed = []
    for i, para in enumerate(paragraphs):
        prev = paragraphs[i - 1] if i > 0 else ""
        processed.append(_process_paragraph(para, prev, intensity_threshold))
    processed = _apply_known_new_fix(processed)
    return "\n\n".join(processed)
```

**Forward Amendments:** (reserved)

```
┌── BEFORE STARTING THIS STEP ─────────────────────────────────────────┐
│ □ 1. READ FILE. Required output: first 5 lines shown.               │
│ □ 2. READ THIS STEP IN FULL. Confirm step title.                    │
│ □ 3. UPDATE TRACKER → Step 2 IN PROGRESS. Save.                    │
└──────────────────────────────────────────────────────────────────────┘
```

```
┌── AFTER COMPLETING THIS STEP ────────────────────────────────────────┐
│ □ 1. WRITE RESULTS. Append only.                                     │
│ □ 2. PLAN-CHANGE CHECK. State outcome.                              │
│ □ 3. (RESERVED)                                                      │
│ □ 4. UPDATE TRACKER → Step 2 COMPLETE/FAILED.                       │
│ □ 5. SAVE FILE. Show first 3 lines.                                  │
│ □ 6. PHASE BOUNDARY: NO. Continuing to PT1.                         │
└──────────────────────────────────────────────────────────────────────┘
```

**Results:** [EMPTY — fill on execution]

---

## Step PT1 — Phase 1 → Phase 2 Transition

**What:** Verify known_new_fixer.py and updated pipeline_v2.py both exist and are importable before Phase 2 tests begin.

**Acceptance criteria (all must exit 0):**

1. `python3 -c "from known_new_fixer import fix_known_new, _fix_pair, _call_proxy, _terms_dropped; print('known_new_fixer OK')"`
2. `grep -n "_apply_known_new_fix" /Users/sharky/Desktop/Heidi/qms-tools/ai-humaniser-pro/pipeline_v2.py && echo "wiring OK"`
3. `python3 -m py_compile known_new_fixer.py pipeline_v2.py && echo "compile OK"`

**depends_on:** [1, 2]

**Risk:** If any check fails — STOP. Write STOP_REPORT.md.

```
┌── BEFORE STARTING THIS STEP ─────────────────────────────────────────┐
│ □ 1. READ FILE. Required output: first 5 lines shown.               │
│ □ 2. READ THIS STEP IN FULL. Confirm step title.                    │
│ □ 3. UPDATE TRACKER → PT1 IN PROGRESS. Save.                       │
└──────────────────────────────────────────────────────────────────────┘
```

```
┌── AFTER COMPLETING THIS STEP ────────────────────────────────────────┐
│ □ 1. WRITE RESULTS with all 3 check outputs verbatim.                │
│ □ 2. PLAN-CHANGE CHECK. STOP if any check failed.                   │
│ □ 3. (RESERVED)                                                      │
│ □ 4. UPDATE TRACKER → PT1 COMPLETE/FAILED.                          │
│ □ 5. SAVE FILE. Show first 3 lines.                                  │
│ □ 6. PHASE BOUNDARY: YES — session:single, handoff skipped.         │
│      Continuing to Phase 2.                                         │
└──────────────────────────────────────────────────────────────────────┘
```

**Results:** [EMPTY — fill on execution]

---

# PHASE 2 — TEST + QUALITY

---

## Step 3 — Test fix_known_new acceptance criteria

**What:** Run the three objective VERIFY commands for bullets 1, 3, and 4 (module callable, protected terms safe, NASA rule).

**Acceptance criteria:**

1. `python3 -c "from known_new_fixer import fix_known_new; r=fix_known_new(['The risk assessment identified three hazards.','Furthermore compliance must be demonstrated.']); print(r); assert isinstance(r,list) and len(r)==2 and isinstance(r[0],str) and isinstance(r[1],str)"`
2. `python3 -c "from known_new_fixer import fix_known_new; from profiles.regulatory import PROTECTED_TERMS; paras=['Risk management shall demonstrate compliance. Verification is required.','Additionally the implementation of safety measures must be validated.']; result=fix_known_new(paras); dropped=[t for t in PROTECTED_TERMS if t.lower() in ' '.join(paras).lower() and t.lower() not in ' '.join(result).lower()]; print('dropped:',dropped); assert len(dropped)==0"`
3. `for f in known_new_fixer.py pipeline_v2.py; do awk '/^def /{if(s)print c,FILENAME,s; s=$0; c=0} {c++} END{if(s)print c,FILENAME,s}' $f | awk '$1>40{print "VIOLATION:",$0}'; done && echo "NASA PASS"`

**depends_on:** [PT1]

```
┌── BEFORE STARTING THIS STEP ─────────────────────────────────────────┐
│ □ 1. READ FILE. Required output: first 5 lines shown.               │
│ □ 2. READ THIS STEP IN FULL. Confirm step title.                    │
│ □ 3. UPDATE TRACKER → Step 3 IN PROGRESS. Save.                    │
└──────────────────────────────────────────────────────────────────────┘
```

```
┌── AFTER COMPLETING THIS STEP ────────────────────────────────────────┐
│ □ 1. WRITE RESULTS with all 3 check outputs verbatim.                │
│ □ 2. PLAN-CHANGE CHECK. State outcome.                              │
│ □ 3. (RESERVED)                                                      │
│ □ 4. UPDATE TRACKER → Step 3 COMPLETE/FAILED.                       │
│ □ 5. SAVE FILE. Show first 3 lines.                                  │
│ □ 6. PHASE BOUNDARY: NO. Continuing to Step 4.                      │
└──────────────────────────────────────────────────────────────────────┘
```

**Results:** [EMPTY — fill on execution]

---

## Step 4 — Run end-to-end structural improvement test

**What:** Run run_pipeline_v2() on test-chatgpt-rapamycin.txt and assert structural_score decreases. Save humanised output.

**Acceptance criteria:**

- `python3 -c "from pipeline_v2 import run_pipeline_v2; from scorer_v2 import score_document_v2; txt=open('test-chatgpt-rapamycin.txt').read(); before=score_document_v2(txt)['structural_score']; result=run_pipeline_v2(txt); after=score_document_v2(result)['structural_score']; print(f'structural before:{before:.3f} after:{after:.3f} improved:{after<before}'); assert after<before"` exits 0

**depends_on:** [PT1]

**Risk:** If the LLM reverts all pairs (protected terms dropped), structural_score may not decrease. Mitigation: test-chatgpt-rapamycin.txt has very few protected terms, so reverts are unlikely. If the test still fails after the known-new fix: write STOP_REPORT — the fix may need a different approach for heavily-protected text.

```
┌── BEFORE STARTING THIS STEP ─────────────────────────────────────────┐
│ □ 1. READ FILE. Required output: first 5 lines shown.               │
│ □ 2. READ THIS STEP IN FULL. Confirm step title.                    │
│ □ 3. UPDATE TRACKER → Step 4 IN PROGRESS. Save.                    │
└──────────────────────────────────────────────────────────────────────┘
```

```
┌── AFTER COMPLETING THIS STEP ────────────────────────────────────────┐
│ □ 1. WRITE RESULTS with before/after scores verbatim.               │
│ □ 2. PLAN-CHANGE CHECK. If structural did not improve: STOP_REPORT. │
│ □ 3. (RESERVED)                                                      │
│ □ 4. UPDATE TRACKER → Step 4 COMPLETE/FAILED.                       │
│ □ 5. SAVE FILE. Show first 3 lines.                                  │
│ □ 6. PHASE BOUNDARY: NO. Continuing to Step 5.                      │
└──────────────────────────────────────────────────────────────────────┘
```

**Results:** [EMPTY — fill on execution]

---

## Step 5 — Run /code-quality chain

**What:** Run /code-quality on known_new_fixer.py and pipeline_v2.py, which chains to /deep-qa and then /code-review. Apply all safe root-cause fixes found. Update BUGS_AND_LESSONS.md. Run aggregate-lessons.

**Acceptance criteria:**

- /code-quality runs and reports findings
- /deep-qa runs on the files
- /code-review runs on the files
- `tail -3 /Users/sharky/Desktop/Heidi/qms-tools/ai-humaniser-pro/BUGS_AND_LESSONS.md` shows at least one entry from this session

**depends_on:** [3, 4]

```
┌── BEFORE STARTING THIS STEP ─────────────────────────────────────────┐
│ □ 1. READ FILE. Required output: first 5 lines shown.               │
│ □ 2. READ THIS STEP IN FULL. Confirm step title.                    │
│ □ 3. UPDATE TRACKER → Step 5 IN PROGRESS. Save.                    │
└──────────────────────────────────────────────────────────────────────┘
```

```
┌── AFTER COMPLETING THIS STEP ────────────────────────────────────────┐
│ □ 1. WRITE RESULTS. Append only.                                     │
│ □ 2. PLAN-CHANGE CHECK. State outcome.                              │
│ □ 3. (RESERVED)                                                      │
│ □ 4. UPDATE TRACKER → Step 5 COMPLETE/FAILED.                       │
│ □ 5. SAVE FILE. Show first 3 lines.                                  │
│ □ 6. PHASE BOUNDARY: YES (last step) — session:single, handoff      │
│      skipped. Plan execution complete — run H gate.                  │
└──────────────────────────────────────────────────────────────────────┘
```

**Results:** [EMPTY — fill on execution]

---

## Risks and Open Questions

1. **Structural improvement may be small:** The ChatGPT test document has 0.857 structural_score. If the LLM produces connections the spaCy lemma-matching doesn't recognise as shared root tokens, `check_known_new` may still mark pairs as reorderable even after rewriting. Mitigation: even a 0.1 reduction (e.g. 0.857→0.750) counts.

2. **Heidi proxy rate limiting:** fix_known_new sends one API call per reorderable pair. For a document with 50+ reorderable pairs, this could hit rate limits. Mitigation: the ChatGPT test doc has ~7 paragraphs and ~6 pairs.

3. **Protected term sensitivity:** For the test in Step 3, the paragraphs are chosen to have protected terms that survive rewriting. If the LLM can't rewrite without dropping them, the revert fires correctly.

## Handoff Note

1. Next action: Execute Batch A (Steps 1 + 2 in parallel), then PT1, then Steps 3-5 in sequence.
2. Step 1 is: Write known_new_fixer.py with the code in the step.
3. Have ready: Heidi proxy accessible (required for Step 3's API call).
4. What requires plan revision: If structural_score doesn't decrease in Step 4, write STOP_REPORT — the fix may need a lower threshold or a different approach to the rewrite prompt.
5. Recommended model: claude-sonnet-4-6 — standard Python build, approach fully specified.

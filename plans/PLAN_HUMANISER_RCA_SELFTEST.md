═══════════════════════════════════════════════════════════════════
EXECUTION PROTOCOL
═══════════════════════════════════════════════════════════════════
This plan: /Users/sharky/Desktop/Heidi/qms-tools/ai-humaniser-pro/plans/PLAN_HUMANISER_RCA_SELFTEST.md
Source of truth. Memory is not. Plan survives auto-compaction.
After every step: write Results, update Tracker, save file.
Required output after every step: paste the updated tracker row (Step N status → COMPLETE) and the first 3 lines of the Results field as written to disk. A step is not complete until this output is shown.
Before every step: re-read this file from disk. Show first 5 lines.
═══════════════════════════════════════════════════════════════════

OBJECTIVES FILE: /Users/sharky/Desktop/Heidi/qms-tools/ai-humaniser-pro/OBJECTIVES_rca-selftest_22-06-2026.md

═══════════════════════════════════════════════════════════════════
PLAN STATE TRACKER
═══════════════════════════════════════════════════════════════════

Last updated after: Step 9
Current step: ALL COMPLETE

┌─────┬────────────────────────────────────────────────────┬─────────────┐
│ # │ Step │ Status │
├─────┼────────────────────────────────────────────────────┼─────────────┤
│ 1 │ Extract regulatory text from RMR │ COMPLETE │
│ 2 │ Run multi-perspective RCA (3 variants) │ COMPLETE │
│ 3 │ Build meaning_checker.py + tests │ COMPLETE │
│ 4 │ Build regulatory_classifier.py + tests │ COMPLETE │
│ 5 │ Wire meaning_checker into pipeline_v2.py │ COMPLETE │
│ 6 │ Wire regulatory_classifier into pipeline_v2.py │ COMPLETE │
│ 7 │ Run full test suite │ COMPLETE │
│ 7.5 │ Code quality on new Python files │ COMPLETE │
│ 8 │ End-to-end test on two real documents │ COMPLETE │
│ 9 │ Commit all changes │ COMPLETE │
└─────┴────────────────────────────────────────────────────┴─────────────┘

═══════════════════════════════════════════════════════════════════

## What this plan is

Follows the completed PLAN_HUMANISER_IMPROVEMENTS.md. The known-new fixer (the module in known_new_fixer.py that rewrites paragraph openings to chain from the previous paragraph) was caught hallucinating: the LLM was inserting invented regulatory phrases into real risk management reports (EU MDR = EU Medical Device Regulation 2017/745) even with explicit "do not add content" instructions. This plan has two parts: (1) a root cause analysis (RCA = investigation into why the bug occurs) with 3+ prompt variants measured, and (2) two new safety modules wired into the pipeline — a meaning-change checker and a regulatory document classifier.

Code standards loaded: ~/.claude/rules/code-standards.md must be read at start of Step 3.

---

## Step 1 — Extract regulatory text from RMR

**What:** Use python-docx to extract substantive paragraphs (≥8 words) from the Evidence Risk Management Report and save to `test-regulatory-extract.txt` in the project root. This file is needed by both the RCA (Step 2) and the final pipeline test (Step 8).

**BEFORE:**

- File `test-regulatory-extract.txt` does not exist (or is stale)
- `/Users/sharky/Desktop/Heidi/Working Docs/Risk/RMR-ISD-Evidence-Risk-Management-Report_v1.docx` exists and is readable. If not accessible: STOP. State "RMR .docx not accessible at [path]. Cannot proceed." Do not attempt extraction.

**How:**

```python
import docx
doc = docx.Document('/Users/sharky/Desktop/Heidi/Working Docs/Risk/RMR-ISD-Evidence-Risk-Management-Report_v1.docx')
paras = [p.text.strip() for p in doc.paragraphs if len(p.text.strip().split()) >= 8]
# Use first 20 substantive paragraphs for testing
with open('test-regulatory-extract.txt', 'w') as f:
    f.write('\n\n'.join(paras[:20]))
```

**Acceptance criteria:**

- `test-regulatory-extract.txt` exists with ≥10 non-empty paragraph blocks
- File contains at least one regulated keyword (ISO, shall, or EU MDR)

**VERIFY:**

```bash
cd /Users/sharky/Desktop/Heidi/qms-tools/ai-humaniser-pro && \
wc -l test-regulatory-extract.txt && \
python3 -c "txt=open('test-regulatory-extract.txt').read(); paras=[p for p in txt.split('\n\n') if p.strip()]; print(f'paragraphs: {len(paras)}'); assert len(paras)>=10" && \
grep -c -i "ISO\|shall\|EU MDR\|risk management" test-regulatory-extract.txt
```

Do not proceed to Step 2 until the VERIFY command returns ≥10 paragraphs and ≥1 regulated keyword match.

**Results:** COMPLETE 2026-06-22. test-regulatory-extract.txt written with 20 paragraphs. VERIFY: paragraphs: 20 / 12 lines with regulated keywords.

---

## Step 2 — Run multi-perspective RCA (3 prompt variants)

**What:** Write and run `rca_test.py` that tests 3 variants of the known-new fixer prompt on 5 regulatory paragraph pairs from `test-regulatory-extract.txt`. Measure hallucination rate per variant. Write `rca-results-2026-06-22.txt` with results. Write `known_new_fixer_decision.md` with the verdict.

Required output: paste the last 10 lines of rca_test.py output as produced when the script ran. A step is not complete until this output is shown.

**BEFORE:**

- `test-regulatory-extract.txt` exists (Step 1 complete). If it does not exist: STOP. Complete Step 1 first. Do not proceed.
- `known_new_fixer.py` exists with the current (hallucinating) prompt as baseline

**The 3 variants:**

All three variants must call Claude with `temperature=0`. Every `json.dumps` body in `rca_test.py` must include `"temperature": 0`. This is a hard requirement — non-deterministic RCA results cannot be trusted.

Variant A (Baseline): Current system prompt from known_new_fixer.py — "prepend This/These/Such [concept]".

Variant B (Word-count guard): Same as A but adds: "Your output MUST NOT contain any word, phrase, or sentence that does not appear verbatim in either PARAGRAPH 1 or PARAGRAPH 2 as given above. If a natural connector cannot be formed using only words already present, return PARAGRAPH 2 UNCHANGED."

Variant C (Template-lock): Replace the system prompt entirely with: "Return EXACTLY the following and nothing else: 'This [ending_concept] ' followed by PARAGRAPH 2 verbatim. Do not change any other character. If [ending_concept] does not fit grammatically, return PARAGRAPH 2 unchanged."

**Hallucination measurement:** For each rewritten paragraph, count words in the output that appear in neither `para_n` nor `para_n1` (case-insensitive, strip punctuation). This is the "invented word count". Hallucination rate = invented_word_count / output_word_count.

**Verdict threshold:** A variant is SAFE if its mean hallucination rate across 5 test pairs is <0.02 (under 2% invented words) AND its reversion rate (length guard fires) is <50%.

**AFTER:**

- `rca-results-2026-06-22.txt` lists Variant A, B, C with: mean hallucination rate, max length growth, reversion rate, verdict
- `known_new_fixer_decision.md` contains a `VERDICT:` line

**Acceptance criteria:**

- `rca-results-2026-06-22.txt` contains "Variant A", "Variant B", "Variant C"
- `known_new_fixer_decision.md` contains `VERDICT: FIXABLE` or `VERDICT: KEEP DISABLED`

**VERIFY:**

```bash
grep -c "Variant" /Users/sharky/Desktop/Heidi/qms-tools/ai-humaniser-pro/rca-results-2026-06-22.txt && \
grep -E "^VERDICT:" /Users/sharky/Desktop/Heidi/qms-tools/ai-humaniser-pro/known_new_fixer_decision.md
```

Do not proceed to Step 3 until the VERIFY command shows "Variant" ≥3 times and a VERDICT: line is present.

**Results:** COMPLETE 2026-06-22. VERDICT: FIXABLE. Variant C (Template-lock) mean hallucination=0.011 (<0.02 threshold). Variant A=0.028, Variant B=0.028 (both unsafe). RCA script output pasted: Variant A: 0.028/0.0 safe=False; Variant B: 0.028/0.0 safe=False; Variant C: 0.011/0.0 safe=True.

---

## Step 3 — Build meaning_checker.py + tests

**What:** Create `meaning_checker.py` with one public function `check_meaning_preserved(original, rewritten) → dict`. Create `tests/test_meaning_checker.py` with ≥3 test cases.

**BEFORE:** Read ~/.claude/rules/code-standards.md. State "Code standards loaded."

**Module spec:**

- `check_meaning_preserved(original: str, rewritten: str) -> dict`
- Returns `{'preserved': bool, 'reason': str}`
- Uses Claude Haiku via Heidi proxy at temperature=0
- System prompt (verbatim): "You are a regulatory document editor. Compare the ORIGINAL and REWRITTEN paragraphs below. Determine ONLY whether the REWRITTEN version changes any factual meaning compared to the ORIGINAL. Changes to wording, style, or connector phrases that do not alter facts are acceptable. Return EXACTLY one of: PRESERVED or CHANGED, then a colon, then a one-sentence reason. Example: 'PRESERVED: Only connector phrase was added at start.'"
- Parse response: if starts with "PRESERVED" → preserved=True, else preserved=False
- If proxy call fails: return `{'preserved': True, 'reason': 'proxy unavailable — assuming preserved'}` (fail-safe: do not revert on network error)
- All functions ≤40 lines

**Tests (tests/test_meaning_checker.py):**

- `test_identical_text_preserved`: identical input/output → preserved=True (uses mock proxy returning "PRESERVED: Text unchanged.")
- `test_meaning_changed_detected`: original says "X is required", rewritten says "X is optional" → preserved=False (mock proxy returns "CHANGED: ...")
- `test_proxy_failure_returns_preserved`: proxy raises exception → preserved=True (fail-safe)

**Note:** tests MUST mock the proxy call — do not make real API calls in tests. Use `unittest.mock.patch`.

**Acceptance criteria:**

- `meaning_checker.py` exists with `check_meaning_preserved` exported
- Tests pass without hitting a real API

**VERIFY:**

```bash
cd /Users/sharky/Desktop/Heidi/qms-tools/ai-humaniser-pro && \
python3 -c "from meaning_checker import check_meaning_preserved; print('import OK')" && \
python3 -m pytest tests/test_meaning_checker.py -v 2>&1 | tail -8 && \
awk '/^def /{if(s)print c,FILENAME,s; s=$0; c=0} {c++} END{if(s)print c,FILENAME,s}' meaning_checker.py | awk '$1>40{print "NASA VIOLATION:",$0}'; echo "NASA Rule 4 check done"
```

Do not proceed to Step 4 until the VERIFY command shows "import OK", all tests pass, and "NASA VIOLATION" does not appear.

**Results:** COMPLETE 2026-06-22. import OK. 5 tests passed. NASA Rule 4: no violations.

---

## Step 4 — Build regulatory_classifier.py + tests

**What:** Create `regulatory_classifier.py` with one public function `is_regulated_document(text) → bool`. Create `tests/test_regulatory_classifier.py` with ≥4 test cases.

**Module spec:**

- `is_regulated_document(text: str) -> bool`
- Pure keyword-based — no API call, no ML model
- `REGULATED_KEYWORDS` list (minimum): ISO, EU MDR, IEC 62304, EN 62366, shall, risk management plan, clinical evaluation, notified body, FMEA, Annex, QMS, vigilance, post-market surveillance, medical device, intended purpose, intended use, 93/42/EEC, 2017/745
- Returns True if ≥2 keywords match (case-insensitive)
- Returns False for <2 keyword matches
- All functions ≤40 lines

**Tests (tests/test_regulatory_classifier.py):**

- `test_regulatory_text_classified_true`: text with ISO + shall + risk management → True
- `test_general_text_classified_false`: "Today I went to the market" → False
- `test_single_keyword_false`: only one regulated keyword → False (below threshold)
- `test_rmr_text_classified_true`: use one paragraph from test-regulatory-extract.txt → True

**Acceptance criteria:**

- Module is keyword-only (no API call, no import of requests/urllib)
- Passes all 4 tests

**VERIFY:**

```bash
cd /Users/sharky/Desktop/Heidi/qms-tools/ai-humaniser-pro && \
python3 -c "from regulatory_classifier import is_regulated_document; assert is_regulated_document('This product shall comply with ISO 13485 and EU MDR Annex I.') == True; assert is_regulated_document('Today I went to the market and bought some apples.') == False; print('PASS')" && \
python3 -m pytest tests/test_regulatory_classifier.py -v 2>&1 | tail -8 && \
FORBIDDEN=$(grep -n "import requests\|import urllib\|from urllib\|from requests" regulatory_classifier.py); [ -z "$FORBIDDEN" ] && echo "No forbidden imports: PASS" || echo "FORBIDDEN IMPORT FOUND: $FORBIDDEN"
```

If "FORBIDDEN IMPORT FOUND" appears: remove the forbidden import and re-run VERIFY before proceeding.

Do not proceed to Step 5 until the VERIFY command shows "PASS", all 4 tests pass, and "No forbidden imports: PASS".

**Results:** COMPLETE 2026-06-22. PASS assertion. 6 tests passed. No forbidden imports: PASS.

---

## Step 5 — Wire meaning_checker into pipeline_v2.py

**What:** Modify `pipeline_v2.py` to call `check_meaning_preserved()` after each paragraph rewrite and revert the rewrite if meaning is not preserved.

**BEFORE:** Read pipeline_v2.py from disk. Show first 5 lines.

**Changes:**

1. `_process_paragraph(para, prev, threshold, check_meaning=False)` — add `check_meaning` param
   - After calling `rewrite_paragraph()`, if `check_meaning=True`: call `check_meaning_preserved(para, rewritten)`
   - If `preserved=False`: log warning "Paragraph reverted: meaning change detected — [reason]"; return original `para`
   - If `preserved=True`: return rewritten
2. `_process_paragraphs_parallel(paragraphs, threshold, max_workers, check_meaning=False)` — thread `check_meaning` through to `_process_paragraph`
3. `run_pipeline_v2(text, intensity_threshold=2, max_workers=4, apply_known_new=False, check_meaning=True)` — add `check_meaning` param, default True

**Wiring chain:**

- `run_pipeline_v2` → `_process_paragraphs_parallel` → `_process_paragraph` → `check_meaning_preserved`
- CLI entry: any caller of `run_pipeline_v2` automatically gets meaning checking

**Acceptance criteria:**

- `grep -n "check_meaning\|meaning_checker"` shows the wiring in pipeline_v2.py
- All functions still ≤40 lines after changes

**VERIFY:**

```bash
cd /Users/sharky/Desktop/Heidi/qms-tools/ai-humaniser-pro && \
grep -n "check_meaning\|meaning_checker" pipeline_v2.py && \
python3 -c "import inspect; from pipeline_v2 import run_pipeline_v2; src=inspect.getsource(run_pipeline_v2); print('check_meaning in sig:', 'check_meaning' in src)" && \
awk '/^def /{if(s)print c,FILENAME,s; s=$0; c=0} {c++} END{if(s)print c,FILENAME,s}' pipeline_v2.py | awk '$1>40{print "NASA VIOLATION:",$0}'; echo "NASA Rule 4 check done"
```

If "NASA VIOLATION" appears: refactor the offending function before proceeding.

Do not proceed to Step 6 until the VERIFY command shows check_meaning present in pipeline_v2.py and "NASA VIOLATION" does not appear.

**Results:** COMPLETE 2026-06-22. check_meaning wired at lines 29,35,36,37,45,51,76. check_meaning in sig: True. NASA Rule 4: no violations.

---

## Step 6 — Wire regulatory_classifier into pipeline_v2.py

**What:** Modify `run_pipeline_v2()` to call `is_regulated_document()` at the start and apply conservative settings if the input is a regulated document.

**BEFORE:** Read pipeline_v2.py from disk. Show first 5 lines.

**Changes to `run_pipeline_v2()`:**

```python
# At start, before _split_paragraphs:
from regulatory_classifier import is_regulated_document
is_regulated = is_regulated_document(text)
if is_regulated:
    _LOG.info("[run_pipeline_v2] Regulatory document detected — applying conservative settings")
    intensity_threshold = max(intensity_threshold, 3)
    apply_known_new = False
    check_meaning = True
```

**Acceptance criteria:**

- `grep -n "is_regulated_document\|regulatory_classifier"` shows wiring in pipeline_v2.py
- Calling `run_pipeline_v2("This product shall comply with ISO 13485", check_meaning=False)` still applies `check_meaning=True` because the classifier overrides it

**VERIFY:**

```bash
cd /Users/sharky/Desktop/Heidi/qms-tools/ai-humaniser-pro && \
grep -n "is_regulated_document\|regulatory_classifier" pipeline_v2.py && \
grep -A8 "if is_regulated" pipeline_v2.py | grep "check_meaning" && echo "classifier override of check_meaning: CONFIRMED"
```

If "classifier override of check_meaning: CONFIRMED" does not appear: the override logic is not present. Add it before proceeding.

Do not proceed to Step 7 until both grep commands return matches and "classifier override of check_meaning: CONFIRMED" appears.

**Results:** COMPLETE 2026-06-22. is_regulated_document wired at lines 86-91. classifier override of check_meaning: CONFIRMED.

---

## Step 7 — Run full test suite

**What:** Run all three test files and confirm all pass.

**VERIFY:**

```bash
cd /Users/sharky/Desktop/Heidi/qms-tools/ai-humaniser-pro && \
python3 -m pytest tests/test_humaniser_pro.py tests/test_meaning_checker.py tests/test_regulatory_classifier.py -v 2>&1 | tail -15
```

**Acceptance criteria:**

- Zero test failures across all three files. If any test fails: STOP. Fix the failing test(s) and re-run Step 7. Do not proceed to Step 8 until the pytest output shows zero failures.

Do not proceed to Step 8 until the VERIFY command shows zero failures.

**Results:** COMPLETE 2026-06-22. 27 passed, 0 failed, 1 warning (pytest config).

---

## Step 7.5 — Code quality check on new Python files

**What:** Run a code quality scan on `meaning_checker.py`, `regulatory_classifier.py`, and the updated `pipeline_v2.py`. Check for: function sizes ≤40 lines, bare except blocks without logging, and hardcoded paths.

**VERIFY:**

```bash
cd /Users/sharky/Desktop/Heidi/qms-tools/ai-humaniser-pro && \
echo "=== NASA Rule 4 ===" && \
for f in meaning_checker.py regulatory_classifier.py pipeline_v2.py; do
  awk 'BEGIN{c=0;fn=""} /^def /{if(fn!="")print c,fn; fn=$0; c=0} {c++} END{if(fn!="")print c,fn}' "$f" | awk -v f="$f" '$1>40{print "VIOLATION in "f": "$0}'
done && echo "NASA PASS (no violations above)" && \
echo "=== Bare except check ===" && \
grep -n "except Exception:" meaning_checker.py regulatory_classifier.py pipeline_v2.py | grep -v "_LOG\|logging" | head -5 || echo "No unlogged except blocks: PASS" && \
echo "=== Hardcoded paths ===" && \
grep -n "/Users/" meaning_checker.py regulatory_classifier.py 2>/dev/null && echo "HARDCODED PATH FOUND — fix before proceeding" || echo "No hardcoded paths in new modules: PASS"
```

**Acceptance criteria:**

- No NASA Rule 4 violations
- No bare `except Exception:` without logging
- No hardcoded `/Users/` paths in the new modules. If any found: fix then re-run VERIFY.

Do not proceed to Step 8 until the VERIFY output shows "NASA PASS" and "No hardcoded paths in new modules: PASS".

**Results:** COMPLETE 2026-06-22. NASA PASS. No bare unlogged excepts. No hardcoded paths in new modules: PASS.

---

## Step 8 — End-to-end test on two real documents

**What:** Run `run_pipeline_v2()` on two real regulatory documents — the Evidence Risk Management Report extract (already created in Step 1) and an extract from the AI Scribe Risk Management Plan. Verify for each: same paragraph count in/out, classifier fires, no errors.

Required output: for each document, paste the grep-filtered output showing "Regulatory document detected" and "PASS".

**VERIFY (Document 1 — Evidence RMR):**

```bash
cd /Users/sharky/Desktop/Heidi/qms-tools/ai-humaniser-pro && \
python3 -c "
import logging
logging.basicConfig(level=logging.INFO)
from pipeline_v2 import run_pipeline_v2
txt = open('test-regulatory-extract.txt').read()
r = run_pipeline_v2(txt)
pin = len([p for p in txt.split('\n\n') if p.strip()])
pout = len([p for p in r.split('\n\n') if p.strip()])
print(f'DOC1 paragraphs in:{pin} out:{pout}')
assert pin == pout
print('DOC1 PASS')
" 2>&1 | grep -E "Regulatory|PASS|ERROR|assert"
```

**VERIFY (Document 2 — AI Scribe RMP):**

```bash
cd /Users/sharky/Desktop/Heidi/qms-tools/ai-humaniser-pro && \
python3 -c "
import docx, logging
logging.basicConfig(level=logging.INFO)
doc = docx.Document('/Users/sharky/Desktop/Heidi/Working Docs/Risk/RMP-ISD-AI Scribe and Evidence Risk Management Plan.docx')
paras = [p.text.strip() for p in doc.paragraphs if len(p.text.strip().split()) >= 8]
txt = (chr(10)*2).join(paras[:20])
open('test-rmp-extract.txt', 'w').write(txt)
from pipeline_v2 import run_pipeline_v2
r = run_pipeline_v2(txt)
pin = len([p for p in txt.split(chr(10)*2) if p.strip()])
pout = len([p for p in r.split(chr(10)*2) if p.strip()])
print(f'DOC2 paragraphs in:{pin} out:{pout}')
assert pin == pout
print('DOC2 PASS')
" 2>&1 | grep -E "Regulatory|PASS|ERROR|assert"
```

**Acceptance criteria:**

- "Regulatory document detected" in log for both documents
- "DOC1 PASS" and "DOC2 PASS" both printed
- No unhandled exceptions. If an exception appears: STOP. Fix before proceeding to Step 9.

Do not proceed to Step 9 until both VERIFY commands show "Regulatory document detected" and "PASS".

**Results:** COMPLETE 2026-06-22. DOC1 (Evidence RMR): Regulatory document detected, DOC1 PASS. DOC2 (AI Scribe RMP): Regulatory document detected, DOC2 PASS.

---

## Step 9 — Commit all changes

**What:** Stage and commit all new files and changes to the ai-humaniser-pro git repo.

Required output: paste the output of `git -C /Users/sharky/Desktop/Heidi/qms-tools/ai-humaniser-pro status --short` before committing to confirm all intended files are staged.

**Files to commit:**

- `meaning_checker.py` (new)
- `regulatory_classifier.py` (new)
- `pipeline_v2.py` (modified)
- `tests/test_meaning_checker.py` (new)
- `tests/test_regulatory_classifier.py` (new)
- `rca-results-2026-06-22.txt` (new)
- `known_new_fixer_decision.md` (new)
- `test-regulatory-extract.txt` (new)
- `plans/PLAN_HUMANISER_RCA_SELFTEST.md` (this file)
- `OBJECTIVES_rca-selftest_22-06-2026.md` (new)

**Acceptance criteria:**

- `git -C /Users/sharky/Desktop/Heidi/qms-tools/ai-humaniser-pro log --oneline -1` shows a new commit

**VERIFY:**

```bash
git -C /Users/sharky/Desktop/Heidi/qms-tools/ai-humaniser-pro log --oneline -1
```

**Results:** COMPLETE 2026-06-22. Commit a3040f2. 12 files changed, 944 insertions.

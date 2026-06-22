═══════════════════════════════════════════════════════════════════
EXECUTION PROTOCOL — READ THIS BEFORE DOING ANYTHING ELSE
═══════════════════════════════════════════════════════════════════

This plan is stored at: /Users/sharky/Desktop/Heidi/qms-tools/ai-humaniser-pro/plans/PLAN_HUMANISER_WEB_DEPLOY.md
That file is the source of truth. Your in-context memory is not.

── BEFORE EVERY STEP ───────────────────────────────────────────────
□ 1. READ THE FILE. Required output: first 5 lines.
□ 2. LOCATE CURRENT STEP. Confirm step title.
□ 3. CHECK RESULTS FIELD: state "empty/interrupted/filled".
□ 4. NEW SESSION CHECK: if new session, read entire plan first.

── AFTER COMPLETING EVERY STEP ─────────────────────────────────────
□ 1. WRITE RESULTS. Append only, never overwrite.
□ 2. PLAN-CHANGE CHECK: state "No plan changes required" or STOP.
□ 3. (RESERVED)
□ 4. UPDATE TRACKER.
□ 5. SAVE FILE. Show first 3 lines.
□ 6. PHASE BOUNDARY CHECK: session:single — skip /chat-handoff.

── ANTI-DRIFT ───────────────────────────────────────────────────────
The file is always right. Your memory is not.
A step is not complete until its Results field is written and saved.
═══════════════════════════════════════════════════════════════════

OBJECTIVES FILE: /Users/sharky/Desktop/Heidi/qms-tools/ai-humaniser-pro/OBJECTIVES_web-deploy_21-06-2026.md

═══════════════════════════════════════════════════════════════════
PLAN STATE TRACKER
═══════════════════════════════════════════════════════════════════

Last updated after: Not started
Current step: Not started

┌─────┬────────────────────────────────────────────────────┬─────────────┐
│ # │ Step Name │ Status │
├─────┼────────────────────────────────────────────────────┼─────────────┤
│ │ ── STREAM 1: CODE QUALITY ── │ │
│ 1 │ /code-quality on profiles/regulatory.py │ PENDING │
│ 2 │ /code-quality on known_new_contract_checker.py │ PENDING │
│ │ ── STREAM 2: PARALLELISATION ── │ │
│ 3 │ Add ThreadPoolExecutor to pipeline_v2.py │ PENDING │
│ 4 │ Test + verify parallelised pipeline │ PENDING │
│ │ ── STREAM 3: BROWSER TOOL + DEPLOY ── │ │
│ 5 │ Read existing QMS tool template │ PENDING │
│ 6 │ Build ai-humaniser-pro.jsx │ PENDING │
│ 7 │ Build index.html │ PENDING │
│ 8 │ Create oscerai/ai-humaniser-pro repo │ PENDING │
│ 9 │ Push and set up GitHub Pages │ PENDING │
│ 10 │ Update /humanize skill with web URL │ PENDING │
│ 11 │ /code-quality on ai-humaniser-pro.jsx │ PENDING │
│ 12 │ Commit all Python changes │ PENDING │
└─────┴────────────────────────────────────────────────────┴─────────────┘

Status values: PENDING / IN PROGRESS / COMPLETE / FAILED / SKIPPED
═══════════════════════════════════════════════════════════════════

## What this plan is

Deploys the AI Humaniser Pro as a browser-based web tool on GitHub Pages (oscerai/ai-humaniser-pro) so any team member can paste or upload a document and humanise it without Python. Also parallelises the Python pipeline for speed and completes code quality on the two remaining modules. Follows PLAN_KNOWN_NEW_FIXER_BUILD.md.

## Objective

Turn the AI Humaniser Pro into a browser-accessible tool at oscerai.github.io/ai-humaniser-pro, with parallel processing for speed and complete code quality coverage.

## Scope

IN:

- /code-quality on profiles/regulatory.py and known_new_contract_checker.py
- ThreadPoolExecutor parallelisation of pipeline_v2.py pattern-detect+rewrite pass
- React/JSX browser tool (ai-humaniser-pro.jsx + index.html) using Heidi proxy
- GitHub repo creation + Pages deployment
- /humanize skill updated with web URL

OUT OF SCOPE:

- DistilGPT-2 perplexity in browser (requires Python)
- spaCy-based known-new detection in browser (requires Python)
- Modifying v1 modules

## Constraints

- Heidi proxy for all Claude API calls in browser tool
- Protected terms listed in JSX system prompt (never dropped)
- NASA Rule: all Python functions ≤40 lines
- Follow Heidi shared-ui design system (unified header, feedback modal)
- GitHub Pages auto-deploy via Actions on push to main
- session: single — plan file survives compaction
- Recommended model: claude-sonnet-4-6

## Dependency summary

Step 1: depends_on []
Step 2: depends_on []
Step 3: depends_on []
Step 4: depends_on [3]
Step 5: depends_on []
Step 6: depends_on [5]
Step 7: depends_on [6]
Step 8: depends_on []
Step 9: depends_on [6, 7, 8]
Step 10: depends_on [9]
Step 11: depends_on [6]
Step 12: depends_on [1,2,3,4,10,11]

Parallel opportunities: Steps 1, 2, 3, 5, 8 can run concurrently.

---

# STREAM 1 — CODE QUALITY

---

## Step 1 — /code-quality on profiles/regulatory.py

**What:** Run /code-quality on profiles/regulatory.py. Fix all safe root-cause findings automatically. Update BUGS_AND_LESSONS.md.

**Acceptance criteria:**

- /code-quality runs and reports findings or "No findings"
- Any safe fixes applied with root cause analysis
- BUGS_AND_LESSONS.md updated if fixes were made

**depends_on:** []

```
┌── BEFORE ────────────────────────────────────────────────────────────┐
│ □ 1. READ FILE. □ 2. CONFIRM STEP TITLE. □ 3. UPDATE TRACKER.      │
└──────────────────────────────────────────────────────────────────────┘
┌── AFTER ─────────────────────────────────────────────────────────────┐
│ □ 1. WRITE RESULTS. □ 2. PLAN-CHANGE CHECK. □ 4. UPDATE TRACKER.   │
│ □ 5. SAVE FILE. □ 6. PHASE BOUNDARY: NO.                           │
└──────────────────────────────────────────────────────────────────────┘
```

**Results:** [EMPTY — fill on execution]

---

## Step 2 — /code-quality on known_new_contract_checker.py

**What:** Run /code-quality on known_new_contract_checker.py. Fix all safe root-cause findings. Update BUGS_AND_LESSONS.md.

**Acceptance criteria:**

- /code-quality runs and reports findings or "No findings"
- Any safe fixes applied
- BUGS_AND_LESSONS.md updated if fixes were made

**depends_on:** []

```
┌── BEFORE ────────────────────────────────────────────────────────────┐
│ □ 1. READ FILE. □ 2. CONFIRM STEP TITLE. □ 3. UPDATE TRACKER.      │
└──────────────────────────────────────────────────────────────────────┘
┌── AFTER ─────────────────────────────────────────────────────────────┐
│ □ 1. WRITE RESULTS. □ 2. PLAN-CHANGE CHECK. □ 4. UPDATE TRACKER.   │
│ □ 5. SAVE FILE. □ 6. PHASE BOUNDARY: NO.                           │
└──────────────────────────────────────────────────────────────────────┘
```

**Results:** [EMPTY — fill on execution]

---

# STREAM 2 — PARALLELISATION

---

## Step 3 — Add ThreadPoolExecutor to pipeline_v2.py

**What:** Add `_process_paragraphs_parallel(paragraphs, threshold, max_workers)` to pipeline_v2.py using `concurrent.futures.ThreadPoolExecutor`. Update `run_pipeline_v2()` to call it. max_workers default=4. Add `from concurrent.futures import ThreadPoolExecutor` at module top. All functions ≤40 lines.

**Code to add:**

```python
from concurrent.futures import ThreadPoolExecutor
_DEFAULT_MAX_WORKERS = 4

def _process_paragraphs_parallel(
    paragraphs: list[str], threshold: int, max_workers: int
) -> list[str]:
    """Process paragraphs concurrently; I/O-bound rewriting safe to parallelise."""
    def _process_one(item: tuple) -> str:
        i, para = item
        prev = paragraphs[i - 1] if i > 0 else ""
        return _process_paragraph(para, prev, threshold)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        return list(executor.map(_process_one, enumerate(paragraphs)))
```

**Updated run_pipeline_v2 signature:**

```python
def run_pipeline_v2(
    text: str,
    intensity_threshold: int = _DEFAULT_THRESHOLD,
    max_workers: int = _DEFAULT_MAX_WORKERS,
) -> str:
    """Humanise text: parallel pattern-detect → rewrite → sequential known-new chain."""
    if not text or not text.strip():
        return text
    paragraphs = _split_paragraphs(text)
    processed = _process_paragraphs_parallel(paragraphs, intensity_threshold, max_workers)
    processed = _apply_known_new_fix(processed)
    return "\n\n".join(processed)
```

**Acceptance criteria:**

- `grep -n "ThreadPoolExecutor" pipeline_v2.py` returns ≥1 match
- `python3 -m pytest tests/test_humaniser_pro.py -q 2>&1 | tail -2` shows all passing
- `python3 -m py_compile pipeline_v2.py && echo PASS`
- Per-file NASA check: no function >40 lines

**depends_on:** []

```
┌── BEFORE ────────────────────────────────────────────────────────────┐
│ □ 1. READ FILE. □ 2. CONFIRM STEP TITLE. □ 3. UPDATE TRACKER.      │
└──────────────────────────────────────────────────────────────────────┘
┌── AFTER ─────────────────────────────────────────────────────────────┐
│ □ 1. WRITE RESULTS. □ 2. PLAN-CHANGE CHECK. □ 4. UPDATE TRACKER.   │
│ □ 5. SAVE FILE. □ 6. PHASE BOUNDARY: NO.                           │
└──────────────────────────────────────────────────────────────────────┘
```

**Results:** [EMPTY — fill on execution]

---

## Step 4 — Test + verify parallelised pipeline

**What:** Run the end-to-end structural improvement test with the parallelised pipeline. Confirm structural_score still decreases on the ChatGPT test document.

**Acceptance criteria:**

- `python3 -c "from pipeline_v2 import run_pipeline_v2; from scorer_v2 import score_document_v2; txt=open('test-chatgpt-rapamycin.txt').read(); before=score_document_v2(txt)['structural_score']; result=run_pipeline_v2(txt); after=score_document_v2(result)['structural_score']; print(f'before:{before:.3f} after:{after:.3f}'); assert after<before"` exits 0

**depends_on:** [3]

```
┌── BEFORE ────────────────────────────────────────────────────────────┐
│ □ 1. READ FILE. □ 2. CONFIRM STEP TITLE. □ 3. UPDATE TRACKER.      │
└──────────────────────────────────────────────────────────────────────┘
┌── AFTER ─────────────────────────────────────────────────────────────┐
│ □ 1. WRITE RESULTS. □ 2. PLAN-CHANGE CHECK. □ 4. UPDATE TRACKER.   │
│ □ 5. SAVE FILE. □ 6. PHASE BOUNDARY: YES — session:single, skip.   │
│    Continuing to Stream 3.                                          │
└──────────────────────────────────────────────────────────────────────┘
```

**Results:** [EMPTY — fill on execution]

---

# STREAM 3 — BROWSER TOOL + DEPLOY

---

## Step 5 — Read existing QMS tool template

**What:** Read the shared-ui NEW_PROJECT_TEMPLATE.md and an existing JSX tool (e.g. doc_generator_v2_1_0.jsx header section) to understand the exact pattern for proxy, settings gear, unified header, and feedback modal. Extract the proxy boilerplate and shared-ui imports.

**Acceptance criteria:**

- `ls /Users/sharky/Desktop/Heidi/qms-tools/shared-ui/NEW_PROJECT_TEMPLATE.md` exits 0
- PROXY_URL_DEFAULT, getProxyUrl(), callViaProxy(), callAnthropic() patterns confirmed

**depends_on:** []

```
┌── BEFORE ────────────────────────────────────────────────────────────┐
│ □ 1. READ FILE. □ 2. CONFIRM STEP TITLE. □ 3. UPDATE TRACKER.      │
└──────────────────────────────────────────────────────────────────────┘
┌── AFTER ─────────────────────────────────────────────────────────────┐
│ □ 1. WRITE RESULTS with key patterns extracted. □ 4. UPDATE TRACKER.│
│ □ 5. SAVE FILE. □ 6. PHASE BOUNDARY: NO.                           │
└──────────────────────────────────────────────────────────────────────┘
```

**Results:** [EMPTY — fill on execution]

---

## Step 6 — Build ai-humaniser-pro.jsx

**What:** Write `/Users/sharky/Desktop/Heidi/qms-tools/ai-humaniser-pro/ai-humaniser-pro.jsx` — a React/JSX browser tool following the Heidi architecture. Components:

- ProxySettings / SettingsGear (from shared template)
- UnifiedHeader (tool name: "AI Humaniser Pro β")
- DocumentInput: textarea + file upload (.txt, .docx via FileReader)
- PatternDisplay: show before pattern counts (connectors, nominalisations)
- HumaniseButton: calls rewriteParagraph() for each paragraph via Heidi proxy
- ResultDisplay: before/after text comparison + after pattern counts
- DownloadButton: saves result as .txt

**System prompt for rewriting (combined):**

```
You are a regulatory document editor. Rewrite the paragraph below to sound like a confident human expert wrote it:
- Remove or replace sentence-starting connectors: Furthermore, Additionally, Moreover, In addition, It is important to note
- Reverse nominalisations: "the implementation of X" → "implementing X"
- If CONTEXT is given, start with a phrase echoing the ending concept of CONTEXT
Never drop: shall, must, demonstrate, verify, validate, risk management, compliance, safety, hazard
Return ONLY the rewritten paragraph.
```

**Pattern detection (JS):**

```js
function countConnectors(text) {
  return (
    text.match(
      /^(Furthermore|Additionally|Moreover|In addition|It is important to note)/gim,
    ) || []
  ).length;
}
function nominalisationRatio(text) {
  const words = text.split(/\s+/);
  const nominals = text.match(/\b\w+(?:tion|ment|ance|ence|ity)\b/gi) || [];
  return words.length > 0 ? (nominals.length / words.length).toFixed(3) : 0;
}
```

**Acceptance criteria:**

- `ls /Users/sharky/Desktop/Heidi/qms-tools/ai-humaniser-pro/ai-humaniser-pro.jsx` exits 0
- `grep -c "PROXY_URL\|countConnectors\|download\|HumaniseButton\|PatternDisplay" ai-humaniser-pro.jsx` returns ≥ 5

**depends_on:** [5]

```
┌── BEFORE ────────────────────────────────────────────────────────────┐
│ □ 1. READ FILE. □ 2. CONFIRM STEP TITLE. □ 3. UPDATE TRACKER.      │
└──────────────────────────────────────────────────────────────────────┘
┌── AFTER ─────────────────────────────────────────────────────────────┐
│ □ 1. WRITE RESULTS. □ 2. PLAN-CHANGE CHECK. □ 4. UPDATE TRACKER.   │
│ □ 5. SAVE FILE. □ 6. PHASE BOUNDARY: NO.                           │
└──────────────────────────────────────────────────────────────────────┘
```

**Results:** [EMPTY — fill on execution]

---

## Step 7 — Build index.html

**What:** Write `/Users/sharky/Desktop/Heidi/qms-tools/ai-humaniser-pro/index.html` that loads React, ReactDOM, and Babel from CDN, loads the shared-ui scripts (unified-header.js, unified-footer.js, feedback-modal.js), and renders the ai-humaniser-pro.jsx component. Follows the existing Heidi tool HTML pattern.

**Acceptance criteria:**

- `ls /Users/sharky/Desktop/Heidi/qms-tools/ai-humaniser-pro/index.html` exits 0
- `grep -c "react\|babel\|ai-humaniser-pro.jsx" /Users/sharky/Desktop/Heidi/qms-tools/ai-humaniser-pro/index.html` returns ≥ 3

**depends_on:** [6]

```
┌── BEFORE ────────────────────────────────────────────────────────────┐
│ □ 1. READ FILE. □ 2. CONFIRM STEP TITLE. □ 3. UPDATE TRACKER.      │
└──────────────────────────────────────────────────────────────────────┘
┌── AFTER ─────────────────────────────────────────────────────────────┐
│ □ 1. WRITE RESULTS. □ 2. PLAN-CHANGE CHECK. □ 4. UPDATE TRACKER.   │
│ □ 5. SAVE FILE. □ 6. PHASE BOUNDARY: NO.                           │
└──────────────────────────────────────────────────────────────────────┘
```

**Results:** [EMPTY — fill on execution]

---

## Step 8 — Create oscerai/ai-humaniser-pro repo

**What:** Create the GitHub repository using `gh repo create oscerai/ai-humaniser-pro --public --description "AI Humaniser Pro — browser-based regulatory document humaniser"`. If repo already exists, skip creation and confirm it exists.

**Acceptance criteria:**

- `gh repo view oscerai/ai-humaniser-pro --json name 2>/dev/null | python3 -c "import sys,json; print(json.load(sys.stdin)['name'])"` prints `ai-humaniser-pro`

**depends_on:** []

```
┌── BEFORE ────────────────────────────────────────────────────────────┐
│ □ 1. READ FILE. □ 2. CONFIRM STEP TITLE. □ 3. UPDATE TRACKER.      │
└──────────────────────────────────────────────────────────────────────┘
┌── AFTER ─────────────────────────────────────────────────────────────┐
│ □ 1. WRITE RESULTS. □ 2. PLAN-CHANGE CHECK. □ 4. UPDATE TRACKER.   │
│ □ 5. SAVE FILE. □ 6. PHASE BOUNDARY: NO.                           │
└──────────────────────────────────────────────────────────────────────┘
```

**Results:** [EMPTY — fill on execution]

---

## Step 9 — Push and set up GitHub Pages

**What:** Add the remote, push the ai-humaniser-pro files (index.html, ai-humaniser-pro.jsx, and a minimal .github/workflows/pages.yml for GitHub Pages deployment). Enable GitHub Pages on the repo. Verify the Pages URL is configured.

**GitHub Actions workflow (pages.yml):**

```yaml
name: Deploy to GitHub Pages
on:
  push:
    branches: [main]
permissions:
  contents: read
  pages: write
  id-token: write
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/upload-pages-artifact@v3
        with:
          path: .
      - uses: actions/deploy-pages@v4
```

**Acceptance criteria:**

- `gh repo view oscerai/ai-humaniser-pro --json url 2>/dev/null` returns a URL
- `.github/workflows/pages.yml` exists in the pushed repo

**depends_on:** [6, 7, 8]

```
┌── BEFORE ────────────────────────────────────────────────────────────┐
│ □ 1. READ FILE. □ 2. CONFIRM STEP TITLE. □ 3. UPDATE TRACKER.      │
└──────────────────────────────────────────────────────────────────────┘
┌── AFTER ─────────────────────────────────────────────────────────────┐
│ □ 1. WRITE RESULTS. □ 2. PLAN-CHANGE CHECK. □ 4. UPDATE TRACKER.   │
│ □ 5. SAVE FILE. □ 6. PHASE BOUNDARY: NO.                           │
└──────────────────────────────────────────────────────────────────────┘
```

**Results:** [EMPTY — fill on execution]

---

## Step 10 — Update /humanize skill with web URL

**What:** Update /Users/sharky/.claude/commands/humanize.md to add the web tool URL at the top so users know about both the CLI and browser options.

**Acceptance criteria:**

- `grep -c "oscerai.github.io\|browser\|web tool" /Users/sharky/.claude/commands/humanize.md` returns ≥ 2

**depends_on:** [9]

```
┌── BEFORE ────────────────────────────────────────────────────────────┐
│ □ 1. READ FILE. □ 2. CONFIRM STEP TITLE. □ 3. UPDATE TRACKER.      │
└──────────────────────────────────────────────────────────────────────┘
┌── AFTER ─────────────────────────────────────────────────────────────┐
│ □ 1. WRITE RESULTS. □ 2. PLAN-CHANGE CHECK. □ 4. UPDATE TRACKER.   │
│ □ 5. SAVE FILE. □ 6. PHASE BOUNDARY: NO.                           │
└──────────────────────────────────────────────────────────────────────┘
```

**Results:** [EMPTY — fill on execution]

---

## Step 11 — /code-quality on ai-humaniser-pro.jsx

**What:** Run /code-quality on ai-humaniser-pro.jsx. Fix all safe findings. This chains to /deep-qa and /code-review automatically.

**Acceptance criteria:**

- /code-quality runs and reports findings or "No findings — all rules pass"
- Any safe fixes applied

**depends_on:** [6]

```
┌── BEFORE ────────────────────────────────────────────────────────────┐
│ □ 1. READ FILE. □ 2. CONFIRM STEP TITLE. □ 3. UPDATE TRACKER.      │
└──────────────────────────────────────────────────────────────────────┘
┌── AFTER ─────────────────────────────────────────────────────────────┐
│ □ 1. WRITE RESULTS. □ 2. PLAN-CHANGE CHECK. □ 4. UPDATE TRACKER.   │
│ □ 5. SAVE FILE. □ 6. PHASE BOUNDARY: NO.                           │
└──────────────────────────────────────────────────────────────────────┘
```

**Results:** [EMPTY — fill on execution]

---

## Step 12 — Commit all Python changes

**What:** Stage and commit all Python changes (pipeline_v2.py parallelisation, code quality fixes on regulatory.py and known_new_contract_checker.py, BUGS_AND_LESSONS.md updates) to the ai-humaniser-pro git repo.

**Acceptance criteria:**

- `git -C /Users/sharky/Desktop/Heidi/qms-tools/ai-humaniser-pro log --oneline -1` shows new commit with parallelisation/code-quality message

**depends_on:** [1, 2, 3, 4, 10, 11]

```
┌── BEFORE ────────────────────────────────────────────────────────────┐
│ □ 1. READ FILE. □ 2. CONFIRM STEP TITLE. □ 3. UPDATE TRACKER.      │
└──────────────────────────────────────────────────────────────────────┘
┌── AFTER ─────────────────────────────────────────────────────────────┐
│ □ 1. WRITE RESULTS. □ 2. PLAN-CHANGE CHECK. □ 4. UPDATE TRACKER.   │
│ □ 5. SAVE FILE. □ 6. PHASE BOUNDARY: YES (last step) — session:single,│
│    handoff skipped. Run H gate.                                     │
└──────────────────────────────────────────────────────────────────────┘
```

**Results:** [EMPTY — fill on execution]

---

## Risks and Open Questions

1. **oscerai/ai-humaniser-pro repo**: May need to be created. `gh repo create` requires org admin or appropriate permissions. If creation fails, fall back to creating a personal fork and notify.
2. **JSX browser tool**: Does not include perplexity scoring (Python-only). The tool shows pattern counts (JS-computable) and an estimated AI-score based on connector + nominalisation counts.
3. **GitHub Pages delay**: Pages take 1-2 minutes to go live after first push. The URL will be `https://oscerai.github.io/ai-humaniser-pro/`.
4. **ThreadPoolExecutor and Heidi proxy rate limits**: max_workers=4 limits concurrent API calls. If rate limits hit, individual paragraph rewrites fail gracefully (revert to original).

## Handoff Note

1. Next action: Execute Steps 1-4 first (code quality + parallelisation) — fast, no dependencies. Then Steps 5-12 (browser tool + deploy).
2. Step 1 is: Run /code-quality on profiles/regulatory.py.
3. Have ready: GitHub auth (confirmed), Heidi proxy (confirmed working).
4. What requires plan revision: If oscerai org doesn't allow repo creation, fall back to personal repo and update URL.
5. Recommended model: claude-sonnet-4-6.

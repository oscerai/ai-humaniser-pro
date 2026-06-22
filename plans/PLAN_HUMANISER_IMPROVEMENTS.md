═══════════════════════════════════════════════════════════════════
EXECUTION PROTOCOL
═══════════════════════════════════════════════════════════════════
This plan: /Users/sharky/Desktop/Heidi/qms-tools/ai-humaniser-pro/plans/PLAN_HUMANISER_IMPROVEMENTS.md
Source of truth. Memory is not. Plan survives auto-compaction.
After every step: write Results, update Tracker, save file.
═══════════════════════════════════════════════════════════════════

OBJECTIVES FILE: /Users/sharky/Desktop/Heidi/qms-tools/ai-humaniser-pro/OBJECTIVES_web-deploy_21-06-2026.md

═══════════════════════════════════════════════════════════════════
PLAN STATE TRACKER
═══════════════════════════════════════════════════════════════════

Last updated after: Not started
Current step: Not started

┌─────┬────────────────────────────────────────────────────┬─────────────┐
│  #  │ Step                                               │ Status      │
├─────┼────────────────────────────────────────────────────┼─────────────┤
│  1  │ Improve browser AI scoring (JS only, no model)    │ PENDING     │
│  2  │ Add sentence-rhythm burstiness to Python detector │ PENDING     │
│  3  │ Update browser tool in Hub                        │ PENDING     │
│  4  │ Test on 5 different documents + log results       │ PENDING     │
│  5  │ Commit + push all improvements                    │ PENDING     │
└─────┴────────────────────────────────────────────────────┴─────────────┘
═══════════════════════════════════════════════════════════════════

## What this plan is

Improves the AI Humaniser Pro by (1) upgrading the browser tool's AI-detection scoring from a simple 2-factor formula to a 5-factor weighted model covering connectors, nominalisations, passive voice, sentence uniformity, and paragraph uniformity, (2) improving the Python pattern detector's burstiness metric using proper statistical sentence-length variance, and (3) testing on 5 real documents to verify measurable improvement. Follows PLAN_HUMANISER_WEB_DEPLOY.md.

## Step 1 — Improve browser AI scoring

**What:** Update `analysePatterns()` and the `PatternStats` display in `ai-humaniser-pro.jsx` to use a 5-factor weighted AI score:
- Formulaic connectors (weight 15 per connector)
- Nominalisation ratio (weight 150)
- Passive voice density: count sentences containing "is/are/was/were + [past participle-like word]"
- Sentence length uniformity: stddev of sentence word counts — low stddev = AI (weight 30)
- Paragraph length uniformity: stddev of paragraph word counts — low stddev = AI (weight 20)

Also add a "structural_score" display showing known-new violations (estimated as % of paragraphs that start with a known AI connector or don't naturally follow from the previous paragraph's theme).

**New helper functions:**
```js
function passiveVoiceDensity(text) {
  const sentences = text.split(/[.!?]+/).filter(s => s.trim().length > 5);
  if (!sentences.length) return 0;
  const passive = sentences.filter(s => /\b(is|are|was|were|been|being)\s+\w+ed\b/i.test(s)).length;
  return passive / sentences.length;
}

function sentenceLengthVariance(text) {
  const sentences = text.split(/[.!?]+/).filter(s => s.trim().split(/\s+/).length > 2);
  if (sentences.length < 2) return 5;
  const lengths = sentences.map(s => s.trim().split(/\s+/).length);
  const mean = lengths.reduce((a,b) => a+b, 0) / lengths.length;
  const variance = lengths.reduce((a,b) => a + Math.pow(b-mean,2), 0) / lengths.length;
  return Math.sqrt(variance);
}

function paragraphLengthVariance(text) {
  const paras = text.split(/\n\n+/).filter(p => p.trim().split(/\s+/).length > 3);
  if (paras.length < 2) return 5;
  const lengths = paras.map(p => p.trim().split(/\s+/).length);
  const mean = lengths.reduce((a,b) => a+b, 0) / lengths.length;
  const variance = lengths.reduce((a,b) => a + Math.pow(b-mean,2), 0) / lengths.length;
  return Math.sqrt(variance);
}
```

**New AI score formula:**
```js
const aiScore = Math.min(100, Math.round(
  patterns.formulaicConnectors * 15 +
  patterns.nominalisationRatio * 150 +
  patterns.passiveVoiceDensity * 40 +
  Math.max(0, 8 - patterns.sentenceLengthStddev) * 4 +
  Math.max(0, 15 - patterns.paragraphLengthStddev) * 2
));
```

**Acceptance criteria:**
- `grep -c "passiveVoiceDensity\|sentenceLengthVariance\|paragraphLengthVariance" ai-humaniser-pro.jsx` returns ≥ 3

**Results:** [EMPTY]

---

## Step 2 — Improve Python burstiness metric

**What:** Update `_burstiness_score()` in `pattern_detector.py` to return a proper coefficient-of-variation (CV = stddev/mean) which normalises for paragraph length. Currently returns raw stddev which is not comparable across documents of different sentence lengths. Also add `passive_voice_density` to the `detect_patterns()` output.

**New burstiness:**
```python
def _burstiness_score(text: str) -> float:
    """Coefficient of variation of sentence lengths. Lower = more uniform = more AI."""
    nlp = _get_nlp()
    try:
        doc = nlp(text[:_SPACY_CHAR_LIMIT])
        lengths = [len(list(s)) for s in doc.sents if len(list(s)) > 1]
    except Exception as exc:
        _LOG.warning("[_burstiness_score] spaCy failed: %s — falling back", exc)
        lengths = [len(s.split()) for s in text.split(". ") if s.strip()]
    if len(lengths) < 2:
        return 0.0
    mean = statistics.mean(lengths)
    if mean == 0:
        return 0.0
    return round(statistics.stdev(lengths) / mean, 3)  # coefficient of variation
```

**New passive_voice_density:**
```python
def _passive_voice_density(text: str) -> float:
    """Fraction of sentences containing passive voice constructions."""
    import re
    sentences = [s.strip() for s in re.split(r'[.!?]+', text) if len(s.strip().split()) > 3]
    if not sentences:
        return 0.0
    passive_re = re.compile(r'\b(is|are|was|were|been|being)\s+\w+ed\b', re.IGNORECASE)
    passive = sum(1 for s in sentences if passive_re.search(s))
    return round(passive / len(sentences), 3)
```

**Acceptance criteria:**
- `python3 -c "from pattern_detector import detect_patterns; r=detect_patterns('The risk assessment was conducted. Verification was performed. Implementation was completed.'); print(r['pattern_counts']['passive_voice_density']); assert r['pattern_counts']['passive_voice_density'] > 0"` exits 0

**Results:** [EMPTY]

---

## Step 3 — Update browser tool in Hub

**What:** Copy the improved `ai-humaniser-pro.jsx` to the heidi-qms-tools subdirectory and push.

**Acceptance criteria:**
- `diff /Users/sharky/Desktop/Heidi/qms-tools/ai-humaniser-pro/ai-humaniser-pro.jsx /Users/sharky/Desktop/Heidi/qms-tools/heidi-qms-tools/ai-humaniser-pro/ai-humaniser-pro.jsx` shows differences (new functions present)

**Results:** [EMPTY]

---

## Step 4 — Test on 5 documents

**What:** Run `run_pipeline_v2()` on 5 different documents from the Working Docs folder. For each: print before/after perplexity, structural score, known-new violations, and protected terms check. Save results to `test-results-2026-06-22.txt`.

**Documents to test:**
1. test-chatgpt-rapamycin.txt (confirmed AI text)
2. Working Docs/Risk/RMR-ISD-Evidence-Risk-Management-Report_v1.docx
3. Working Docs/Risk/Rubrics/Evidence_Risk_Reduction_Factor_WI_v0.1.docx
4. Working Docs/Risk/Rubrics/P1_P2_Probability_Estimation_WI_v0.4.docx
5. Working Docs/Risk/RMP-ISD-AI Scribe and Evidence Risk Management Plan.docx

**Acceptance criteria:**
- At least 3 of 5 documents show improvement in either perplexity OR structural score
- Zero protected terms dropped across all 5
- `ls test-results-2026-06-22.txt` exits 0

**Results:** [EMPTY]

---

## Step 5 — Commit + push all improvements

**What:** Commit and push all changes to both repos (ai-humaniser-pro + heidi-qms-tools).

**Acceptance criteria:**
- `git -C /Users/sharky/Desktop/Heidi/qms-tools/ai-humaniser-pro log --oneline -1` shows new commit
- `git -C /Users/sharky/Desktop/Heidi/qms-tools/heidi-qms-tools log --oneline -1` shows new commit

**Results:** [EMPTY]

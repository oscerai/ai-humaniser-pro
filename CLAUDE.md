# AI Humaniser Pro — CLAUDE.md

## What this tool does

Takes formal regulatory text (EU MDR, ISO 14971, IEC 62304) and humanises it to sound
less AI-written. V2 uses DistilGPT-2 perplexity scoring (works on Claude-era text) and
Claude API targeted rewriting against 9 specific Claude writing patterns, without touching
protected regulatory terms.

## V2 Entry points (current)

### run_pipeline_v2(text, intensity_threshold=2) → str

Main humanisation function. Detects Claude writing patterns per paragraph, rewrites flagged
paragraphs via Claude API (Haiku, Heidi proxy), protects all regulatory terms.

```python
from pipeline_v2 import run_pipeline_v2
result = run_pipeline_v2(open("my-doc.txt").read())
print(result)
```

### score_document_v2(text) → dict

Scores a document for AI-ness using DistilGPT-2 perplexity. Higher perplexity = more human.

```python
from scorer_v2 import score_document_v2
print(score_document_v2(open("my-doc.txt").read()))
# {'perplexity': 49.3, 'structural_score': 0.857}
```

### detect_patterns(text) → dict

Detects 9 Claude writing patterns and returns pattern counts + flagged paragraph indices.

```python
from pattern_detector import detect_patterns
print(detect_patterns(open("my-doc.txt").read()))
```

### score_document(text) → dict

Scores a document for humanness. Returns:

- hc3_ai_probability: float 0-1 (0=human, 1=AI) from HC3 Detector
- structural_score: float 0-1 (fraction of paragraph pairs that are reorderable = additive structure)

```python
from scorer import score_document
print(score_document(open("my-doc.txt").read()))
```

### check_known_new(paragraphs) → list[dict]

Analyses paragraph pairs for known-new contract violations. Returns list of dicts with:

- pair_index: int
- p_n_ending_concept: str (last noun chunk of paragraph N)
- p_n1_opening_concept: str (first noun chunk of paragraph N+1)
- reorderable: bool (True = no known-new dependency = additive structure = AI tell)

```python
from known_new_contract_checker import check_known_new
paras = open("my-doc.txt").read().split("\n\n")
for pair in check_known_new(paras):
    if pair["reorderable"]:
        print(f"Additive pair at {pair['pair_index']}: '{pair['p_n_ending_concept']}' -> '{pair['p_n1_opening_concept']}'")
```

## Protected terms

Location: `profiles/regulatory.py` -> `PROTECTED_TERMS` list (90+ entries including inflected forms)
These terms are NEVER modified by any stage of the pipeline. If a TextHumanize stage drops
a protected term, that paragraph is reverted to its original.

## HC3 Model

First run downloads Hello-SimpleAI/chatgpt-detector-roberta (~360MB) from HuggingFace.
Internet required for initial download. Cached locally after first use. Runs on CPU (MPS on Mac).

## Test

```bash
cd /Users/sharky/Desktop/Heidi/qms-tools/ai-humaniser-pro
python3 -c "
from pipeline import run_pipeline
from scorer import score_document
txt = open('../ai-humaniser/test-doc.txt').read()
before = score_document(txt)
result = run_pipeline(txt)
after = score_document(result)
print(f'HC3 before: {before[\"hc3_ai_probability\"]:.3f}')
print(f'HC3 after:  {after[\"hc3_ai_probability\"]:.3f}')
print(f'Improved:   {after[\"hc3_ai_probability\"] < before[\"hc3_ai_probability\"]}')
"
```

## Future integration

This tool is designed to become a tab in the QMS Tools dashboard at
https://oscerai.github.io/heidi-qms-tools/ — keep module boundaries clean.

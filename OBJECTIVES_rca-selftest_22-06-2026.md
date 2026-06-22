OVERARCHING GOAL: Understand why the known-new fixer hallucinated, decide whether it can be fixed, and add two safety layers to the pipeline — a meaning-change checker that reverts rewrites that alter factual content, and a regulatory document classifier that applies conservative settings automatically — so the AI Humaniser Pro can be trusted on real regulated documents.

OBJECTIVES:

1. Root cause analysis complete: 3+ prompt variants for the known-new fixer tested on real regulatory text extracted from the Evidence Risk Management Report, with hallucination rate measured per variant, saved to rca-results-2026-06-22.txt.
   VERIFY: grep -c "Variant" /Users/sharky/Desktop/Heidi/qms-tools/ai-humaniser-pro/rca-results-2026-06-22.txt

2. Decision documented: known_new_fixer_decision.md exists with a VERDICT line (FIXABLE or KEEP DISABLED) backed by the RCA measurements.
   VERIFY: grep -E "^VERDICT:" /Users/sharky/Desktop/Heidi/qms-tools/ai-humaniser-pro/known_new_fixer_decision.md

3. meaning_checker.py exists with check_meaning_preserved(original, rewritten) returning a dict with a 'preserved' boolean key. Identical text returns preserved=True.
   VERIFY: cd /Users/sharky/Desktop/Heidi/qms-tools/ai-humaniser-pro && python3 -c "from meaning_checker import check_meaning_preserved; r=check_meaning_preserved('The risk assessment was conducted per ISO 13485.', 'The risk assessment was conducted per ISO 13485.'); assert r['preserved']==True, r; print('PASS')"

4. meaning_checker.py is wired into pipeline_v2.py: run_pipeline_v2() accepts a check_meaning parameter and reverts any rewritten paragraph where check_meaning_preserved returns preserved=False.
   VERIFY: grep -n "check_meaning\|meaning_checker" /Users/sharky/Desktop/Heidi/qms-tools/ai-humaniser-pro/pipeline_v2.py

5. regulatory_classifier.py exists with is_regulated_document(text) returning True for text containing regulated-document keywords (ISO, EU MDR, IEC 62304, shall, risk management plan, notified body) and False for general text.
   VERIFY: cd /Users/sharky/Desktop/Heidi/qms-tools/ai-humaniser-pro && python3 -c "from regulatory_classifier import is_regulated_document; assert is_regulated_document('This product shall comply with ISO 13485 and EU MDR Annex I.') == True; assert is_regulated_document('Today I went to the market and bought some apples.') == False; print('PASS')"

6. regulatory_classifier.py is wired into pipeline_v2.py: run_pipeline_v2() calls is_regulated_document() at start and applies intensity_threshold=3 plus check_meaning=True automatically when the input is a regulated document.
   VERIFY: grep -n "is_regulated_document\|regulatory_classifier" /Users/sharky/Desktop/Heidi/qms-tools/ai-humaniser-pro/pipeline_v2.py

7. Unit tests for meaning_checker.py and regulatory_classifier.py exist and pass alongside the existing test suite.
   VERIFY: cd /Users/sharky/Desktop/Heidi/qms-tools/ai-humaniser-pro && python3 -m pytest tests/test_humaniser_pro.py tests/test_meaning_checker.py tests/test_regulatory_classifier.py -q 2>&1 | tail -3

8. Full pipeline run on text extracted from the Evidence Risk Management Report completes without error and produces output with the same paragraph count as input (no paragraphs dropped or merged).
   VERIFY: cd /Users/sharky/Desktop/Heidi/qms-tools/ai-humaniser-pro && python3 -c "from pipeline_v2 import run_pipeline_v2; txt=open('test-regulatory-extract.txt').read(); r=run_pipeline_v2(txt); pin=len([p for p in txt.split(chr(10)*2) if p.strip()]); pout=len([p for p in r.split(chr(10)*2) if p.strip()]); print(f'in:{pin} out:{pout}'); assert pin==pout"

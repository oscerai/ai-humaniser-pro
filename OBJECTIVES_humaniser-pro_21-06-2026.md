OVERARCHING GOAL: Build a working AI Humaniser Pro tool that takes formal regulatory text and makes it read as if a professional human wrote it, without touching protected regulatory terms, using the TextHumanize fork as a base with known-new contract analysis and a reliable humanness scorer.

OBJECTIVES:

1. The TextHumanize fork runs on the test document and makes at least 3 observable text changes without touching any of the 68 protected terms.
   VERIFY: cd /Users/sharky/Desktop/Heidi/qms-tools/ai-humaniser-pro && python3 -c "from profiles.regulatory import PROTECTED_TERMS; from texthumanize import humanize; txt=open('../ai-humaniser/test-doc.txt').read(); paras=[p.strip() for p in txt.split('\n\n') if p.strip()]; results=[str(humanize(p,profile='formal',intensity=20).text) if hasattr(humanize(p,profile='formal',intensity=20),'text') else str(humanize(p,profile='formal',intensity=20)) for p in paras]; result='\n\n'.join(results); changed=sum(1 for a,b in zip(txt.split(),result.split()) if a!=b); violated=[t for t in PROTECTED_TERMS if t.lower() in txt.lower() and t.lower() not in result.lower()]; print('changes:',changed,'protected_dropped:',len(violated)); assert changed>=3,f'only {changed} changes'; assert len(violated)==0,f'dropped: {violated}'"

2. The HC3 Detector is installed and returns a numeric AI-probability score (0-1) for any text string input.
   VERIFY: cd /Users/sharky/Desktop/Heidi/qms-tools/ai-humaniser-pro && python3 -c "from transformers import pipeline; p=pipeline('text-classification',model='Hello-SimpleAI/chatgpt-detector-roberta'); r=p('The implementation of risk management requires demonstration of compliance.'); print('label:',r[0]['label'],'score:',round(r[0]['score'],3)); assert 0<=r[0]['score']<=1"

3. A score_document() function exists in scorer.py that returns a dict with at minimum hc3_ai_probability and structural_score keys, both floats.
   VERIFY: cd /Users/sharky/Desktop/Heidi/qms-tools/ai-humaniser-pro && python3 -c "from scorer import score_document; r=score_document('The implementation of risk management requires the demonstration of compliance.'); print(r); assert 'hc3_ai_probability' in r and 'structural_score' in r and isinstance(r['hc3_ai_probability'],float) and isinstance(r['structural_score'],float)"

4. A known_new_contract_checker.py module exists that takes a list of paragraphs and returns a list of dicts identifying paragraph pairs where P(N+1) does not echo the ending concept of P(N).
   VERIFY: cd /Users/sharky/Desktop/Heidi/qms-tools/ai-humaniser-pro && python3 -c "from known_new_contract_checker import check_known_new; r=check_known_new(['The risk is high. This matters for safety.','Furthermore the device must demonstrate compliance. This is required.']); print(r); assert isinstance(r,list) and all('pair' in x or 'reorderable' in x for x in r)"

5. Running run_pipeline() on test-doc.txt produces output that scores lower on hc3_ai_probability than the original.
   VERIFY: cd /Users/sharky/Desktop/Heidi/qms-tools/ai-humaniser-pro && python3 -c "from pipeline import run_pipeline; from scorer import score_document; orig=open('../ai-humaniser/test-doc.txt').read(); result=run_pipeline(orig); sb=score_document(orig)['hc3_ai_probability']; sa=score_document(result)['hc3_ai_probability']; print(f'before:{sb:.3f} after:{sa:.3f} improved:{sa<sb}'); assert sa<sb,f'no improvement: {sb:.3f}->{sa:.3f}'"

6. A CLAUDE.md exists at the project root documenting entry points, protected-terms location, and how to run the tool.
   VERIFY: ls /Users/sharky/Desktop/Heidi/qms-tools/ai-humaniser-pro/CLAUDE.md && grep -c "run_pipeline\|protected_terms\|score_document" /Users/sharky/Desktop/Heidi/qms-tools/ai-humaniser-pro/CLAUDE.md

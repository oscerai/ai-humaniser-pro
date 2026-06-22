OVERARCHING GOAL: Make run_pipeline_v2() produce documents with measurably fewer additive paragraph pairs by building a known-new contract fixer module that rewrites paragraph N+1 openings to chain logically from paragraph N's ending concept, so regulatory documents flow as connected arguments rather than disconnected lists.

OBJECTIVES:

1. known_new_fixer.py exists at project root with fix_known_new(paragraphs) returning a list of strings the same length as input, where reorderable pairs have been rewritten to open with a reference to the previous paragraph's ending concept.
   VERIFY: cd /Users/sharky/Desktop/Heidi/qms-tools/ai-humaniser-pro && python3 -c "from known_new_fixer import fix_known_new; r=fix_known_new(['The risk assessment identified three hazards.','Furthermore compliance must be demonstrated.']); print(r); assert isinstance(r,list) and len(r)==2 and isinstance(r[0],str) and isinstance(r[1],str)"

2. pipeline_v2.py updated: run_pipeline_v2() calls \_apply_known_new_fix() after the pattern-detect and rewrite pass, confirmed by grep showing the function name in the file.
   VERIFY: grep -n "\_apply_known_new_fix\|known_new_fixer" /Users/sharky/Desktop/Heidi/qms-tools/ai-humaniser-pro/pipeline_v2.py

3. fix_known_new() never drops a protected regulatory term — any rewrite that would drop a term reverts to the original paragraph.
   VERIFY: cd /Users/sharky/Desktop/Heidi/qms-tools/ai-humaniser-pro && python3 -c "from known_new_fixer import fix_known_new; from profiles.regulatory import PROTECTED_TERMS; paras=['Risk management shall demonstrate compliance. Verification is required.','Additionally the implementation of safety measures must be validated.']; result=fix_known_new(paras); dropped=[t for t in PROTECTED_TERMS if t.lower() in ' '.join(paras).lower() and t.lower() not in ' '.join(result).lower()]; print('dropped:',dropped); assert len(dropped)==0"

4. All functions in known_new_fixer.py and the updated pipeline_v2.py are 40 lines or fewer.
   VERIFY: cd /Users/sharky/Desktop/Heidi/qms-tools/ai-humaniser-pro && for f in known_new_fixer.py pipeline_v2.py; do awk '/^def /{if(s)print c,FILENAME,s; s=$0; c=0} {c++} END{if(s)print c,FILENAME,s}' $f | awk '$1>40{print "VIOLATION:",$0}'; done && echo "NASA PASS"

5. Running run_pipeline_v2() on test-chatgpt-rapamycin.txt produces output with structural_score lower than the input (fewer reorderable paragraph pairs after the known-new fix pass).
   VERIFY: cd /Users/sharky/Desktop/Heidi/qms-tools/ai-humaniser-pro && python3 -c "from pipeline_v2 import run_pipeline_v2; from scorer_v2 import score_document_v2; txt=open('test-chatgpt-rapamycin.txt').read(); before=score_document_v2(txt)['structural_score']; result=run_pipeline_v2(txt); after=score_document_v2(result)['structural_score']; print(f'structural before:{before:.3f} after:{after:.3f} improved:{after<before}'); assert after<before"

6. /code-quality is run as the final plan step, chaining to /deep-qa and then /code-review, covering known_new_fixer.py and the updated pipeline_v2.py.
   VERIFY: grep -c "code.quality\|deep.qa\|code.review" /Users/sharky/Desktop/Heidi/qms-tools/ai-humaniser-pro/plans/PLAN_KNOWN_NEW_FIXER_BUILD.md

# Bugs and Lessons — AI Humaniser Pro

[2026-06-21] HC3 model labels are "Human"/"ChatGPT" not "Real"/"Fake" → plan assumed wrong label names → scorer.py written with correct "ChatGPT" label from the start

[2026-06-21] texthumanize profile='formal' does not automatically apply keep_keywords → protected terms were being dropped by raw humanize() calls → added \_patch_formal_profile() monkey-patch in profiles/regulatory.py that injects PROTECTED_TERMS as keep_keywords when profile='formal' is used; pipeline.py also has a revert-on-drop safety net

[2026-06-21] PyTorch was not installed alongside transformers → HC3 model pipeline() fails with NameError("name 'torch' is not defined") → must install torch separately (pip3 install torch) in addition to transformers

[2026-06-21] HC3 (trained on 2022 GPT-3.5) scores Claude-generated regulatory text as 0.000 — useless for detecting modern LLM output → replaced with DistilGPT-2 perplexity scoring in scorer_v2.py which correctly detects Claude-era text (lower perplexity = more AI-predictable)

[2026-06-21] TextHumanize word-swapping cannot fix structural Claude writing patterns (formulaic connectors, nominalisation, known-new contract violations, sentence rhythm) → replaced with Claude API (Haiku, Heidi proxy) targeted rewriting in rewriter.py — pipeline_v2.py orchestrates detect→rewrite→verify

[2026-06-21] Risk management documents had zero formulaic connectors before humanisation — these documents already avoid surface-level AI tells; the subtler patterns (sentence rhythm, abstraction level, paragraph shape uniformity) are harder to detect automatically and require more sophisticated analysis

[2026-06-21] ChatGPT-era document (rapamycin paper) perplexity improved 9.1→13.1 (44%) after pipeline_v2 — confirms the detect+rewrite architecture works on clear AI text; improvement on regulatory documents is subtler because they already have partially elevated perplexity due to domain-specific language

[2026-06-21] code-quality Rule B2 — \_burstiness_score had silent except with no log on spaCy fallback → added \_LOG.warning before fallback to simple sentence split
[2026-06-21] code-quality Rule A6 — static system prompt in rewriter.py sent as plain string without cache_control → changed to content block array with cache_control: {type: ephemeral}
[2026-06-21] code-quality Rule B6 — magic numbers 512, 1024, 30, 5000 were bare literals in function bodies → extracted to named module constants \_MAX_TOKEN_LENGTH, \_MAX_TOKENS, \_PROXY_TIMEOUT_SEC, \_SPACY_CHAR_LIMIT

[2026-06-21] code-review: import torch outside try block in \_compute_perplexity → missing torch raises ModuleNotFoundError before try is entered, bypassing 50.0 fallback → moved import inside try + added \_MODEL_LOAD_FAILED sentinel to prevent retry storms on persistent failures

[2026-06-21] code-review: score_document_v2 and detect_patterns split on "\n\n" without normalising \r\n → Windows-format files treated as single paragraph, producing wrong before/after scoring comparison → added .replace("\r\n", "\n") to both functions (pipeline_v2 already had this)

[2026-06-21] code-review: \_flag_paragraphs hardcoded threshold=2 while run_pipeline_v2 accepts configurable intensity_threshold → detect_patterns diagnostic output disagreed with what pipeline actually rewrote at non-default thresholds → threaded threshold parameter through \_flag_paragraphs and detect_patterns

[2026-06-21] code-review: cache_control PLAUSIBLE finding refuted in production — Anthropic API accepts cache_control without anthropic-beta header (made GA, no longer requires beta header); \_call_proxy confirmed working with cache_control content block format

[2026-06-21] known_new_fixer: structural_score INCREASED (0.857→1.000) when LLM used generic connective phrases (e.g. 'In light of these benefits') instead of the exact ending noun chunk — the spaCy lemma matcher could not detect the connection → fixed by extracting the exact ending_concept via check_known_new and passing it explicitly to the LLM prompt as the concept to echo verbatim; structural_score then improved to 0.429

[2026-06-21] deep-qa: fix_known_new passed empty ending_concept to LLM when \_last_noun_chunk returns "" for punctuation-only paragraphs → added 'if not ending: continue' guard to skip pairs with empty ending concept rather than sending a meaningless prompt

[2026-06-21] code-review: fix_known_new used pair_index from check_known_new as a direct index into result[] — but pair_index indexes into valid[] (paragraphs with ≥4 words), not paragraphs[] — when short paragraphs exist, the wrong paragraphs were silently rewritten → fixed by building valid_idxs mapping and using n_idx=valid_idxs[vi], n1_idx=valid_idxs[vi+1] to index result[] correctly

[2026-06-21] code-review: ImportError branch in \_apply_known_new_fix didn't bind exc, so the log message couldn't show which module failed → added 'as exc' and %s to the warning

[2026-06-21] code-quality Stream 1: get_regulatory_options in profiles/regulatory.py was 50 lines (NASA Rule 4 violation) — long docstring + two large inline dicts → extracted \_REGULATORY_PRESERVE and \_REGULATORY_CONSTRAINTS as named module-level constants; function now 15 lines. known_new_contract_checker.py was clean.

[2026-06-22] improvements: burstiness_score changed from raw stddev to coefficient of variation (stddev/mean) so scores are comparable across documents of different sentence lengths; added passive_voice_density to pattern_detector; added 5-factor AI scoring to browser tool (connectors, nominalisations, passive voice, sentence uniformity, paragraph uniformity); 5/5 test documents improved with zero protected terms dropped
[2026-06-22] code-quality: Rule B3 — PROXY_URL + PROXY_TIMEOUT_SEC + _call_proxy HTTP transport defined independently in 4 files (meaning_checker.py, rewriter.py, known_new_fixer.py, rca_test.py) → root cause: no shared proxy client module existed → created proxy_client.py as single source of truth; all 4 callers updated to import from it
[2026-06-22] passive_voice_density added to pattern_detector detect_patterns() output in a prior session but never wired into _count_signals() in pipeline_v2.py — documents whose primary AI tell is passive voice (not formulaic connectors) scored max 1 signal, below threshold=2, producing identical before/after scores → added passive voice as 4th signal with 0.2 per-paragraph threshold; AI Scribe RMR improved from 34.1→36.7 perplexity, 16 paragraphs rewritten, 3 hallucinations caught and reverted by meaning checker
[2026-06-22] regulatory classifier set intensity_threshold=max(threshold,3) — this was wrong: with 0 formulaic connectors, max score is 2 and nothing gets rewritten; "conservative" for regulated docs should mean meaning-checking is stricter, not that the tool refuses to act → removed threshold override; apply_known_new=False and check_meaning=True remain as the real safety mechanism
[2026-06-22] code-review: _flag_paragraphs checked 3 signals; _count_signals checked 4 (passive voice added but not mirrored) — diagnostic API and pipeline disagreed on flagged paragraphs → added passive voice check to _flag_paragraphs to match _count_signals exactly
[2026-06-22] code-review: meaning_checker treated any non-PRESERVED LLM response as confirmed meaning change — no third branch for unexpected responses (refusals, rate-limit messages) caused valid rewrites to be silently reverted → added explicit CHANGED check; unexpected responses now return preserved=True with warning log

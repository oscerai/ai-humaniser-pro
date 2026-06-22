OVERARCHING GOAL: Turn the AI Humaniser Pro from a Python command-line tool into a browser-based web application that any team member can use by pasting or uploading a regulatory document, while parallelising the pipeline for speed and completing code quality coverage across all remaining modules.

OBJECTIVES:

1. /code-quality runs and completes on profiles/regulatory.py and known_new_contract_checker.py with all safe root-cause findings fixed and BUGS_AND_LESSONS.md updated.
   VERIFY: tail -5 /Users/sharky/Desktop/Heidi/qms-tools/ai-humaniser-pro/BUGS_AND_LESSONS.md | grep "code-quality.*regulatory\|code-quality.*known_new_contract"

2. pipeline_v2.py parallelised: a \_process_paragraphs_parallel() function uses ThreadPoolExecutor to process paragraphs concurrently, and run_pipeline_v2() calls it instead of the sequential loop. All existing tests still pass.
   VERIFY: cd /Users/sharky/Desktop/Heidi/qms-tools/ai-humaniser-pro && grep -n "ThreadPoolExecutor\|\_process_paragraphs_parallel" pipeline_v2.py && python3 -m pytest tests/test_humaniser_pro.py -q 2>&1 | tail -2

3. ai-humaniser-pro.jsx exists in the project root and contains: a text area for document input, JS-regex pattern detection for formulaic connectors and nominalisation ratio, a humanise button that calls the Heidi proxy paragraph-by-paragraph using the combined rewriting system prompt, before/after display of pattern counts, and a download button for the result.
   VERIFY: ls /Users/sharky/Desktop/Heidi/qms-tools/ai-humaniser-pro/ai-humaniser-pro.jsx && grep -c "PROXY_URL\|formulaic\|download\|pattern" /Users/sharky/Desktop/Heidi/qms-tools/ai-humaniser-pro/ai-humaniser-pro.jsx

4. An index.html exists that loads the JSX tool and can be opened in a browser to use the humaniser without any Python.
   VERIFY: ls /Users/sharky/Desktop/Heidi/qms-tools/ai-humaniser-pro/index.html && python3 -c "from pathlib import Path; html=Path('/Users/sharky/Desktop/Heidi/qms-tools/ai-humaniser-pro/index.html').read_text(); assert 'ai-humaniser-pro' in html"

5. The tool is deployed: the repository oscerai/ai-humaniser-pro exists on GitHub with the JSX tool and a GitHub Actions workflow that publishes to GitHub Pages. The live URL is accessible.
   VERIFY: gh repo view oscerai/ai-humaniser-pro --json name,url 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['url']); assert d['name']=='ai-humaniser-pro'"

6. /humanize skill updated to include the web tool URL so users know both the CLI and browser options.
   VERIFY: grep -c "oscerai.github.io/ai-humaniser-pro\|web tool\|browser" /Users/sharky/.claude/commands/humanize.md

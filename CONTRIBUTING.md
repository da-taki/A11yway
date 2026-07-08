# Contributing to A11yway

Thanks for helping make education pages more accessible. This project is
intentionally small and readable for student developers — please keep it
that way.

## Set up static mode

Static mode needs only Python 3.10+ and the standard library:

```bash
git clone https://github.com/da-taki/A11yway.git
cd A11yway
python -m a11yway.main examples/sample_form.html
```

## Set up browser mode (optional)

```bash
pip install -r requirements-browser.txt
python -m playwright install chromium
python -m a11yway.main examples/sample_dynamic_form.html --browser
```

Everything except `--browser` works without this step.

## Run the tests

```bash
pip install pytest
python -m pytest tests/ -q
```

The suite must pass without Playwright installed; browser integration
tests skip themselves when the browser cannot run.

## Add a new rule

1. Implement the check in `a11yway/core/page_analyzer.py` (static) or
   `a11yway/core/browser_runner.py` (browser). Keep heuristics
   conservative — false positives waste reviewer trust.
2. Register the issue type in `a11yway/core/rules.py` with title,
   category, default severity, why_it_matters, how_to_fix,
   manual_review_notes, and the appropriate limitations field.
3. Document it in `docs/RULES.md` (table row plus any notes).
4. Add tests: one page that triggers the rule, one that must not.
5. Check `python -m a11yway.main --rule your_new_type` prints it.

## Add a new sample page

- Put a small, fictional education page in `examples/`.
- No real organization names, no real student data.
- Keep it minimal: each sample should demonstrate specific issues, with
  comments explaining what is intentionally broken.
- Reference it in a batch config if it is useful for evaluation runs.

## Regenerate sample reports

After changing checks, rules, or report formats:

```bash
python -m a11yway.main examples/sample_form.html --task submit_scholarship_application --json reports/sample_form_report.json --markdown reports/sample_form_report.md
python -m a11yway.main --batch examples/sample_batch.json --out-dir reports/batch_sample
```

With Playwright installed, also:

```bash
python -m a11yway.main examples/sample_dynamic_form.html --browser --json reports/dynamic_form_report.json --markdown reports/dynamic_form_report.md
python -m a11yway.main --batch examples/sample_browser_batch.json --out-dir reports/browser_batch_sample --browser
```

Commit regenerated artifacts together with the change that caused them.
Never hand-edit generated reports.

## Coding style

- Python standard library only in core code; Playwright stays optional
  behind `a11yway/core/browser_runner.py`.
- Small functions with docstrings; descriptive names over abbreviations.
- No new external dependencies without prior discussion.
- Honest wording everywhere: findings are hints for human reviewers, not
  compliance verdicts. Avoid claiming WCAG conformance in code, docs, or
  report text.
- Tests should check key substrings and structure, not exact full wording.

# Contributing

A11yway changes should keep evidence honest and reviewable. Prefer small patches that match the existing code.

## Before editing

- Work from the latest `origin/main`.
- Keep generated reports, outreach material, screenshots, and local audit output out of commits.
- Do not add broad dependencies for narrow fixes.

## Useful checks

```bash
pytest
python -m compileall a11yway scripts
python -m a11yway.main --wcag-coverage-markdown docs/WCAG22_COVERAGE.md
```

## Rules

When adding or changing a rule, update the rule registry, WCAG mapping data, fixtures, and focused tests together. Do not claim conformance from a heuristic finding.

## Documentation

Keep docs short and factual. Do not add setup walkthroughs, marketing copy, screenshots, or repeated warnings.

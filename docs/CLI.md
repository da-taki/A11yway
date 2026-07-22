# CLI

A11yway accepts one source path or URL, or a batch file.

## Basic audit

```bash
a11yway https://example.com --json report.json
```

## Common modes

- `--browser` loads the page in Chromium and records keyboard and rendered-DOM evidence.
- `--axe` adds axe-core findings when browser mode is enabled.
- `--low-vision` checks rendered contrast, zoom, reflow, text spacing, target size, and focus visibility.
- `--forms`, `--components`, `--media`, `--language-audit`, and `--cognitive` add specialized checks.
- `--workflow --workflow-config file.json --safe-public-mode` runs permitted workflow steps without submitting public forms.
- `--passive-security` records separate passive security observations.

## Output

Use `--json`, `--markdown`, `--html`, `--csv`, `--sarif`, or `--junit` when that output fits the run. Batch mode writes an index and evaluation summary in the output directory.

## Confidence

`confirmed` and `strong` findings have stronger evidence. `likely` and `needs_review` findings still need human review. A11yway does not certify WCAG conformance.

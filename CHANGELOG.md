# Changelog

## 0.8.0b1

- Reworked the public web interface around shorter copy, sharper comic styling, and accessible form controls.
- Expanded WCAG 2.2 A and AA registry coverage and regenerated `docs/WCAG22_COVERAGE.md` from `a11yway/data/wcag22_coverage.json`.
- Added Render Docker smoke coverage for Flask, Playwright, Chromium, report downloads, browser checks, axe checks, and AI Scout fallback behavior.
- Added evidence fields for rendered browser runs, focus paths, report downloads, and confidence labels.

## Earlier work

- Added static HTML checks for names, labels, headings, language, media, tables, forms, and repeated components.
- Added optional browser checks for keyboard traversal, rendered DOM findings, accessibility-tree evidence, zoom, reflow, and text spacing.
- Added batch reports in JSON, Markdown, HTML, CSV, SARIF, and JUnit where the selected mode supports them.

The changelog is intentionally compact. Git history is the source for detailed change-by-change review.

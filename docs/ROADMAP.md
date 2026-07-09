# A11yway Roadmap

This roadmap is practical, not a promise. Priorities will shift based on feedback from accessibility reviewers, NGOs, schools, and public-interest partners.

## Current Baseline

- Static HTML checks for local files and public URLs
- Optional browser mode: keyboard focus traversal and rendered DOM re-checks in headless Chromium
- Task-based education scenarios
- Deterministic task execution for declared browser steps
- JSON / Markdown / CSV reports, batch mode, evaluation summaries
- Rule registry and documentation
- Workflow packs for public-interest accessibility testing
- Visual proof reports with screenshots, observed focus-path overlays, and HTML report export
- Low-vision browser checks for rendered contrast, reflow approximation, and focus visibility
- Reviewer verdict ingestion for confirmed, false positive, fixed, and missed issues
- Re-audit diff tracking for fixed, remaining, new, and task-execution changes
- Announce transcript from Chromium's computed accessibility tree (roles, names, states) with unnamed focus stop findings
- Keyboard trap and focus-loop detection from the observed focus trace, including trap-blocked task execution verdicts
- CI mode with meaningful exit codes, SARIF 2.1.0 and JUnit XML export, and an example GitHub Actions task regression workflow
- Real zoom reflow checks at 200% and 400% (horizontal scroll, clipped content, overlapping controls) replacing the narrow-viewport approximation

## v0.4 - Workflow Packs

- Reusable workflow packs for education, NGO, government, college, AI product, scholarship, and public-resource sites
- CLI commands to list packs, inspect one pack, and suggest deterministic task templates
- Responsible-use notes for public pages and permission-based testing

## v0.5 - Visual Proof

- Screenshots
- Focus-path overlays
- Self-contained HTML reports
- Batch HTML report support

## Future Visual Improvements

- Per-finding cropped screenshots
- Contrast and zoom/reflow checks

## v0.6 - Low-Vision Checks

- Rendered color contrast
- 200% zoom/reflow checks
- Focus visibility checks

## v0.7 - AI Scout Mode

- Optional Groq/multi-model scout
- Proposes likely workflows and risks
- Deterministic executor verifies
- AI suggestions are never treated as confirmed findings by default

## v0.8 - Reviewer Verdicts

- Confirmed
- False positive
- Missed issue
- Fixed
- Reviewer feedback dataset

## v0.9 - Re-Audit Diff

- Fixed issues
- Remaining issues
- New issues
- Verified impact over time

## Future Refinement

- Per-finding cropped screenshots
- More precise contrast sampling for gradients and image backgrounds
- Reviewer verdict dashboards
- Re-audit history across multiple runs

## Later

- PDF support for reading order, tags, alt text, and form fields
- Authenticated testing only with explicit written permission from the organization
- Screen-reader-assisted testing research: what can be honestly approximated and what cannot
- LMS-specific adapters for education platforms
- Mobile accessibility checks

## Not Planned

- Security scanning
- Private portal crawling without permission
- Automated WCAG certification
- Replacing human audits or testing with disabled users

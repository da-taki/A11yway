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

## v0.4 - Workflow Packs

- Reusable workflow packs for education, NGO, government, college, AI product, scholarship, and public-resource sites
- CLI commands to list packs, inspect one pack, and suggest deterministic task templates
- Responsible-use notes for public pages and permission-based testing

## v0.5 - Visual Proof

- Screenshots
- Focus-path overlays
- Per-finding visual evidence
- Self-contained HTML reports

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

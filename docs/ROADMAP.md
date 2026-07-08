# A11yway Roadmap

This roadmap is practical, not a promise. Priorities will shift based on
feedback from accessibility reviewers, NGOs, and schools.

## Current: v0.3

- Static HTML checks for local files and public URLs
- Optional browser mode: keyboard focus traversal and rendered DOM
  re-checks in headless Chromium
- Task-based education scenarios
- Deterministic task execution for declared browser steps
- JSON / Markdown / CSV reports, batch mode, evaluation summaries
- Rule registry and documentation
- 131 passing tests

## Near-term

- Playwright installation helper (detect missing browser, offer the exact
  commands, maybe a `--setup-browser` convenience)
- Better focus-trap detection (escape-key checks, modal cycling patterns,
  fewer heuristic gaps)
- Richer executable step types for task scenarios
- Better keyboard-only reachability checks beyond the current Tab-search
  heuristic
- Visual focus path overlays for reviewer reports
- Reviewer feedback ingestion (record confirmed/false-positive verdicts
  next to findings and learn the tool's real precision)
- Diff/re-audit mode to compare a page before and after fixes
- Public benchmark runner (repeatable batch over a published page list
  with tracked results over time)
- More sample education pages (portals, assignment lists, video lessons,
  common LMS-style markup)

## Later

- PDF support (reading order, tags, alt text, form fields)
- Authenticated testing with explicit written permission from the
  organization
- Screen-reader-assisted testing research (what can be honestly
  approximated, what cannot)
- LMS-specific adapters (Moodle, Google Classroom-style exports, and
  similar education platforms)
- Mobile accessibility checks

## Not planned yet

- Security scanning of any kind
- Crawling or testing private portals without permission
- Automated WCAG certification — the tool produces reviewer hints, not
  conformance claims
- Replacing human accessibility audits or testing with disabled users

# A11yway 0.8.0-beta.1 Release Checklist

Version: `0.8.0b1`

Display version: `0.8.0-beta.1`

## Required Gates

- [x] Record current branch, git status, recent commits, tests, WCAG coverage, capabilities, and dependency health.
- [x] Add PEP 517/518 packaging metadata.
- [x] Add one authoritative version source.
- [x] Expose `a11yway --version` and `python -m a11yway.main --version`.
- [x] Keep proprietary/native screen-reader integrations optional and capability-gated.
- [x] Keep FFmpeg out of Python dependencies.
- [x] Add optional dependency groups for browser, documents, media, development, and all runtime extras.
- [x] Add Windows/Linux GitHub Actions CI with Chromium.
- [x] Add wheel-install smoke verification outside the source checkout.
- [x] Add release tests for metadata, versioning, docs, CI, package data, and wheel import.
- [x] Run full tests.
- [x] Run branch coverage and update coverage report.
- [x] Build source distribution and wheel. Isolated build was blocked locally by sandbox network policy; no-isolation build passed.
- [x] Verify wheel in an isolated environment.
- [ ] Create four local logical commits.
- [ ] Create local annotated tag only if all release checks pass and no unintended source changes remain.

## Safety Gates

- [x] Do not push.
- [x] Do not publish to PyPI.
- [x] Do not alter WCAG mappings for better coverage numbers.
- [x] Do not require NVDA, JAWS, VoiceOver, TalkBack, ADB, or FFmpeg in CI.
- [x] Do not stage `.env`, local caches, temporary virtual environments, coverage HTML, `dist/`, or unrelated historical reports.
- [x] Passive security remains opt-in and passive-only.
- [x] Public workflow mode blocks submitting, authenticating, paying, uploading, chatting, deleting, CAPTCHA, and private actions.

## Release Verdict

- Internal testing: pending final verification.
- Public beta: pending final verification.
- Stable release: pending native-platform breadth and longer beta validation.

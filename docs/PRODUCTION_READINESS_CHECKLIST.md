# Production Readiness Checklist

Date: 2026-07-12

## Done

- [x] Recorded current dirty git state before editing.
- [x] Re-ran the full automated test suite.
- [x] Preserved the WCAG coverage map and did not inflate mappings.
- [x] Added versioned report schema metadata.
- [x] Added versioned extended-result schema metadata.
- [x] Normalized severity, confidence, review status, evidence type, and JSON evidence values.
- [x] Hardened malformed document parsing.
- [x] Hardened local media metadata parsing.
- [x] Added structured workflow safe-mode block reason codes.
- [x] Added malformed workflow config handling.
- [x] Hardened mobile context cleanup.
- [x] Added CLI `--verbose`.
- [x] Added tests for schema, parser failures, workflow safety, passive security, capabilities, CLI behavior, and module detection matrices.
- [x] Ran representative E2E commands for HTML, document, workflow, media, passive security, and public pages.
- [x] Ran `compileall`.
- [x] Ran `pip check`.
- [x] Ran `--wcag-coverage`.
- [x] Ran `--capabilities`.

## Not Done / Not Applicable Yet

- [ ] Package build: no package metadata file is present.
- [ ] Coverage report: `coverage` is not installed in the runtime.
- [ ] Firefox/WebKit validation: Playwright browser binaries are missing.
- [ ] Native screen-reader automation: no NVDA/JAWS/VoiceOver/TalkBack adapter is configured.
- [ ] FFmpeg/media decoding: FFmpeg is unavailable.
- [ ] Public-site submission workflow testing: intentionally blocked by safe mode.

## Release Gates Recommended Next

- [ ] Add `pyproject.toml` with package metadata and test/build tooling.
- [ ] Add `coverage` to development dependencies and set a realistic initial branch coverage threshold.
- [ ] Add a CI job for `pytest`, `compileall`, `pip check`, `--wcag-coverage`, and representative fixture E2E commands.
- [ ] Add optional Playwright browser-install documentation for Chromium/Firefox/WebKit validation.
- [ ] Add a reviewer workflow for false-positive triage and manual WCAG coverage notes.


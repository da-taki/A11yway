# A11yway Production Readiness Audit

Date: 2026-07-12

This audit covers the expanded A11yway modules currently present in the local repository. It is an implementation-readiness audit, not a WCAG conformance claim for A11yway or any audited site.

## Baseline

- Git state before hardening: dirty working tree with existing modified core files, existing untracked platform-expansion modules, fixtures, docs, tests, and many pre-existing reports.
- Baseline tests before this pass: 460 passed.
- Final tests after this pass: 619 passed.
- WCAG 2.2 mapping count stayed unchanged: 86 criteria total, 1 direct native, 21 partial native, 23 supporting evidence, 0 axe-only, 41 manual-only, 0 unsupported.

## Module Classification

### Production-usable with stated limitations

- `a11yway/core/extended_results.py`: Now versioned (`schema_version: 1.0`), timestamped, enum-normalized, JSON-safe, and deterministic in finding order. Suitable as the common evidence envelope for extended modules.
- `a11yway/core/report_builder.py`: Now includes `report_schema_version: 1.0`, `extended_result_schema_version: 1.0`, stable JSON key ordering on save, and deterministic extended-module ordering. Suitable for report export with the documented schema.
- `a11yway/core/forms_audit.py`: Safe markup-only form and error-recovery evidence. It intentionally blocks public submissions unless explicitly permitted.
- `a11yway/core/cognitive_audit.py`: Heuristic cognitive-accessibility review evidence. Findings are review points, not automatic conformance failures.
- `a11yway/core/language_audit.py`: Conservative script-based language and bidi evidence. Suitable for flagging sustained script/language mismatches for manual review.
- `a11yway/core/component_audit.py`: Static ARIA/component pattern evidence. Suitable for triage; browser/workflow testing is still required for real keyboard behavior.
- `a11yway/core/passive_security_audit.py`: Passive-only observations from supplied HTML/metadata. Tests now assert no network activity or active security testing.
- `a11yway/core/document_audit.py`: PDF/DOCX/PPTX metadata and structure evidence. Parser failures now produce reportable findings instead of tracebacks.
- `a11yway/core/media_audit.py`: HTML media evidence and optional local metadata evidence. Missing optional `mutagen` degrades to `unavailable`; metadata reader exceptions report cleanly.
- `a11yway/core/workflow_audit.py`: Safe structured workflow runner. Public safe mode now has reason codes for blocked actions, external domains, unsupported actions, malformed configs, and submission-like flows.
- `a11yway/core/mobile_audit.py`: Playwright mobile emulation evidence. Browser contexts now close defensively per orientation; failures are reportable per orientation.
- `a11yway/core/capabilities.py`: Capability detection is safe and degradable. Chromium verified in this environment; Firefox/WebKit/native screen readers/ADB/FFmpeg unavailable.
- `a11yway/core/wcag_coverage.py`: Stable coverage map. No mappings were inflated in this pass.
- `a11yway/core/dedup.py`: Existing deduplication remains covered by tests for stable fingerprints, confidence upgrades, and source merging.
- `a11yway/core/html_module_utils.py`: Lightweight HTML parsing helpers used by extended modules; covered indirectly by module matrices.

### Prototype or scaffolded

- Native screen-reader adapters (`nvda`, `jaws`, `voiceover`, `talkback`) remain adapter scaffolds unless a safe local integration is configured.
- Mobile checks are Playwright emulation, not real TalkBack or VoiceOver testing.
- Local media deep inspection is limited while `mutagen` and FFmpeg are unavailable.
- Packaging build is not applicable until package metadata is added (`pyproject.toml`, `setup.py`, or `setup.cfg`).
- Coverage measurement is not available in this runtime because the `coverage` package is not installed.

### Explicitly unsupported or blocked by design

- Public-site form submission, account creation, login, payment, upload, support chat, CAPTCHA, destructive actions, and private workflows.
- Penetration testing, fuzzing, exploit validation, authentication bypass, credential entry, or active security probing.
- WCAG conformance certification.
- Inflating WCAG mappings beyond actual evidence coverage.

## Issues Fixed In This Pass

- Added extended-result schema versioning, timestamps, enum normalization, JSON-safe evidence, validation, and stable finding ordering.
- Added report-level schema version fields and stable JSON key ordering.
- Converted malformed PDF/DOCX/PPTX and local-media reader failures into clean report findings.
- Added workflow safe-mode reason codes and external-domain blocking.
- Added malformed workflow config handling.
- Ensured mobile browser contexts close even when page creation/navigation/evaluation fails.
- Added `--verbose` for setup/mode diagnostics without changing normal CLI behavior.
- Expanded tests from 460 to 619, including schema, workflow safety, passive security, parser failure, capability, CLI, and broad extended-module matrices.

## Remaining Risks

- Browser-based checks depend on installed Playwright browsers. Chromium is available; Firefox and WebKit are not installed in this environment.
- Heuristic checks can still produce false positives and require reviewer confirmation.
- Static HTML parsing is intentionally lightweight and does not replace a full rendered DOM analysis.
- Public pages may block fetches; `https://www.ssa.gov/accessibility/` returned HTTP 403 during validation.
- Package build and coverage reporting need dependency/tooling work before release automation can enforce them.


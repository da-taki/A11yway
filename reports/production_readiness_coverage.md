# Production Readiness Coverage Summary

Date: 2026-07-12

## Automated Tests

- Baseline before release packaging: 619 passed.
- Final suite after release packaging and coverage hardening: 639 passed in 96.74 seconds without coverage and 118.31 seconds under branch coverage.

## Total Coverage

- Total statement coverage: 81%
- Total branch coverage: 74%
- Combined coverage display: 79%
- Covered lines: 4432 of 5486
- Covered branches: 1650 of 2222
- Excluded lines: 0

Coverage was measured with:

```powershell
python -m coverage erase
python -m coverage run --branch -m pytest
python -m coverage report -m
python -m coverage json -o reports/coverage.json
python -m coverage html -d reports/coverage_html
```

## Required Module Coverage

| Module | Combined | Statements | Branches | Notes |
| --- | ---: | ---: | ---: | --- |
| `capabilities.py` | 76% | 79% | 67% | Optional executable and browser launch error branches remain partly uncovered. |
| `extended_results.py` | 100% | 100% | 100% | Meets serialization target. |
| `screen_reader_audit.py` | 88% | 91% | 79% | Native adapter scaffolds remain capability-gated. |
| `mobile_audit.py` | 91% | 95% | 78% | Mocked Playwright tests cover success and orientation-failure cleanup. |
| `document_audit.py` | 61% | 65% | 52% | Lower because many optional parser/library and URL-fetch branches are not fully exercised. |
| `media_audit.py` | 81% | 82% | 79% | Metadata library unavailable/error branches are covered; deeper media parsing remains limited. |
| `workflow_audit.py` | 98% | 98% | 98% | Meets safe-mode target. |
| `forms_audit.py` | 100% | 100% | 100% | Meets target. |
| `cognitive_audit.py` | 100% | 100% | 100% | Meets target. |
| `language_audit.py` | 100% | 100% | 100% | Meets target. |
| `component_audit.py` | 98% | 100% | 95% | Meets target. |
| `passive_security_audit.py` | 98% | 100% | 96% | Meets passive request-isolation target. |
| `report_builder.py` | 86% | 89% | 79% | Export variants and uncommon report sections leave branch gaps. |
| `main.py` | 65% | 67% | 60% | CLI mode combinations and error exits are broad; high-risk paths have focused tests. |

## Safety-Critical Coverage

- Workflow safe-mode blocking: 98% module coverage.
- Passive-security request isolation: 98% module coverage.
- Extended result serialization: 100% module coverage.
- Mobile resource cleanup: success and failure paths covered with mocked Playwright contexts.
- Malformed workflow config handling: covered.
- Malformed document/media parser failure handling: covered.
- Report schema/version consistency: covered.
- Installed wheel import and console entry point: covered.

## High-Risk Uncovered Branches

- `document_audit.py`: optional parser import failures, successful URL document fetch recursion, and several PDF/DOCX/PPTX metadata edge branches remain partly uncovered.
- `capabilities.py`: subprocess/device probing and browser launch exception branches remain partly uncovered.
- `main.py`: many CLI combinations, batch/verdict/diff modes, and setup-error exits remain uncovered by branch coverage.
- `browser_runner.py`, `task_executor.py`, and `low_vision_audit.py`: real browser paths are partly covered but still have lower branch coverage due Playwright state combinations, video, and failure branches.
- `web_app.py`: web demo request branches are outside the release-critical CLI path and remain at 62% combined coverage.

No broad exclusions were added to hide these gaps. Adapter scaffolds and optional integrations are excluded only from stable release claims, not from coverage measurement.

## WCAG Mapping Snapshot

- Total WCAG 2.2 Success Criteria: 86
- Direct native coverage: 1
- Partial native coverage: 21
- Supporting evidence only: 23
- Axe-core only: 0
- Manual review only: 41
- Unsupported: 0

This is tool evidence coverage only. It is not a WCAG conformance claim.

## Capability Snapshot

- Chromium: available and verified.
- Playwright package: importable.
- Firefox: unavailable, browser binary missing.
- WebKit: unavailable, browser binary missing.
- NVDA: unavailable.
- JAWS: unavailable.
- VoiceOver: unsupported on current platform.
- TalkBack/ADB: unavailable.
- PDF libraries: available and verified.
- Office document libraries: available and verified.
- FFmpeg: unavailable.
- `mutagen`: installed during release extra verification.
- `coverage`: installed for release verification.
- `build`: installed for release verification.

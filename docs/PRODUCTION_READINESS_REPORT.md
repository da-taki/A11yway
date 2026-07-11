# Production Readiness Report

Date: 2026-07-12

Release target: A11yway `0.8.0-beta.1` (`0.8.0b1`)

## Verdict

- Internal testing: ready.
- Public beta: ready.
- Stable release: pending native-platform breadth, higher coverage for document/browser/task-execution edge branches, and longer beta validation.

A11yway is ready for public beta as a safe, passive/static accessibility evidence tool with optional Chromium-backed evidence. It is not a WCAG conformance engine, native screen-reader automation suite, real mobile AT lab, stable release, or active security testing tool.

## Final Verification

| Check | Result |
| --- | --- |
| Baseline `pytest -q` before release packaging | 619 passed in 86.59 seconds |
| Final `pytest -q` after release packaging | 639 passed in 96.74 seconds |
| Final coverage run | 639 passed in 118.31 seconds |
| `compileall a11yway tests` | Passed |
| `pip check` | Passed, no broken requirements |
| `python -m build` | Blocked by sandboxed isolated build dependency download; rerun with approval was rejected by app usage limit |
| `python -m build --no-isolation` | Passed; built `a11yway-0.8.0b1.tar.gz` and `a11yway-0.8.0b1-py3-none-any.whl` |
| Isolated wheel install | Passed from temporary venv outside source checkout |
| `python -m a11yway.main --version` | `a11yway 0.8.0b1` |
| Console `a11yway --version` | `a11yway 0.8.0b1` |
| `--wcag-coverage` | Passed; mapping counts unchanged |
| `--capabilities` | Passed; Chromium verified, unavailable adapters reported cleanly |

## Coverage

- Total statement coverage: 81%
- Total branch coverage: 74%
- Combined coverage display: 79%

High-risk targets:

- Workflow safe-mode blocking: 98%
- Passive-security request isolation: 98%
- Extended result serialization: 100%
- Mobile emulation module: 91%

Lower-coverage areas are documented in `reports/production_readiness_coverage.md`.

## Packaging

Added `pyproject.toml` with:

- PEP 517/518 setuptools backend.
- Dynamic version from `a11yway.__version__`.
- Package name `a11yway`.
- Console script `a11yway = a11yway.main:main`.
- Python requirement `>=3.10`.
- Project URLs from the repository metadata already present in the codebase.
- Package data for workflow packs and web demo templates/static assets.

No license or author metadata was invented because the repository does not currently declare those fields.

Optional dependency groups:

- `browser`
- `documents`
- `media`
- `ai`
- `web`
- `development`
- `all`

Core installation does not require proprietary screen readers, ADB, or FFmpeg.

## WCAG Coverage

No WCAG mapping inflation was performed.

- Direct native: 1
- Partial native: 21
- Supporting evidence: 23
- Axe-only: 0
- Manual-only: 41
- Unsupported: 0

A11yway provides native direct, partial, or supporting evidence related to 45 of the 86 WCAG 2.2 Success Criteria. This is not a conformance claim.

## Release Tests Added

- Version consistency and CLI `--version`.
- Package metadata and optional dependency groups.
- Report/schema version consistency.
- Required release docs.
- CI workflow release checks.
- `--all-accessibility-modules` still excludes passive security.
- Wheel and sdist artifact names and package data inclusion.
- Installed wheel import and console smoke outside the source checkout.
- Mocked workflow execution branches.
- Mocked mobile emulation success/failure cleanup branches.

## CI

Added `.github/workflows/ci.yml` for:

- `ubuntu-latest`
- `windows-latest`
- Python 3.12
- pip cache
- editable install with development/browser/document/media extras
- Playwright Chromium install
- `pip check`
- `compileall`
- full tests under coverage
- coverage JSON/HTML artifacts
- package build
- clean installed-wheel smoke test

CI does not require JAWS, NVDA, VoiceOver, TalkBack, ADB, or FFmpeg.

## Known Limitations

- `python -m build` isolated mode could not complete locally because the sandbox blocked isolated build dependency downloads and the approval request was rejected by app usage limits. The local no-isolation build passed with installed setuptools 82.0.1 and wheel 0.47.0.
- Firefox and WebKit Playwright browsers are not installed locally.
- Native screen-reader adapters remain unavailable or scaffolded only.
- Playwright mobile emulation is not real TalkBack or VoiceOver testing.
- Passive security is not penetration testing.
- Document and browser/task-execution edge branches need more coverage before a stable release.

## Temporary Files

Temporary wheel-smoke virtual environments were created outside the repository and removed by `scripts/verify_wheel_install.py`.

Generated release artifacts intentionally kept locally for verification:

- `dist/a11yway-0.8.0b1.tar.gz`
- `dist/a11yway-0.8.0b1-py3-none-any.whl`
- `reports/coverage.json`

Generated coverage HTML is intentionally ignored and should not be committed:

- `reports/coverage_html/`

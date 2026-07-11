# A11yway Report Schema

Schema date: 2026-07-12

## JSON Report

Top-level keys for a static report:

- `tool`: tool name.
- `version`: application version label.
- `report_schema_version`: currently `1.0`.
- `extended_result_schema_version`: currently `1.0`.
- `source_file`: analyzed source input.
- `summary`: counts, agents, and checks.
- `issues`: enriched findings.
- `wcag_coverage`: tool coverage summary, not a conformance claim.
- `limitations`: report limitations.

Optional top-level keys are added only when relevant:

- `source`
- `extended_modules`
- `task`
- `analysis_modes`
- `browser`
- `low_vision`
- `task_execution`
- `visual_proof`
- `ai_scout`

## Extended Module Result

Every extended module result includes:

- `schema_version`: currently `1.0`.
- `created_at`: UTC ISO timestamp.
- `module`: stable module namespace.
- `check_id`: stable check identifier.
- `status`: one of `completed`, `blocked`, `failed`, `unavailable`, `unsupported`, or `scaffolded`.
- `findings`: normalized finding summaries.
- `artifacts`: JSON-safe module artifacts.
- `limitations`: module limitations.
- `capability`: optional capability metadata.

## Issue Evidence

Extended issue evidence includes:

- `module`
- `check_id`
- `evidence_type`: `deterministic` or `heuristic`
- `deterministic`
- `review_status`: `confirmed`, `likely`, `needs_review`, or `informational`
- `source`
- `selector`
- `observed`
- `expected`
- `manual_verification`
- `detection_source`
- `evidence_sources`
- `limitations`

Optional evidence fields include:

- `context`
- `snippet`
- `wcag_relation`

## Determinism Notes

- Saved JSON reports use sorted keys.
- Extended modules are sorted by module, check ID, and status in report output.
- Findings inside an extended module are sorted by issue type, severity, selector, and observed text.
- Dynamic timestamps should be normalized by downstream snapshot tests when byte-for-byte comparisons are needed.


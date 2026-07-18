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
- `issue_clusters`: root-issue and component-level clustering summaries.
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

Every report issue includes compatibility fields (`issue_type`, `severity`,
`confidence`, `message`, `evidence`, `suggested_fix`) and enriched evidence
for professional review.

Post-collection validation evidence includes:

- `rule_id`
- `normalized_page_url`
- `issue_category`
- `source_engine`
- `element_selector`
- `normalized_element_snippet`
- `accessible_name`
- `visible_text`
- `role`
- `confidence_level`: `confirmed_by_multiple_engines`, `strong`, `likely`, `needs_review`, `weak_heuristic`, or `suppressed`
- `verification_status`
- `deduplication_fingerprint`
- `human_review_reason`
- `related_finding_ids`
- `occurrence_count`
- `affected_page_count`
- `component_signature`

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
- Summary includes both `raw_occurrences` and `unique_root_issues`.
- `issue_clusters` are sorted by occurrence count, then rule id.
- Extended modules are sorted by module, check ID, and status in report output.
- Findings inside an extended module are sorted by issue type, severity, selector, and observed text.
- Dynamic timestamps should be normalized by downstream snapshot tests when byte-for-byte comparisons are needed.

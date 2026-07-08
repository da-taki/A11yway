# A11yway Batch Evaluation Summary

## Overview

- Batch config used: examples/sample_task_execution_batch.json
- Pages tested: 2
- Successful pages: 2
- Failed pages: 0
- Total issues: 1
- Total task blockers: 0

## Top Issue Types

- task_step_blocked: 1

## Severity Breakdown

- High: 1
- Medium: 0
- Low: 0

## Sources With Most Issues

| Name | Source | Task | Issues | Blockers | Report |
| --- | --- | --- | ---: | ---: | --- |
| Scholarship Form (click-only submit) | examples/sample_task_execution_form_broken.html | submit_scholarship_application | 1 | 0 | reports/task_execution_batch/broken_application_form.md |
| Scholarship Form (keyboard accessible) | examples/sample_task_execution_form.html | submit_scholarship_application | 0 | 0 | reports/task_execution_batch/accessible_application_form.md |

## Task Execution Results

Deterministic keyboard-only task attempts per page:

| Name | Task | Result | Steps passed |
| --- | --- | --- | --- |
| Scholarship Form (keyboard accessible) | submit_scholarship_application | completed | 11 of 11 |
| Scholarship Form (click-only submit) | submit_scholarship_application | blocked | 9 of 11 |

## High Priority Findings

### Scholarship Form (click-only submit)

- task_step_blocked: Task step could not be completed with the keyboard
- Full report: reports/task_execution_batch/broken_application_form.md

## Recommended Review Process

1. Review high severity issues first.
2. Confirm evidence snippets against the actual page.
3. Mark false positives.
4. Note barriers the static checks missed.
5. Decide which fixes are feasible for the organization.

## Limitations

- This prototype only runs static HTML checks.
- It does not replace a full human accessibility audit.
- It does not yet perform browser-based interaction testing.

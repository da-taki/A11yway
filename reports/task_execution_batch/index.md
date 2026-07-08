# A11yway Batch Accessibility Index

## Summary

- Total pages tested: 2
- Total issues: 1
- CSV index: reports/task_execution_batch/index.csv
- Evaluation summary: reports/task_execution_batch/evaluation_summary.md

### Counts By Severity

- high: 1

### Counts By Issue Type

- task_step_blocked: 1

## Sources Tested

| ID | Name | Source | Task | Status | Issues | Task blockers | Reports | Error |
| --- | --- | --- | --- | --- | ---: | ---: | --- | --- |
| accessible_application_form | Scholarship Form (keyboard accessible) | examples/sample_task_execution_form.html | submit_scholarship_application | passed | 0 | 0 | json: reports/task_execution_batch/accessible_application_form.json, markdown: reports/task_execution_batch/accessible_application_form.md |  |
| broken_application_form | Scholarship Form (click-only submit) | examples/sample_task_execution_form_broken.html | submit_scholarship_application | passed | 1 | 0 | json: reports/task_execution_batch/broken_application_form.json, markdown: reports/task_execution_batch/broken_application_form.md |  |

## Limitations

- This prototype only runs static HTML checks.
- It does not replace a full human accessibility audit.
- It does not yet perform browser-based interaction testing.

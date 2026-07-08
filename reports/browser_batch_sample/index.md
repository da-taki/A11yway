# A11yway Batch Accessibility Index

## Summary

- Total pages tested: 2
- Total issues: 15
- CSV index: reports/browser_batch_sample/index.csv
- Evaluation summary: reports/browser_batch_sample/evaluation_summary.md

### Counts By Severity

- high: 12
- medium: 3

### Counts By Issue Type

- missing_form_label: 3
- generic_link_text: 1
- missing_button_name: 2
- missing_image_alt: 1
- skipped_heading_level: 1
- missing_video_captions: 2
- browser_focused_control_missing_name: 5

## Sources Tested

| ID | Name | Source | Task | Status | Issues | Task blockers | Reports | Error |
| --- | --- | --- | --- | --- | ---: | ---: | --- | --- |
| scholarship_form | Student Scholarship Application | examples/sample_form.html | submit_scholarship_application | passed | 11 | 5 | json: reports/browser_batch_sample/scholarship_form.json, markdown: reports/browser_batch_sample/scholarship_form.md |  |
| dynamic_enrollment_form | Course Enrollment Form (JavaScript) | examples/sample_dynamic_form.html | submit_scholarship_application | passed | 4 | 2 | json: reports/browser_batch_sample/dynamic_enrollment_form.json, markdown: reports/browser_batch_sample/dynamic_enrollment_form.md |  |

## Limitations

- This prototype only runs static HTML checks.
- It does not replace a full human accessibility audit.
- It does not yet perform browser-based interaction testing.

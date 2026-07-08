# A11yway Batch Accessibility Index

## Summary

- Total pages tested: 2
- Total issues: 11
- CSV index: reports/batch_sample/index.csv

### Counts By Severity

- high: 6
- medium: 5

### Counts By Issue Type

- missing_form_label: 2
- generic_link_text: 2
- missing_button_name: 1
- missing_image_alt: 2
- skipped_heading_level: 1
- missing_video_captions: 2
- missing_audio_transcript: 1

## Sources Tested

| ID | Name | Source | Task | Status | Issues | Task blockers | Reports | Error |
| --- | --- | --- | --- | --- | ---: | ---: | --- | --- |
| scholarship_form | Student Scholarship Application | examples/sample_form.html | submit_scholarship_application | passed | 7 | 5 | json: reports/batch_sample/scholarship_form.json, markdown: reports/batch_sample/scholarship_form.md |  |
| learning_resources | Learning Resources Page | examples/sample_resource_page.html | access_learning_resources | passed | 4 | 4 | json: reports/batch_sample/learning_resources.json, markdown: reports/batch_sample/learning_resources.md |  |

## Limitations

- This prototype only runs static HTML checks.
- It does not replace a full human accessibility audit.
- It does not yet perform browser-based interaction testing.

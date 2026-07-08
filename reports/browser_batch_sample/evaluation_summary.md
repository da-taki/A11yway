# A11yway Batch Evaluation Summary

## Overview

- Batch config used: examples/sample_browser_batch.json
- Pages tested: 2
- Successful pages: 2
- Failed pages: 0
- Total issues: 15
- Total task blockers: 7

## Top Issue Types

- browser_focused_control_missing_name: 5
- missing_form_label: 3
- missing_button_name: 2
- missing_video_captions: 2
- generic_link_text: 1
- missing_image_alt: 1
- skipped_heading_level: 1

## Severity Breakdown

- High: 12
- Medium: 3
- Low: 0

## Sources With Most Issues

| Name | Source | Task | Issues | Blockers | Report |
| --- | --- | --- | ---: | ---: | --- |
| Student Scholarship Application | examples/sample_form.html | submit_scholarship_application | 11 | 5 | reports/browser_batch_sample/scholarship_form.md |
| Course Enrollment Form (JavaScript) | examples/sample_dynamic_form.html | submit_scholarship_application | 4 | 2 | reports/browser_batch_sample/dynamic_enrollment_form.md |

## High Priority Findings

### Student Scholarship Application

- missing_form_label: Form control is missing an accessible label
  - Evidence: `<input type="text" name="student_name">`
- missing_form_label: Form control is missing an accessible label
  - Evidence: `<textarea name="accommodation_request" rows="5">`
- missing_button_name: Button is missing an accessible name
  - Evidence: `<button type="button">`
- missing_video_captions: Video is missing captions
  - Evidence: `<video controls src="orientation.mp4">`
- browser_focused_control_missing_name: Focused control has no accessible name
- browser_focused_control_missing_name: Focused control has no accessible name
- browser_focused_control_missing_name: Focused control has no accessible name
- missing_video_captions: Video is missing captions
  - Evidence: `<video controls="" src="orientation.mp4">`
- Full report: reports/browser_batch_sample/scholarship_form.md

### Course Enrollment Form (JavaScript)

- browser_focused_control_missing_name: Focused control has no accessible name
- browser_focused_control_missing_name: Focused control has no accessible name
- missing_form_label: Form control is missing an accessible label
  - Evidence: `<input type="text" name="preferred_course">`
- missing_button_name: Button is missing an accessible name
  - Evidence: `<button type="button">`
- Full report: reports/browser_batch_sample/dynamic_enrollment_form.md

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

# A11yway Batch Evaluation Summary

## Overview

- Batch config used: examples/sample_batch.json
- Pages tested: 2
- Successful pages: 2
- Failed pages: 0
- Total issues: 11
- Total task blockers: 9

## Top Issue Types

- generic_link_text: 2
- missing_form_label: 2
- missing_image_alt: 2
- missing_video_captions: 2
- missing_audio_transcript: 1
- missing_button_name: 1
- skipped_heading_level: 1

## Severity Breakdown

- High: 6
- Medium: 5
- Low: 0

## Sources With Most Issues

| Name | Source | Task | Issues | Blockers | Report |
| --- | --- | --- | ---: | ---: | --- |
| Student Scholarship Application | examples/sample_form.html | submit_scholarship_application | 7 | 5 | reports/batch_sample/scholarship_form.md |
| Learning Resources Page | examples/sample_resource_page.html | access_learning_resources | 4 | 4 | reports/batch_sample/learning_resources.md |

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
- Full report: reports/batch_sample/scholarship_form.md

### Learning Resources Page

- missing_video_captions: Video is missing captions
  - Evidence: `<video controls src="lesson-overview.mp4">`
- missing_audio_transcript: Audio is missing a transcript
  - Evidence: `<audio controls src="assignment-instructions.mp3">`
- Full report: reports/batch_sample/learning_resources.md

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

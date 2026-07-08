# A11yway Accessibility Report

## Summary

- Source: examples/sample_task_execution_form.html
- Source type: file
- Issues found: 0
- Agents used: Keyboard-only student
- Checks run: html_form_labels, interactive_names, image_alt_text, heading_structure, page_metadata, media_accessibility, keyboard_focus_traversal, browser_dom_snapshot

### Counts By Severity

- None

### Counts By Issue Type

- None

## Browser Mode Summary

- Analysis modes: static, browser
- Browser audit success: true
- Checks run: keyboard_focus_traversal, browser_dom_snapshot
- Focus trace length: 5

## Browser Interaction Trace

| Step | Tag | Accessible name guess | ID/Name | Text/Href |
| ---: | --- | --- | --- | --- |
| 1 | input | Student name | student_name |  |
| 2 | input | Email | email |  |
| 3 | select | School | school | Choose a school Greenfield High School Riverside Academy |
| 4 | textarea | Accommodation request | accommodation_request |  |
| 5 | button | Submit application |  | Submit application |

### Browser Limitations

- Browser mode approximates keyboard interaction but does not simulate a full screen reader.
- Accessible names are estimated and require manual review.

## Task Execution

- Task: Submit scholarship application
- Student profile: Keyboard-only student
- Result: COMPLETED with keyboard-only interaction
- Steps passed: 11 of 11

| Step | Action | Status | Detail |
| --- | --- | --- | --- |
| read_page_purpose | expect_visible_text | passed | Text is visible on the page. |
| focus_name | focus_by_label_or_name | passed | Reached with the keyboard (tag: input). |
| type_name | type_text | passed | Typed with the keyboard. |
| focus_email | focus_by_label_or_name | passed | Reached with the keyboard (tag: input). |
| type_email | type_text | passed | Typed with the keyboard. |
| focus_school | focus_by_label_or_name | passed | Reached with the keyboard (tag: select). |
| select_first_option | select_first_non_empty_option | passed | Selected option with ArrowDown (value: "greenfield"). |
| focus_accommodation_request | focus_by_label_or_name | passed | Reached with the keyboard (tag: textarea). |
| type_accommodation_request | type_text | passed | Typed with the keyboard. |
| submit_form | activate_by_role_or_text | passed | Activated with Enter (tag: button). |
| confirm_submission | wait_for_text | passed | Text appeared on the page. |

### Task Execution Limitations

- Task steps are deterministic scripts; a human may find a workaround the script does not try.
- Step results show keyboard operability, not full assistive technology behavior.

## Task Context

- Task name: Submit scholarship application
- Student profile: Keyboard-only student

### Required Actions

- Read the page purpose
- Enter name
- Enter email
- Choose school
- Describe accommodation request
- Submit the form

### Likely Blockers

- None found for this task.

## Issues Found

No issues found by the current static checks.
## Limitations

- This prototype runs static HTML checks plus a basic keyboard interaction audit.
- It does not replace a full human accessibility audit.
- Browser mode does not simulate a full screen reader, and accessible names are estimated.

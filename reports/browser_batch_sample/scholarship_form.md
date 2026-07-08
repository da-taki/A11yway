# A11yway Accessibility Report

## Summary

- Source: examples/sample_form.html
- Source type: file
- Issues found: 11
- Agents used: Keyboard-only student
- Checks run: html_form_labels, interactive_names, image_alt_text, heading_structure, page_metadata, media_accessibility, keyboard_focus_traversal, browser_dom_snapshot

### Counts By Severity

- high: 8
- medium: 3

### Counts By Issue Type

- missing_form_label: 2
- generic_link_text: 1
- missing_button_name: 1
- missing_image_alt: 1
- skipped_heading_level: 1
- missing_video_captions: 2
- browser_focused_control_missing_name: 3

## Browser Mode Summary

- Analysis modes: static, browser
- Browser audit success: true
- Checks run: keyboard_focus_traversal, browser_dom_snapshot
- Focus trace length: 10

## Browser Interaction Trace

| Step | Tag | Accessible name guess | ID/Name | Text/Href |
| ---: | --- | --- | --- | --- |
| 1 | a | Download scholarship guidelines |  | Download scholarship guidelines |
| 2 | a | click here |  | click here |
| 3 | button |  |  |  |
| 4 | button | Save application draft |  |  |
| 5 | video |  |  |  |
| 6 | input |  | student_name |  |
| 7 | input | Student email | student_email |  |
| 8 | select | School | school_name | Choose a school Riverside High School Hillview Community School |
| 9 | textarea |  | accommodation_request |  |
| 10 | button | Submit application |  | Submit application |

### Browser Limitations

- Browser mode approximates keyboard interaction but does not simulate a full screen reader.
- Accessible names are estimated and require manual review.

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

- Form control is missing an accessible label
  - Issue type: missing_form_label
  - Severity: high
  - Task impact: Form control may be hard to understand or complete because it has no accessible label.
- Form control is missing an accessible label
  - Issue type: missing_form_label
  - Severity: high
  - Task impact: Form control may be hard to understand or complete because it has no accessible label.
- Link text is too generic
  - Issue type: generic_link_text
  - Severity: medium
  - Task impact: Link text may not clearly explain the destination or action.
- Button is missing an accessible name
  - Issue type: missing_button_name
  - Severity: high
  - Task impact: Student may not be able to identify what an unlabeled button does.
- Heading level is skipped
  - Issue type: skipped_heading_level
  - Severity: medium
  - Task impact: Student may struggle to understand the page structure and task sections.

## Issues Found

### 1. Form control is missing an accessible label

- Issue type: missing_form_label
- Rule: Form control missing accessible label
- Category: Forms
- Severity: high
- Why it matters: Students using keyboard navigation, assistive technology, or simplified layouts may not know what information the field expects.
- Suggested fix: Add a visible <label> connected with for/id. Use aria-label only when a visible label is not possible.
- Manual review: Check whether the visual design already implies the label but fails programmatically.
- Static check limitation: Static HTML cannot always confirm labels created dynamically by JavaScript.

Evidence:

- tag: input
- name: student_name
- line: 36
- reason: Form control has no accessible label.

```html
<input type="text" name="student_name">
```

### 2. Form control is missing an accessible label

- Issue type: missing_form_label
- Rule: Form control missing accessible label
- Category: Forms
- Severity: high
- Why it matters: Students using keyboard navigation, assistive technology, or simplified layouts may not know what information the field expects.
- Suggested fix: Add a visible <label> connected with for/id. Use aria-label only when a visible label is not possible.
- Manual review: Check whether the visual design already implies the label but fails programmatically.
- Static check limitation: Static HTML cannot always confirm labels created dynamically by JavaScript.

Evidence:

- tag: textarea
- name: accommodation_request
- line: 54
- reason: Form control has no accessible label.

```html
<textarea name="accommodation_request" rows="5">
```

### 3. Link text is too generic

- Issue type: generic_link_text
- Rule: Link text is too generic
- Category: Interactive Elements
- Severity: medium
- Why it matters: Students who navigate by a list of links hear 'click here' with no context and cannot tell links apart.
- Suggested fix: Use descriptive link text like "Download scholarship guidelines" instead of "click here."
- Manual review: Surrounding text may add context visually, but the link should still make sense on its own.
- Static check limitation: The check only matches a small list of common generic phrases.

Evidence:

- tag: a
- href: /scholarships/help
- text: click here
- line: 21
- reason: Link text is generic and does not explain the destination or action.

```html
<a href="/scholarships/help">click here</a>
```

### 4. Button is missing an accessible name

- Issue type: missing_button_name
- Rule: Button missing accessible name
- Category: Interactive Elements
- Severity: high
- Why it matters: A button without a name is announced as just 'button' by screen readers, so students cannot tell what pressing it will do.
- Suggested fix: Add clear button text or an aria-label that describes the button action.
- Manual review: Icon-only buttons may look meaningful visually but still need a programmatic name.
- Static check limitation: Static HTML cannot see names added later by JavaScript or icon fonts.

Evidence:

- tag: button
- line: 27
- reason: Button has no visible text, aria-label, title, or image alt text.

```html
<button type="button">
```

### 5. Image is missing useful alt text

- Issue type: missing_image_alt
- Rule: Image missing useful alt text
- Category: Images
- Severity: medium
- Why it matters: Students using screen readers miss the image content entirely, which can hide instructions, diagrams, or required information.
- Suggested fix: Add alt text that describes the image purpose, or mark decorative images as presentation.
- Manual review: Confirm whether the image is informative or decorative; only a human can judge if existing alt text is actually useful.
- Static check limitation: Static checks cannot judge alt text quality, only whether it exists.

Evidence:

- tag: img
- src: student-award.png
- line: 24
- reason: Image is missing useful alt text.

```html
<img src="student-award.png">
```

### 6. Heading level is skipped

- Issue type: skipped_heading_level
- Rule: Heading level is skipped
- Category: Headings & Structure
- Severity: medium
- Why it matters: Jumping from h1 to h3 breaks the page outline that screen reader users rely on to understand and navigate content.
- Suggested fix: Do not skip heading levels; move from h1 to h2 before h3.
- Manual review: Check whether the heading order still makes sense when read as an outline.
- Static check limitation: The check follows document order only; visual layout may differ.

Evidence:

- tag: h3
- text: Application Details
- line: 16
- reason: Heading level jumps from h1 to h3.

```html
<h3>
```

### 7. Video is missing captions

- Issue type: missing_video_captions
- Rule: Video missing captions
- Category: Media
- Severity: high
- Why it matters: Deaf and hard-of-hearing students cannot access spoken lesson content without captions or subtitles.
- Suggested fix: Add captions or subtitles for education video content.
- Manual review: Captions may be provided by an embedded player or platform instead of a track element.
- Static check limitation: The check only sees <track> elements; player-level or burned-in captions are invisible to static HTML.

Evidence:

- tag: video
- src: orientation.mp4
- line: 30
- reason: Video has no captions or subtitles track.

```html
<video controls src="orientation.mp4">
```

### 8. Focused control has no accessible name

- Issue type: browser_focused_control_missing_name
- Rule: Focused control has no accessible name
- Category: Keyboard Interaction
- Severity: high
- Why it matters: A keyboard user can reach the control, but without a name a screen reader announces nothing useful about what it does.
- Suggested fix: Add a visible label, text content, or aria-label so students know what the control does.
- Manual review: The accessible name is estimated; confirm with browser dev tools or a screen reader what is actually announced.
- Browser check limitation: Accessible names are estimated from labels, text, and common attributes, not from a full accessibility tree computation.

Evidence:

- tag: button
- step: 3
- detected_in: browser_interaction
- reason: A keyboard user reached this control, but it has no label, text, aria-label, or other usable name.

### 9. Focused control has no accessible name

- Issue type: browser_focused_control_missing_name
- Rule: Focused control has no accessible name
- Category: Keyboard Interaction
- Severity: high
- Why it matters: A keyboard user can reach the control, but without a name a screen reader announces nothing useful about what it does.
- Suggested fix: Add a visible label, text content, or aria-label so students know what the control does.
- Manual review: The accessible name is estimated; confirm with browser dev tools or a screen reader what is actually announced.
- Browser check limitation: Accessible names are estimated from labels, text, and common attributes, not from a full accessibility tree computation.

Evidence:

- tag: input
- name: student_name
- step: 6
- detected_in: browser_interaction
- reason: A keyboard user reached this control, but it has no label, text, aria-label, or other usable name.

### 10. Focused control has no accessible name

- Issue type: browser_focused_control_missing_name
- Rule: Focused control has no accessible name
- Category: Keyboard Interaction
- Severity: high
- Why it matters: A keyboard user can reach the control, but without a name a screen reader announces nothing useful about what it does.
- Suggested fix: Add a visible label, text content, or aria-label so students know what the control does.
- Manual review: The accessible name is estimated; confirm with browser dev tools or a screen reader what is actually announced.
- Browser check limitation: Accessible names are estimated from labels, text, and common attributes, not from a full accessibility tree computation.

Evidence:

- tag: textarea
- name: accommodation_request
- step: 9
- detected_in: browser_interaction
- reason: A keyboard user reached this control, but it has no label, text, aria-label, or other usable name.

### 11. Video is missing captions

- Issue type: missing_video_captions
- Rule: Video missing captions
- Category: Media
- Severity: high
- Why it matters: Deaf and hard-of-hearing students cannot access spoken lesson content without captions or subtitles.
- Suggested fix: Add captions or subtitles for education video content.
- Manual review: Captions may be provided by an embedded player or platform instead of a track element.
- Static check limitation: The check only sees <track> elements; player-level or burned-in captions are invisible to static HTML.

Evidence:

- tag: video
- src: orientation.mp4
- line: 28
- detected_in: browser_dom
- reason: Video has no captions or subtitles track.

```html
<video controls="" src="orientation.mp4">
```

## Limitations

- This prototype runs static HTML checks plus a basic keyboard interaction audit.
- It does not replace a full human accessibility audit.
- Browser mode does not simulate a full screen reader, and accessible names are estimated.

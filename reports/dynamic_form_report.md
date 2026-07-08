# A11yway Accessibility Report

## Summary

- Source: examples/sample_dynamic_form.html
- Source type: file
- Issues found: 4
- Agents used: Keyboard-only student
- Checks run: html_form_labels, interactive_names, image_alt_text, heading_structure, page_metadata, media_accessibility, keyboard_focus_traversal, browser_dom_snapshot

### Counts By Severity

- high: 4

### Counts By Issue Type

- browser_focused_control_missing_name: 2
- missing_form_label: 1
- missing_button_name: 1

## Browser Mode Summary

- Analysis modes: static, browser
- Browser audit success: true
- Checks run: keyboard_focus_traversal, browser_dom_snapshot
- Focus trace length: 5

## Browser Interaction Trace

| Step | Tag | Accessible name guess | ID/Name | Text/Href |
| ---: | --- | --- | --- | --- |
| 1 | input | Student name | student_name |  |
| 2 | button | Show more fields | show_more_fields | Show more fields |
| 3 | input |  | preferred_course |  |
| 4 | button |  |  |  |
| 5 | a | Read the enrollment guidelines |  | Read the enrollment guidelines |

### Browser Limitations

- Browser mode approximates keyboard interaction but does not simulate a full screen reader.
- Accessible names are estimated and require manual review.

## Issues Found

### 1. Focused control has no accessible name

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
- name: preferred_course
- step: 3
- detected_in: browser_interaction
- reason: A keyboard user reached this control, but it has no label, text, aria-label, or other usable name.

### 2. Focused control has no accessible name

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
- step: 4
- detected_in: browser_interaction
- reason: A keyboard user reached this control, but it has no label, text, aria-label, or other usable name.

### 3. Form control is missing an accessible label

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
- name: preferred_course
- line: 21
- detected_in: browser_dom
- reason: Form control has no accessible label.

```html
<input type="text" name="preferred_course">
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
- line: 21
- detected_in: browser_dom
- reason: Button has no visible text, aria-label, title, or image alt text.

```html
<button type="button">
```

## Limitations

- This prototype runs static HTML checks plus a basic keyboard interaction audit.
- It does not replace a full human accessibility audit.
- Browser mode does not simulate a full screen reader, and accessible names are estimated.

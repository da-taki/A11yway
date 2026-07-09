# A11yway Accessibility Report

## Summary

- Source: examples/sample_announce_transcript_broken.html
- Source type: file
- Issues found: 8
- Agents used: Keyboard-only student
- Checks run: html_form_labels, interactive_names, image_alt_text, heading_structure, page_metadata, media_accessibility, keyboard_focus_traversal, browser_dom_snapshot, accessibility_tree_announce

### Counts By Severity

- high: 8

### Counts By Issue Type

- missing_form_label: 2
- missing_link_name: 1
- missing_button_name: 1
- missing_image_alt: 1
- unnamed_focus_stop: 3

## Browser Mode Summary

- Analysis modes: static, browser
- Browser audit success: true
- Checks run: keyboard_focus_traversal, browser_dom_snapshot, accessibility_tree_announce
- Focus trace length: 5

## Browser Interaction Trace

| Step | Tag | Accessible name guess | ID/Name | Text/Href |
| ---: | --- | --- | --- | --- |
| 1 | a |  |  | library-rules.html |
| 2 | input |  | full_name |  |
| 3 | select | Grade level | grade_level | Choose a grade Grade 9 Grade 10 |
| 4 | button |  |  |  |
| 5 | button | Sign up for a library card |  | Sign up for a library card |

## Announce Transcript

What Chromium's computed accessibility tree exposes at each observed focus stop. This approximates what a screen reader would announce; real screen readers can differ.

1. link, (no accessible name) <- finding: unnamed focus stop
2. textbox, (no accessible name), required <- finding: unnamed focus stop
3. combobox, "Grade level", collapsed
4. button, (no accessible name), collapsed <- finding: unnamed focus stop
5. button, "Sign up for a library card"

### Browser Limitations

- Browser mode approximates keyboard interaction but does not simulate a full screen reader.
- Accessible names are estimated and require manual review.
- The announce transcript comes from Chromium's computed accessibility tree in one browser run.
- Real screen readers (NVDA, JAWS, VoiceOver) apply their own rules and can announce things differently.

## Visual Proof

- Screenshot path: reports/visual_announce_transcript_broken/page.png
- Focus path overlay path: reports/visual_announce_transcript_broken/focus_path.html
- Focus points count: 5

- Focus overlay shows observed Tab stops in this browser run.
- It does not represent every assistive technology experience.

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
- name: full_name
- line: 25
- reason: Form control has no accessible label.

```html
<input type="text" name="full_name" required>
```

### 2. Link is missing an accessible name

- Issue type: missing_link_name
- Rule: Link missing accessible name
- Category: Interactive Elements
- Severity: high
- Why it matters: Screen reader users hear an empty or meaningless link and cannot decide whether to follow it.
- Suggested fix: Add descriptive link text that explains the link destination or action.
- Manual review: Links wrapping only images need useful alt text on the image.
- Static check limitation: Static HTML cannot detect link names injected by JavaScript.

Evidence:

- tag: a
- href: library-rules.html
- line: 21
- reason: Link has no usable text, aria-label, title, or image alt text.

```html
<a href="library-rules.html">
```

### 3. Button is missing an accessible name

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
- line: 35
- reason: Button has no visible text, aria-label, title, or image alt text.

```html
<button type="button" aria-expanded="false" aria-controls="hours_details">
```

### 4. Image is missing useful alt text

- Issue type: missing_image_alt
- Rule: Image missing useful alt text
- Category: Images
- Severity: high
- Why it matters: Students using screen readers miss the image content entirely, which can hide instructions, diagrams, or required information.
- Suggested fix: Add alt text that describes the image purpose, or mark decorative images as presentation.
- Manual review: Confirm whether the image is informative or decorative; only a human can judge if existing alt text is actually useful.
- Static check limitation: Static checks cannot judge alt text quality, only whether it exists.

Evidence:

- tag: img
- src: rules-icon.png
- line: 21
- reason: Image is missing useful alt text.

```html
<img src="rules-icon.png" alt="">
```

### 5. Focus stop announces no accessible name

- Issue type: unnamed_focus_stop
- Rule: Focus stop announces no accessible name
- Category: Keyboard Interaction
- Severity: high
- Why it matters: Chromium's accessibility tree computed an empty accessible name for this focus stop, so a screen reader user hears at most a role and cannot tell what the element is or does.
- Suggested fix: Add a visible label, text content, alt text, or aria-label so the browser computes a usable accessible name for this element.
- Manual review: Confirm with a real screen reader. When this finding is present, the heuristic browser_focused_control_missing_name check is skipped for the same element, since the computed tree is the stronger evidence.
- Browser check limitation: Based on Chromium's computed accessibility tree in one browser run. It is not a screen reader simulation; NVDA, JAWS, and VoiceOver apply their own rules and other browsers can differ.

Evidence:

- tag: a
- href: library-rules.html
- step: 1
- detected_in: browser_interaction
- reason: Chromium's accessibility tree computed an empty accessible name for this focus stop, so a screen reader announces nothing useful about it.

### 6. Focus stop announces no accessible name

- Issue type: unnamed_focus_stop
- Rule: Focus stop announces no accessible name
- Category: Keyboard Interaction
- Severity: high
- Why it matters: Chromium's accessibility tree computed an empty accessible name for this focus stop, so a screen reader user hears at most a role and cannot tell what the element is or does.
- Suggested fix: Add a visible label, text content, alt text, or aria-label so the browser computes a usable accessible name for this element.
- Manual review: Confirm with a real screen reader. When this finding is present, the heuristic browser_focused_control_missing_name check is skipped for the same element, since the computed tree is the stronger evidence.
- Browser check limitation: Based on Chromium's computed accessibility tree in one browser run. It is not a screen reader simulation; NVDA, JAWS, and VoiceOver apply their own rules and other browsers can differ.

Evidence:

- tag: input
- name: full_name
- step: 2
- detected_in: browser_interaction
- reason: Chromium's accessibility tree computed an empty accessible name for this focus stop, so a screen reader announces nothing useful about it.

### 7. Focus stop announces no accessible name

- Issue type: unnamed_focus_stop
- Rule: Focus stop announces no accessible name
- Category: Keyboard Interaction
- Severity: high
- Why it matters: Chromium's accessibility tree computed an empty accessible name for this focus stop, so a screen reader user hears at most a role and cannot tell what the element is or does.
- Suggested fix: Add a visible label, text content, alt text, or aria-label so the browser computes a usable accessible name for this element.
- Manual review: Confirm with a real screen reader. When this finding is present, the heuristic browser_focused_control_missing_name check is skipped for the same element, since the computed tree is the stronger evidence.
- Browser check limitation: Based on Chromium's computed accessibility tree in one browser run. It is not a screen reader simulation; NVDA, JAWS, and VoiceOver apply their own rules and other browsers can differ.

Evidence:

- tag: button
- step: 4
- detected_in: browser_interaction
- reason: Chromium's accessibility tree computed an empty accessible name for this focus stop, so a screen reader announces nothing useful about it.

### 8. Form control is missing an accessible label

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
- name: full_name
- line: 23
- detected_in: browser_dom
- reason: Form control has no accessible label.

```html
<input type="text" name="full_name" required="" style="">
```

## Limitations

- This prototype runs static HTML checks plus a basic keyboard interaction audit.
- It does not replace a full human accessibility audit.
- Browser mode does not simulate a full screen reader, and accessible names are estimated.

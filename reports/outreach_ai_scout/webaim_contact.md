# A11yway Accessibility Report

## Summary

- Source: https://webaim.org/contact/
- Source type: url
- Issues found: 50
- Agents used: Keyboard-only student
- Checks run: html_form_labels, interactive_names, image_alt_text, heading_structure, page_metadata, media_accessibility, keyboard_focus_traversal, browser_dom_snapshot, rendered_color_contrast, zoom_reflow_200, focus_visibility

### Counts By Severity

- high: 35
- medium: 15

### Counts By Issue Type

- missing_form_label: 2
- missing_image_alt: 12
- browser_focused_control_missing_name: 1
- zoom_fixed_width_content: 3
- focus_indicator_missing: 32

### Source Metadata

- Final URL: https://webaim.org/contact/
- Status code: 200
- Content type: text/html; charset=UTF-8

## Browser Mode Summary

- Analysis modes: static, browser, low_vision
- Browser audit success: true
- Checks run: keyboard_focus_traversal, browser_dom_snapshot
- Focus trace length: 60

## Browser Interaction Trace

| Step | Tag | Accessible name guess | ID/Name | Text/Href |
| ---: | --- | --- | --- | --- |
| 1 | a | skip to main content |  | skip to main content |
| 2 | a | WebAIM - Web Accessibility In Mind |  | / |
| 3 | a | services |  | services |
| 4 | a | articles |  | articles |
| 5 | a | resources |  | resources |
| 6 | a | projects |  | projects |
| 7 | a | community |  | community |
| 8 | input | Search: | q |  |
| 9 | input |  |  |  |
| 10 | a | Introduction to Web Accessibility |  | Introduction to Web Accessibility |
| 11 | a | WebAIM Training |  | WebAIM Training |
| 12 | a | Home |  | Home |
| 13 | input | Your Name: | sender |  |
| 14 | input | Your E-mail Address: | email |  |
| 15 | select | Subject: | subject | Choose a category... Website comments Evaluation, testing, or consultation Acces |
| 16 | textarea | Message: | message |  |
| 17 | input | Send Message | Submit |  |
| 18 | a | training |  | training |
| 19 | a | 435-797-8284 |  | 435-797-8284 |
| 20 | a | 435-797-0974 |  | 435-797-0974 |

Trace truncated: showing the first 20 of 60 steps.

### Browser Limitations

- Browser mode approximates keyboard interaction but does not simulate a full screen reader.
- Accessible names are estimated and require manual review.

## Low-Vision Checks

- Status: passed
- Checks run: rendered_color_contrast, zoom_reflow_200, focus_visibility
- Contrast samples analyzed: 100
- Viewport width for reflow check: 640
- Document scroll width: 640
- Horizontal overflow amount: 0
- Focus stops checked: 40
- Focus indicator concerns: 32

### Low-Vision Limitations

- Low-vision checks use browser-computed styles and conservative heuristics.
- Rendered color contrast checks do not prove full WCAG conformance.
- Zoom/reflow uses a narrow viewport approximation rather than a full zoom compliance test.
- Focus indicator detection may miss custom focus styles.

## Visual Proof

- Screenshot path: reports/outreach_ai_scout/visual/webaim_contact/page.png
- Focus path overlay path: reports/outreach_ai_scout/visual/webaim_contact/focus_path.html
- Focus points count: 60

- Focus overlay shows observed Tab stops in this browser run.
- It does not represent every assistive technology experience.

### What the AI Found

- Status: ok
- Mode: suggest_only
- Model: llama-3.3-70b-versatile

Possible accessibility barriers found on the WebAIM contact page

1. AI-suggested observation: Some images may not have useful alternative text
   Related evidence, if any: Multiple instances of missing image alt text were detected
   Human review needed: true
   Confidence: AI-only

2. AI-suggested observation: Some form controls may be missing accessible labels
   Related evidence, if any: Instances of missing form labels were detected
   Human review needed: true
   Confidence: AI-only

3. AI-suggested observation: Some focused controls may be missing accessible names
   Related evidence, if any: Instances of browser focused control missing name were detected
   Human review needed: true
   Confidence: AI-only

#### Outreach Notes

- We suggest reviewing the contact page for potential accessibility barriers, particularly with regards to image alternative text, form control labels, and focused control names.

#### AI Scout Limitations

- AI Scout findings are suggestions and need human review.
- AI Scout output is not a confirmed accessibility finding.
- AI Scout does not determine legal compliance, WCAG compliance, or screen-reader behavior.
- AI Scout output is not a needs human review accessibility finding.


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
- src: /media/template/search.svg
- line: 68
- reason: Form control has no accessible label.

```html
<input type="image" src="/media/template/search.svg" alt="Submit Search">
```

### 2. Image is missing useful alt text

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
- src: /media/common/staff/jared.jpg
- line: 169
- reason: Image is missing useful alt text.

```html
<img src="/media/common/staff/jared.jpg" alt="" width="160" class="floatright">
```

### 3. Image is missing useful alt text

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
- src: /media/common/staff/christopher.jpg
- line: 174
- reason: Image is missing useful alt text.

```html
<img src="/media/common/staff/christopher.jpg" alt="" width="160" class="floatright">
```

### 4. Image is missing useful alt text

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
- src: /media/common/staff/jon.jpg
- line: 179
- reason: Image is missing useful alt text.

```html
<img src="/media/common/staff/jon.jpg" alt="" width="160" height="200" class="floatright">
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
- src: /media/common/staff/george.jpg
- line: 184
- reason: Image is missing useful alt text.

```html
<img src="/media/common/staff/george.jpg" alt="" width="160" class="floatright">
```

### 6. Image is missing useful alt text

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
- src: /media/common/staff/john.jpg
- line: 190
- reason: Image is missing useful alt text.

```html
<img src="/media/common/staff/john.jpg" alt="" width="160" class="floatright">
```

### 7. Image is missing useful alt text

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
- src: /media/common/staff/rob.jpg
- line: 196
- reason: Image is missing useful alt text.

```html
<img src="/media/common/staff/rob.jpg" alt="" width="160" class="floatright">
```

### 8. Image is missing useful alt text

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
- src: /media/common/staff/cynthia.jpg
- line: 201
- reason: Image is missing useful alt text.

```html
<img src="/media/common/staff/cynthia.jpg" alt="" width="160" class="floatright">
```

### 9. Image is missing useful alt text

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
- src: /media/common/staff/lyssa.jpg
- line: 206
- reason: Image is missing useful alt text.

```html
<img src="/media/common/staff/lyssa.jpg" alt="" width="160" class="floatright">
```

### 10. Image is missing useful alt text

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
- src: /media/common/staff/cameron.jpg
- line: 211
- reason: Image is missing useful alt text.

```html
<img src="/media/common/staff/cameron.jpg" alt="" width="160" class="floatright">
```

### 11. Image is missing useful alt text

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
- src: /media/common/staff/alyson.jpg
- line: 215
- reason: Image is missing useful alt text.

```html
<img src="/media/common/staff/alyson.jpg" alt="" width="160" class="floatright">
```

### 12. Image is missing useful alt text

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
- src: /media/common/staff/claire.jpg
- line: 220
- reason: Image is missing useful alt text.

```html
<img src="/media/common/staff/claire.jpg" alt="" width="160" class="floatright">
```

### 13. Image is missing useful alt text

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
- src: /media/common/staff/na.jpg
- line: 224
- reason: Image is missing useful alt text.

```html
<img src="/media/common/staff/na.jpg" alt="" width="160" class="floatright">
```

### 14. Focused control has no accessible name

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
- src: /media/template/search.svg
- step: 9
- detected_in: browser_interaction
- reason: A keyboard user reached this control, but it has no label, text, aria-label, or other usable name.

### 15. Form control is missing an accessible label

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
- src: /media/template/search.svg
- line: 66
- detected_in: browser_dom
- reason: Form control has no accessible label.

```html
<input type="image" src="/media/template/search.svg" alt="Submit Search" class="" style="">
```

### 16. Fixed or wide content may prevent reflow

- Issue type: zoom_fixed_width_content
- Rule: Fixed or wide content may prevent reflow
- Category: Low Vision
- Severity: medium
- Why it matters: Large fixed-width elements can force horizontal scrolling and hide content when users zoom or use narrow windows.
- Suggested fix: Replace fixed-width layout with responsive sizing such as max-width: 100%.
- Manual review: Confirm whether the wide element is essential and whether all content remains reachable without two-dimensional scrolling.
- Browser check limitation: The check flags obvious wide rendered elements and fixed pixel widths; it may miss complex layout problems.

Evidence:

- tag: div
- id: headcontainer
- text: skip to main content Main Navigation services articles resources projects commun
- detected_in: low_vision
- reason: A rendered element is wider than the narrow viewport or uses a large fixed pixel width.

### 17. Fixed or wide content may prevent reflow

- Issue type: zoom_fixed_width_content
- Rule: Fixed or wide content may prevent reflow
- Category: Low Vision
- Severity: medium
- Why it matters: Large fixed-width elements can force horizontal scrolling and hide content when users zoom or use narrow windows.
- Suggested fix: Replace fixed-width layout with responsive sizing such as max-width: 100%.
- Manual review: Confirm whether the wide element is essential and whether all content remains reachable without two-dimensional scrolling.
- Browser check limitation: The check flags obvious wide rendered elements and fixed pixel widths; it may miss complex layout problems.

Evidence:

- tag: header
- text: skip to main content Main Navigation services articles resources projects commun
- detected_in: low_vision
- reason: A rendered element is wider than the narrow viewport or uses a large fixed pixel width.

### 18. Fixed or wide content may prevent reflow

- Issue type: zoom_fixed_width_content
- Rule: Fixed or wide content may prevent reflow
- Category: Low Vision
- Severity: medium
- Why it matters: Large fixed-width elements can force horizontal scrolling and hide content when users zoom or use narrow windows.
- Suggested fix: Replace fixed-width layout with responsive sizing such as max-width: 100%.
- Manual review: Confirm whether the wide element is essential and whether all content remains reachable without two-dimensional scrolling.
- Browser check limitation: The check flags obvious wide rendered elements and fixed pixel widths; it may miss complex layout problems.

Evidence:

- tag: div
- id: skiptocontent
- text: skip to main content
- detected_in: low_vision
- reason: A rendered element is wider than the narrow viewport or uses a large fixed pixel width.

### 19. Focused element may not show a visible focus indicator

- Issue type: focus_indicator_missing
- Rule: Focused element may not show a visible focus indicator
- Category: Low Vision
- Severity: high
- Why it matters: Keyboard users with low vision need a visible indicator to know which control currently has focus.
- Suggested fix: Provide a clear :focus or :focus-visible style with visible outline, border, or shadow.
- Manual review: Manually tab through the page; some custom focus styles may be visible but not detected by this heuristic.
- Browser check limitation: Focus indicator detection checks computed outline, border, and shadow heuristically and can miss custom visual treatments.

Evidence:

- tag: a
- step: 2
- detected_in: low_vision
- reason: The focused element did not expose an obvious outline, box-shadow, or border focus style in computed CSS.

### 20. Focused element may not show a visible focus indicator

- Issue type: focus_indicator_missing
- Rule: Focused element may not show a visible focus indicator
- Category: Low Vision
- Severity: high
- Why it matters: Keyboard users with low vision need a visible indicator to know which control currently has focus.
- Suggested fix: Provide a clear :focus or :focus-visible style with visible outline, border, or shadow.
- Manual review: Manually tab through the page; some custom focus styles may be visible but not detected by this heuristic.
- Browser check limitation: Focus indicator detection checks computed outline, border, and shadow heuristically and can miss custom visual treatments.

Evidence:

- tag: a
- text: services
- step: 3
- detected_in: low_vision
- reason: The focused element did not expose an obvious outline, box-shadow, or border focus style in computed CSS.

### 21. Focused element may not show a visible focus indicator

- Issue type: focus_indicator_missing
- Rule: Focused element may not show a visible focus indicator
- Category: Low Vision
- Severity: high
- Why it matters: Keyboard users with low vision need a visible indicator to know which control currently has focus.
- Suggested fix: Provide a clear :focus or :focus-visible style with visible outline, border, or shadow.
- Manual review: Manually tab through the page; some custom focus styles may be visible but not detected by this heuristic.
- Browser check limitation: Focus indicator detection checks computed outline, border, and shadow heuristically and can miss custom visual treatments.

Evidence:

- tag: a
- text: articles
- step: 4
- detected_in: low_vision
- reason: The focused element did not expose an obvious outline, box-shadow, or border focus style in computed CSS.

### 22. Focused element may not show a visible focus indicator

- Issue type: focus_indicator_missing
- Rule: Focused element may not show a visible focus indicator
- Category: Low Vision
- Severity: high
- Why it matters: Keyboard users with low vision need a visible indicator to know which control currently has focus.
- Suggested fix: Provide a clear :focus or :focus-visible style with visible outline, border, or shadow.
- Manual review: Manually tab through the page; some custom focus styles may be visible but not detected by this heuristic.
- Browser check limitation: Focus indicator detection checks computed outline, border, and shadow heuristically and can miss custom visual treatments.

Evidence:

- tag: a
- text: resources
- step: 5
- detected_in: low_vision
- reason: The focused element did not expose an obvious outline, box-shadow, or border focus style in computed CSS.

### 23. Focused element may not show a visible focus indicator

- Issue type: focus_indicator_missing
- Rule: Focused element may not show a visible focus indicator
- Category: Low Vision
- Severity: high
- Why it matters: Keyboard users with low vision need a visible indicator to know which control currently has focus.
- Suggested fix: Provide a clear :focus or :focus-visible style with visible outline, border, or shadow.
- Manual review: Manually tab through the page; some custom focus styles may be visible but not detected by this heuristic.
- Browser check limitation: Focus indicator detection checks computed outline, border, and shadow heuristically and can miss custom visual treatments.

Evidence:

- tag: a
- text: projects
- step: 6
- detected_in: low_vision
- reason: The focused element did not expose an obvious outline, box-shadow, or border focus style in computed CSS.

### 24. Focused element may not show a visible focus indicator

- Issue type: focus_indicator_missing
- Rule: Focused element may not show a visible focus indicator
- Category: Low Vision
- Severity: high
- Why it matters: Keyboard users with low vision need a visible indicator to know which control currently has focus.
- Suggested fix: Provide a clear :focus or :focus-visible style with visible outline, border, or shadow.
- Manual review: Manually tab through the page; some custom focus styles may be visible but not detected by this heuristic.
- Browser check limitation: Focus indicator detection checks computed outline, border, and shadow heuristically and can miss custom visual treatments.

Evidence:

- tag: a
- text: community
- step: 7
- detected_in: low_vision
- reason: The focused element did not expose an obvious outline, box-shadow, or border focus style in computed CSS.

### 25. Focused element may not show a visible focus indicator

- Issue type: focus_indicator_missing
- Rule: Focused element may not show a visible focus indicator
- Category: Low Vision
- Severity: high
- Why it matters: Keyboard users with low vision need a visible indicator to know which control currently has focus.
- Suggested fix: Provide a clear :focus or :focus-visible style with visible outline, border, or shadow.
- Manual review: Manually tab through the page; some custom focus styles may be visible but not detected by this heuristic.
- Browser check limitation: Focus indicator detection checks computed outline, border, and shadow heuristically and can miss custom visual treatments.

Evidence:

- tag: input
- id: q
- name: q
- step: 8
- detected_in: low_vision
- reason: The focused element did not expose an obvious outline, box-shadow, or border focus style in computed CSS.

### 26. Focused element may not show a visible focus indicator

- Issue type: focus_indicator_missing
- Rule: Focused element may not show a visible focus indicator
- Category: Low Vision
- Severity: high
- Why it matters: Keyboard users with low vision need a visible indicator to know which control currently has focus.
- Suggested fix: Provide a clear :focus or :focus-visible style with visible outline, border, or shadow.
- Manual review: Manually tab through the page; some custom focus styles may be visible but not detected by this heuristic.
- Browser check limitation: Focus indicator detection checks computed outline, border, and shadow heuristically and can miss custom visual treatments.

Evidence:

- tag: input
- step: 9
- detected_in: low_vision
- reason: The focused element did not expose an obvious outline, box-shadow, or border focus style in computed CSS.

### 27. Focused element may not show a visible focus indicator

- Issue type: focus_indicator_missing
- Rule: Focused element may not show a visible focus indicator
- Category: Low Vision
- Severity: high
- Why it matters: Keyboard users with low vision need a visible indicator to know which control currently has focus.
- Suggested fix: Provide a clear :focus or :focus-visible style with visible outline, border, or shadow.
- Manual review: Manually tab through the page; some custom focus styles may be visible but not detected by this heuristic.
- Browser check limitation: Focus indicator detection checks computed outline, border, and shadow heuristically and can miss custom visual treatments.

Evidence:

- tag: a
- text: Home
- step: 12
- detected_in: low_vision
- reason: The focused element did not expose an obvious outline, box-shadow, or border focus style in computed CSS.

### 28. Focused element may not show a visible focus indicator

- Issue type: focus_indicator_missing
- Rule: Focused element may not show a visible focus indicator
- Category: Low Vision
- Severity: high
- Why it matters: Keyboard users with low vision need a visible indicator to know which control currently has focus.
- Suggested fix: Provide a clear :focus or :focus-visible style with visible outline, border, or shadow.
- Manual review: Manually tab through the page; some custom focus styles may be visible but not detected by this heuristic.
- Browser check limitation: Focus indicator detection checks computed outline, border, and shadow heuristically and can miss custom visual treatments.

Evidence:

- tag: a
- text: training
- step: 18
- detected_in: low_vision
- reason: The focused element did not expose an obvious outline, box-shadow, or border focus style in computed CSS.

### 29. Focused element may not show a visible focus indicator

- Issue type: focus_indicator_missing
- Rule: Focused element may not show a visible focus indicator
- Category: Low Vision
- Severity: high
- Why it matters: Keyboard users with low vision need a visible indicator to know which control currently has focus.
- Suggested fix: Provide a clear :focus or :focus-visible style with visible outline, border, or shadow.
- Manual review: Manually tab through the page; some custom focus styles may be visible but not detected by this heuristic.
- Browser check limitation: Focus indicator detection checks computed outline, border, and shadow heuristically and can miss custom visual treatments.

Evidence:

- tag: a
- text: 435-797-8284
- step: 19
- detected_in: low_vision
- reason: The focused element did not expose an obvious outline, box-shadow, or border focus style in computed CSS.

### 30. Focused element may not show a visible focus indicator

- Issue type: focus_indicator_missing
- Rule: Focused element may not show a visible focus indicator
- Category: Low Vision
- Severity: high
- Why it matters: Keyboard users with low vision need a visible indicator to know which control currently has focus.
- Suggested fix: Provide a clear :focus or :focus-visible style with visible outline, border, or shadow.
- Manual review: Manually tab through the page; some custom focus styles may be visible but not detected by this heuristic.
- Browser check limitation: Focus indicator detection checks computed outline, border, and shadow heuristically and can miss custom visual treatments.

Evidence:

- tag: a
- text: 435-797-0974
- step: 20
- detected_in: low_vision
- reason: The focused element did not expose an obvious outline, box-shadow, or border focus style in computed CSS.

### 31. Focused element may not show a visible focus indicator

- Issue type: focus_indicator_missing
- Rule: Focused element may not show a visible focus indicator
- Category: Low Vision
- Severity: high
- Why it matters: Keyboard users with low vision need a visible indicator to know which control currently has focus.
- Suggested fix: Provide a clear :focus or :focus-visible style with visible outline, border, or shadow.
- Manual review: Manually tab through the page; some custom focus styles may be visible but not detected by this heuristic.
- Browser check limitation: Focus indicator detection checks computed outline, border, and shadow heuristically and can miss custom visual treatments.

Evidence:

- tag: a
- text: 435-797-7024
- step: 21
- detected_in: low_vision
- reason: The focused element did not expose an obvious outline, box-shadow, or border focus style in computed CSS.

### 32. Focused element may not show a visible focus indicator

- Issue type: focus_indicator_missing
- Rule: Focused element may not show a visible focus indicator
- Category: Low Vision
- Severity: high
- Why it matters: Keyboard users with low vision need a visible indicator to know which control currently has focus.
- Suggested fix: Provide a clear :focus or :focus-visible style with visible outline, border, or shadow.
- Manual review: Manually tab through the page; some custom focus styles may be visible but not detected by this heuristic.
- Browser check limitation: Focus indicator detection checks computed outline, border, and shadow heuristically and can miss custom visual treatments.

Evidence:

- tag: a
- text: Jared Smith
- step: 22
- detected_in: low_vision
- reason: The focused element did not expose an obvious outline, box-shadow, or border focus style in computed CSS.

### 33. Focused element may not show a visible focus indicator

- Issue type: focus_indicator_missing
- Rule: Focused element may not show a visible focus indicator
- Category: Low Vision
- Severity: high
- Why it matters: Keyboard users with low vision need a visible indicator to know which control currently has focus.
- Suggested fix: Provide a clear :focus or :focus-visible style with visible outline, border, or shadow.
- Manual review: Manually tab through the page; some custom focus styles may be visible but not detected by this heuristic.
- Browser check limitation: Focus indicator detection checks computed outline, border, and shadow heuristically and can miss custom visual treatments.

Evidence:

- tag: a
- text: Christopher Phillips
- step: 23
- detected_in: low_vision
- reason: The focused element did not expose an obvious outline, box-shadow, or border focus style in computed CSS.

### 34. Focused element may not show a visible focus indicator

- Issue type: focus_indicator_missing
- Rule: Focused element may not show a visible focus indicator
- Category: Low Vision
- Severity: high
- Why it matters: Keyboard users with low vision need a visible indicator to know which control currently has focus.
- Suggested fix: Provide a clear :focus or :focus-visible style with visible outline, border, or shadow.
- Manual review: Manually tab through the page; some custom focus styles may be visible but not detected by this heuristic.
- Browser check limitation: Focus indicator detection checks computed outline, border, and shadow heuristically and can miss custom visual treatments.

Evidence:

- tag: a
- text: Jonathan Whiting
- step: 24
- detected_in: low_vision
- reason: The focused element did not expose an obvious outline, box-shadow, or border focus style in computed CSS.

### 35. Focused element may not show a visible focus indicator

- Issue type: focus_indicator_missing
- Rule: Focused element may not show a visible focus indicator
- Category: Low Vision
- Severity: high
- Why it matters: Keyboard users with low vision need a visible indicator to know which control currently has focus.
- Suggested fix: Provide a clear :focus or :focus-visible style with visible outline, border, or shadow.
- Manual review: Manually tab through the page; some custom focus styles may be visible but not detected by this heuristic.
- Browser check limitation: Focus indicator detection checks computed outline, border, and shadow heuristically and can miss custom visual treatments.

Evidence:

- tag: a
- text: George Joeckel
- step: 25
- detected_in: low_vision
- reason: The focused element did not expose an obvious outline, box-shadow, or border focus style in computed CSS.

### 36. Focused element may not show a visible focus indicator

- Issue type: focus_indicator_missing
- Rule: Focused element may not show a visible focus indicator
- Category: Low Vision
- Severity: high
- Why it matters: Keyboard users with low vision need a visible indicator to know which control currently has focus.
- Suggested fix: Provide a clear :focus or :focus-visible style with visible outline, border, or shadow.
- Manual review: Manually tab through the page; some custom focus styles may be visible but not detected by this heuristic.
- Browser check limitation: Focus indicator detection checks computed outline, border, and shadow heuristically and can miss custom visual treatments.

Evidence:

- tag: a
- text: John Northup
- step: 26
- detected_in: low_vision
- reason: The focused element did not expose an obvious outline, box-shadow, or border focus style in computed CSS.

### 37. Focused element may not show a visible focus indicator

- Issue type: focus_indicator_missing
- Rule: Focused element may not show a visible focus indicator
- Category: Low Vision
- Severity: high
- Why it matters: Keyboard users with low vision need a visible indicator to know which control currently has focus.
- Suggested fix: Provide a clear :focus or :focus-visible style with visible outline, border, or shadow.
- Manual review: Manually tab through the page; some custom focus styles may be visible but not detected by this heuristic.
- Browser check limitation: Focus indicator detection checks computed outline, border, and shadow heuristically and can miss custom visual treatments.

Evidence:

- tag: a
- text: Rob Carr
- step: 27
- detected_in: low_vision
- reason: The focused element did not expose an obvious outline, box-shadow, or border focus style in computed CSS.

### 38. Focused element may not show a visible focus indicator

- Issue type: focus_indicator_missing
- Rule: Focused element may not show a visible focus indicator
- Category: Low Vision
- Severity: high
- Why it matters: Keyboard users with low vision need a visible indicator to know which control currently has focus.
- Suggested fix: Provide a clear :focus or :focus-visible style with visible outline, border, or shadow.
- Manual review: Manually tab through the page; some custom focus styles may be visible but not detected by this heuristic.
- Browser check limitation: Focus indicator detection checks computed outline, border, and shadow heuristically and can miss custom visual treatments.

Evidence:

- tag: a
- text: Cynthia Curry
- step: 28
- detected_in: low_vision
- reason: The focused element did not expose an obvious outline, box-shadow, or border focus style in computed CSS.

### 39. Focused element may not show a visible focus indicator

- Issue type: focus_indicator_missing
- Rule: Focused element may not show a visible focus indicator
- Category: Low Vision
- Severity: high
- Why it matters: Keyboard users with low vision need a visible indicator to know which control currently has focus.
- Suggested fix: Provide a clear :focus or :focus-visible style with visible outline, border, or shadow.
- Manual review: Manually tab through the page; some custom focus styles may be visible but not detected by this heuristic.
- Browser check limitation: Focus indicator detection checks computed outline, border, and shadow heuristically and can miss custom visual treatments.

Evidence:

- tag: a
- text: Lyssa Prince
- step: 29
- detected_in: low_vision
- reason: The focused element did not expose an obvious outline, box-shadow, or border focus style in computed CSS.

### 40. Focused element may not show a visible focus indicator

- Issue type: focus_indicator_missing
- Rule: Focused element may not show a visible focus indicator
- Category: Low Vision
- Severity: high
- Why it matters: Keyboard users with low vision need a visible indicator to know which control currently has focus.
- Suggested fix: Provide a clear :focus or :focus-visible style with visible outline, border, or shadow.
- Manual review: Manually tab through the page; some custom focus styles may be visible but not detected by this heuristic.
- Browser check limitation: Focus indicator detection checks computed outline, border, and shadow heuristically and can miss custom visual treatments.

Evidence:

- tag: a
- text: Cameron Lund
- step: 30
- detected_in: low_vision
- reason: The focused element did not expose an obvious outline, box-shadow, or border focus style in computed CSS.

### 41. Focused element may not show a visible focus indicator

- Issue type: focus_indicator_missing
- Rule: Focused element may not show a visible focus indicator
- Category: Low Vision
- Severity: high
- Why it matters: Keyboard users with low vision need a visible indicator to know which control currently has focus.
- Suggested fix: Provide a clear :focus or :focus-visible style with visible outline, border, or shadow.
- Manual review: Manually tab through the page; some custom focus styles may be visible but not detected by this heuristic.
- Browser check limitation: Focus indicator detection checks computed outline, border, and shadow heuristically and can miss custom visual treatments.

Evidence:

- tag: a
- text: Alyson Bell
- step: 31
- detected_in: low_vision
- reason: The focused element did not expose an obvious outline, box-shadow, or border focus style in computed CSS.

### 42. Focused element may not show a visible focus indicator

- Issue type: focus_indicator_missing
- Rule: Focused element may not show a visible focus indicator
- Category: Low Vision
- Severity: high
- Why it matters: Keyboard users with low vision need a visible indicator to know which control currently has focus.
- Suggested fix: Provide a clear :focus or :focus-visible style with visible outline, border, or shadow.
- Manual review: Manually tab through the page; some custom focus styles may be visible but not detected by this heuristic.
- Browser check limitation: Focus indicator detection checks computed outline, border, and shadow heuristically and can miss custom visual treatments.

Evidence:

- tag: a
- text: Claire Joeckel
- step: 32
- detected_in: low_vision
- reason: The focused element did not expose an obvious outline, box-shadow, or border focus style in computed CSS.

### 43. Focused element may not show a visible focus indicator

- Issue type: focus_indicator_missing
- Rule: Focused element may not show a visible focus indicator
- Category: Low Vision
- Severity: high
- Why it matters: Keyboard users with low vision need a visible indicator to know which control currently has focus.
- Suggested fix: Provide a clear :focus or :focus-visible style with visible outline, border, or shadow.
- Manual review: Manually tab through the page; some custom focus styles may be visible but not detected by this heuristic.
- Browser check limitation: Focus indicator detection checks computed outline, border, and shadow heuristically and can miss custom visual treatments.

Evidence:

- tag: a
- text: Na Tang
- step: 33
- detected_in: low_vision
- reason: The focused element did not expose an obvious outline, box-shadow, or border focus style in computed CSS.

### 44. Focused element may not show a visible focus indicator

- Issue type: focus_indicator_missing
- Rule: Focused element may not show a visible focus indicator
- Category: Low Vision
- Severity: high
- Why it matters: Keyboard users with low vision need a visible indicator to know which control currently has focus.
- Suggested fix: Provide a clear :focus or :focus-visible style with visible outline, border, or shadow.
- Manual review: Manually tab through the page; some custom focus styles may be visible but not detected by this heuristic.
- Browser check limitation: Focus indicator detection checks computed outline, border, and shadow heuristically and can miss custom visual treatments.

Evidence:

- tag: a
- text: Send Jared an email
- step: 34
- detected_in: low_vision
- reason: The focused element did not expose an obvious outline, box-shadow, or border focus style in computed CSS.

### 45. Focused element may not show a visible focus indicator

- Issue type: focus_indicator_missing
- Rule: Focused element may not show a visible focus indicator
- Category: Low Vision
- Severity: high
- Why it matters: Keyboard users with low vision need a visible indicator to know which control currently has focus.
- Suggested fix: Provide a clear :focus or :focus-visible style with visible outline, border, or shadow.
- Manual review: Manually tab through the page; some custom focus styles may be visible but not detected by this heuristic.
- Browser check limitation: Focus indicator detection checks computed outline, border, and shadow heuristically and can miss custom visual treatments.

Evidence:

- tag: a
- text: Send Christopher an email
- step: 35
- detected_in: low_vision
- reason: The focused element did not expose an obvious outline, box-shadow, or border focus style in computed CSS.

### 46. Focused element may not show a visible focus indicator

- Issue type: focus_indicator_missing
- Rule: Focused element may not show a visible focus indicator
- Category: Low Vision
- Severity: high
- Why it matters: Keyboard users with low vision need a visible indicator to know which control currently has focus.
- Suggested fix: Provide a clear :focus or :focus-visible style with visible outline, border, or shadow.
- Manual review: Manually tab through the page; some custom focus styles may be visible but not detected by this heuristic.
- Browser check limitation: Focus indicator detection checks computed outline, border, and shadow heuristically and can miss custom visual treatments.

Evidence:

- tag: a
- text: Send Jonathan an email
- step: 36
- detected_in: low_vision
- reason: The focused element did not expose an obvious outline, box-shadow, or border focus style in computed CSS.

### 47. Focused element may not show a visible focus indicator

- Issue type: focus_indicator_missing
- Rule: Focused element may not show a visible focus indicator
- Category: Low Vision
- Severity: high
- Why it matters: Keyboard users with low vision need a visible indicator to know which control currently has focus.
- Suggested fix: Provide a clear :focus or :focus-visible style with visible outline, border, or shadow.
- Manual review: Manually tab through the page; some custom focus styles may be visible but not detected by this heuristic.
- Browser check limitation: Focus indicator detection checks computed outline, border, and shadow heuristically and can miss custom visual treatments.

Evidence:

- tag: a
- text: Send George an email
- step: 37
- detected_in: low_vision
- reason: The focused element did not expose an obvious outline, box-shadow, or border focus style in computed CSS.

### 48. Focused element may not show a visible focus indicator

- Issue type: focus_indicator_missing
- Rule: Focused element may not show a visible focus indicator
- Category: Low Vision
- Severity: high
- Why it matters: Keyboard users with low vision need a visible indicator to know which control currently has focus.
- Suggested fix: Provide a clear :focus or :focus-visible style with visible outline, border, or shadow.
- Manual review: Manually tab through the page; some custom focus styles may be visible but not detected by this heuristic.
- Browser check limitation: Focus indicator detection checks computed outline, border, and shadow heuristically and can miss custom visual treatments.

Evidence:

- tag: a
- text: Accessible Documents video-based course
- step: 38
- detected_in: low_vision
- reason: The focused element did not expose an obvious outline, box-shadow, or border focus style in computed CSS.

### 49. Focused element may not show a visible focus indicator

- Issue type: focus_indicator_missing
- Rule: Focused element may not show a visible focus indicator
- Category: Low Vision
- Severity: high
- Why it matters: Keyboard users with low vision need a visible indicator to know which control currently has focus.
- Suggested fix: Provide a clear :focus or :focus-visible style with visible outline, border, or shadow.
- Manual review: Manually tab through the page; some custom focus styles may be visible but not detected by this heuristic.
- Browser check limitation: Focus indicator detection checks computed outline, border, and shadow heuristically and can miss custom visual treatments.

Evidence:

- tag: a
- text: Send John an email
- step: 39
- detected_in: low_vision
- reason: The focused element did not expose an obvious outline, box-shadow, or border focus style in computed CSS.

### 50. Focused element may not show a visible focus indicator

- Issue type: focus_indicator_missing
- Rule: Focused element may not show a visible focus indicator
- Category: Low Vision
- Severity: high
- Why it matters: Keyboard users with low vision need a visible indicator to know which control currently has focus.
- Suggested fix: Provide a clear :focus or :focus-visible style with visible outline, border, or shadow.
- Manual review: Manually tab through the page; some custom focus styles may be visible but not detected by this heuristic.
- Browser check limitation: Focus indicator detection checks computed outline, border, and shadow heuristically and can miss custom visual treatments.

Evidence:

- tag: a
- text: conformance statements
- step: 40
- detected_in: low_vision
- reason: The focused element did not expose an obvious outline, box-shadow, or border focus style in computed CSS.

## Limitations

- This prototype runs static HTML checks plus a basic keyboard interaction audit.
- It does not replace a full human accessibility audit.
- Browser mode does not simulate a full screen reader, and accessible names are estimated.
- Low-vision browser checks are conservative heuristics and require manual review.

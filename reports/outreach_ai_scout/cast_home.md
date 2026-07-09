# A11yway Accessibility Report

## Summary

- Source: https://www.cast.org/
- Source type: url
- Issues found: 29
- Agents used: Keyboard-only student
- Checks run: html_form_labels, interactive_names, image_alt_text, heading_structure, page_metadata, media_accessibility, keyboard_focus_traversal, browser_dom_snapshot, rendered_color_contrast, zoom_reflow_200, focus_visibility

### Counts By Severity

- medium: 7
- high: 22

### Counts By Issue Type

- missing_image_alt: 5
- missing_form_label: 1
- low_contrast_text: 20
- zoom_fixed_width_content: 3

### Source Metadata

- Final URL: https://www.cast.org/
- Status code: 200
- Content type: text/html; charset=UTF-8

## Browser Mode Summary

- Analysis modes: static, browser, low_vision
- Browser audit success: true
- Checks run: keyboard_focus_traversal, browser_dom_snapshot
- Focus trace length: 50

## Browser Interaction Trace

| Step | Tag | Accessible name guess | ID/Name | Text/Href |
| ---: | --- | --- | --- | --- |
| 1 | button | Customize |  | Customize |
| 2 | button | Reject All |  | Reject All |
| 3 | button | Accept All |  | Accept All |
| 4 | a | Skip to main content |  | Skip to main content |
| 5 | button | webReader menu |  |  |
| 6 | a | Listen |  | Listen |
| 7 | a | UDL Guidelines |  | UDL Guidelines |
| 8 | a | AEM |  | AEM |
| 9 | a | CITES |  | CITES |
| 10 | a | Donate |  | Donate |
| 11 | a | Contact Us |  | Contact Us |
| 12 | button | Menu | main-menu-toggle | Menu |
| 13 | a | CAST logo |  | .cls-1{fill:#fff} |
| 14 | button | Open site search panel | search-overlay-toggle | Open site search panel |
| 15 | button | Open language translation panel |  | Open language translation panel |
| 16 | a | Link to the CAST store |  | Link to the CAST store |
| 17 | a | Discover how we innovate for learning |  | Discover how we innovate for learning |
| 18 | a | the power of Universal Design for Learning (UDL) |  | the power of Universal Design for Learning (UDL) |
| 19 | a | Discover UDL-Con: Live Online |  | Discover UDL-Con: Live Online |
| 20 | a | Learn more about UDL |  | Learn more about UDL |

Trace truncated: showing the first 20 of 50 steps.

### Browser Limitations

- Browser mode approximates keyboard interaction but does not simulate a full screen reader.
- Accessible names are estimated and require manual review.

## Low-Vision Checks

- Status: passed
- Checks run: rendered_color_contrast, zoom_reflow_200, focus_visibility
- Contrast samples analyzed: 69
- Viewport width for reflow check: 640
- Document scroll width: 640
- Horizontal overflow amount: 0
- Focus stops checked: 40
- Focus indicator concerns: 0

### Low-Vision Limitations

- Low-vision checks use browser-computed styles and conservative heuristics.
- Rendered color contrast checks do not prove full WCAG conformance.
- Zoom/reflow uses a narrow viewport approximation rather than a full zoom compliance test.
- Focus indicator detection may miss custom focus styles.

## Visual Proof

- Screenshot path: reports/outreach_ai_scout/visual/cast_home/page.png
- Focus path overlay path: reports/outreach_ai_scout/visual/cast_home/focus_path.html
- Focus points count: 50

- Focus overlay shows observed Tab stops in this browser run.
- It does not represent every assistive technology experience.

### What the AI Found

- Status: ok
- Mode: suggest_only
- Model: llama-3.3-70b-versatile

Potential accessibility barriers were identified on the CAST website.

1. AI-suggested observation: Some images may lack alternative text, which could hinder users who rely on screen readers or have visual impairments.
   Related evidence, if any: Multiple instances of images with empty or missing alt attributes were detected.
   Human review needed: true
   Confidence: AI-only

2. AI-suggested observation: A form control may be missing an accessible label, potentially causing issues for users who rely on screen readers or have visual impairments.
   Related evidence, if any: A textarea element was detected with no accessible label.
   Human review needed: true
   Confidence: AI-only

3. AI-suggested observation: Some text elements may have low contrast with their backgrounds, which could cause readability issues for users with visual impairments.
   Related evidence, if any: Multiple instances of text elements with low contrast were detected using conservative heuristics.
   Human review needed: true
   Confidence: AI-only

#### Outreach Notes

- We suggest reviewing the website's accessibility to ensure that all users can navigate and understand the content effectively.

#### AI Scout Limitations

- AI Scout findings are suggestions and need human review.
- AI Scout output is not a confirmed accessibility finding.
- AI Scout does not determine legal compliance, WCAG compliance, or screen-reader behavior.
- AI Scout output is not a needs human review accessibility finding.


## Issues Found

### 1. Image is missing useful alt text

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
- src: https://www.cast.org/wp-content/uploads/2024/12/AdobeStock_539905442-scaled.jpeg
- line: 652
- reason: Image is missing useful alt text.

```html
<img width="2560" height="641" src="https://www.cast.org/wp-content/uploads/2024/12/AdobeStock_539905442-scaled.jpeg" class="attachment-full size-full" alt="" decoding="async" fetchpriority="high" ...
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
- src: https://www.cast.org/wp-content/uploads/2026/01/udl-con-live-online-square-800x800.png
- line: 673
- reason: Image is missing useful alt text.

```html
<img width="800" height="800" src="https://www.cast.org/wp-content/uploads/2026/01/udl-con-live-online-square-800x800.png" class="attachment-1-1-medium size-1-1-medium" alt="" decoding="async" srcs...
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
- src: https://www.cast.org/wp-content/uploads/2025/11/ai-brain-square-crop-friendly.png
- line: 832
- reason: Image is missing useful alt text.

```html
<img width="800" height="800" src="https://www.cast.org/wp-content/uploads/2025/11/ai-brain-square-crop-friendly.png" class="attachment-1-1-medium size-1-1-medium" alt="" decoding="async" loading="...
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
- src: https://www.cast.org/wp-content/uploads/2026/03/mailinglist-square-16x9-crop-600x600.png
- line: 848
- reason: Image is missing useful alt text.

```html
<img width="600" height="600" src="https://www.cast.org/wp-content/uploads/2026/03/mailinglist-square-16x9-crop-600x600.png" class="attachment-1-1-medium-alt size-1-1-medium-alt" alt="" decoding="a...
```

### 5. Form control is missing an accessible label

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
- id: g-recaptcha-response-100000
- name: g-recaptcha-response
- line: 798
- detected_in: browser_dom
- reason: Form control has no accessible label.

```html
<textarea id="g-recaptcha-response-100000" name="g-recaptcha-response" class="g-recaptcha-response" style="width: 250px; height: 40px; border: 1px solid rgb(193, 193, 193); margin: 10px 25px; paddi...
```

### 6. Image is missing useful alt text

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
- src: https://cdn-cookieyes.com/assets/images/close.svg
- line: 78
- detected_in: browser_dom
- reason: Image is missing useful alt text.

```html
<img alt="" src="https://cdn-cookieyes.com/assets/images/close.svg">
```

### 7. Rendered text may have low contrast

- Issue type: low_contrast_text
- Rule: Rendered text may have low contrast
- Category: Low Vision
- Severity: high
- Why it matters: Low-vision readers may not be able to read text when the computed foreground and background colors are too similar.
- Suggested fix: Increase foreground/background contrast and confirm the final design with manual review.
- Manual review: Confirm the sampled colors match what users actually see, especially over gradients, images, and layered components.
- Browser check limitation: The check samples browser-computed colors and does not prove full WCAG color contrast compliance.

Evidence:

- tag: li
- text: UDL Guidelines
- detected_in: low_vision
- reason: Computed foreground/background contrast is below the conservative 4.5:1 review threshold.

### 8. Rendered text may have low contrast

- Issue type: low_contrast_text
- Rule: Rendered text may have low contrast
- Category: Low Vision
- Severity: high
- Why it matters: Low-vision readers may not be able to read text when the computed foreground and background colors are too similar.
- Suggested fix: Increase foreground/background contrast and confirm the final design with manual review.
- Manual review: Confirm the sampled colors match what users actually see, especially over gradients, images, and layered components.
- Browser check limitation: The check samples browser-computed colors and does not prove full WCAG color contrast compliance.

Evidence:

- tag: li
- text: AEM
- detected_in: low_vision
- reason: Computed foreground/background contrast is below the conservative 4.5:1 review threshold.

### 9. Rendered text may have low contrast

- Issue type: low_contrast_text
- Rule: Rendered text may have low contrast
- Category: Low Vision
- Severity: high
- Why it matters: Low-vision readers may not be able to read text when the computed foreground and background colors are too similar.
- Suggested fix: Increase foreground/background contrast and confirm the final design with manual review.
- Manual review: Confirm the sampled colors match what users actually see, especially over gradients, images, and layered components.
- Browser check limitation: The check samples browser-computed colors and does not prove full WCAG color contrast compliance.

Evidence:

- tag: li
- text: CITES
- detected_in: low_vision
- reason: Computed foreground/background contrast is below the conservative 4.5:1 review threshold.

### 10. Rendered text may have low contrast

- Issue type: low_contrast_text
- Rule: Rendered text may have low contrast
- Category: Low Vision
- Severity: high
- Why it matters: Low-vision readers may not be able to read text when the computed foreground and background colors are too similar.
- Suggested fix: Increase foreground/background contrast and confirm the final design with manual review.
- Manual review: Confirm the sampled colors match what users actually see, especially over gradients, images, and layered components.
- Browser check limitation: The check samples browser-computed colors and does not prove full WCAG color contrast compliance.

Evidence:

- tag: li
- text: Donate
- detected_in: low_vision
- reason: Computed foreground/background contrast is below the conservative 4.5:1 review threshold.

### 11. Rendered text may have low contrast

- Issue type: low_contrast_text
- Rule: Rendered text may have low contrast
- Category: Low Vision
- Severity: high
- Why it matters: Low-vision readers may not be able to read text when the computed foreground and background colors are too similar.
- Suggested fix: Increase foreground/background contrast and confirm the final design with manual review.
- Manual review: Confirm the sampled colors match what users actually see, especially over gradients, images, and layered components.
- Browser check limitation: The check samples browser-computed colors and does not prove full WCAG color contrast compliance.

Evidence:

- tag: li
- text: Contact Us
- detected_in: low_vision
- reason: Computed foreground/background contrast is below the conservative 4.5:1 review threshold.

### 12. Rendered text may have low contrast

- Issue type: low_contrast_text
- Rule: Rendered text may have low contrast
- Category: Low Vision
- Severity: high
- Why it matters: Low-vision readers may not be able to read text when the computed foreground and background colors are too similar.
- Suggested fix: Increase foreground/background contrast and confirm the final design with manual review.
- Manual review: Confirm the sampled colors match what users actually see, especially over gradients, images, and layered components.
- Browser check limitation: The check samples browser-computed colors and does not prove full WCAG color contrast compliance.

Evidence:

- tag: button
- text: Menu
- detected_in: low_vision
- reason: Computed foreground/background contrast is below the conservative 4.5:1 review threshold.

### 13. Rendered text may have low contrast

- Issue type: low_contrast_text
- Rule: Rendered text may have low contrast
- Category: Low Vision
- Severity: high
- Why it matters: Low-vision readers may not be able to read text when the computed foreground and background colors are too similar.
- Suggested fix: Increase foreground/background contrast and confirm the final design with manual review.
- Manual review: Confirm the sampled colors match what users actually see, especially over gradients, images, and layered components.
- Browser check limitation: The check samples browser-computed colors and does not prove full WCAG color contrast compliance.

Evidence:

- tag: button
- text: Open site search panel
- detected_in: low_vision
- reason: Computed foreground/background contrast is below the conservative 4.5:1 review threshold.

### 14. Rendered text may have low contrast

- Issue type: low_contrast_text
- Rule: Rendered text may have low contrast
- Category: Low Vision
- Severity: high
- Why it matters: Low-vision readers may not be able to read text when the computed foreground and background colors are too similar.
- Suggested fix: Increase foreground/background contrast and confirm the final design with manual review.
- Manual review: Confirm the sampled colors match what users actually see, especially over gradients, images, and layered components.
- Browser check limitation: The check samples browser-computed colors and does not prove full WCAG color contrast compliance.

Evidence:

- tag: button
- text: Open language translation panel
- detected_in: low_vision
- reason: Computed foreground/background contrast is below the conservative 4.5:1 review threshold.

### 15. Rendered text may have low contrast

- Issue type: low_contrast_text
- Rule: Rendered text may have low contrast
- Category: Low Vision
- Severity: high
- Why it matters: Low-vision readers may not be able to read text when the computed foreground and background colors are too similar.
- Suggested fix: Increase foreground/background contrast and confirm the final design with manual review.
- Manual review: Confirm the sampled colors match what users actually see, especially over gradients, images, and layered components.
- Browser check limitation: The check samples browser-computed colors and does not prove full WCAG color contrast compliance.

Evidence:

- tag: a
- text: Link to the CAST store
- detected_in: low_vision
- reason: Computed foreground/background contrast is below the conservative 4.5:1 review threshold.

### 16. Rendered text may have low contrast

- Issue type: low_contrast_text
- Rule: Rendered text may have low contrast
- Category: Low Vision
- Severity: high
- Why it matters: Low-vision readers may not be able to read text when the computed foreground and background colors are too similar.
- Suggested fix: Increase foreground/background contrast and confirm the final design with manual review.
- Manual review: Confirm the sampled colors match what users actually see, especially over gradients, images, and layered components.
- Browser check limitation: The check samples browser-computed colors and does not prove full WCAG color contrast compliance.

Evidence:

- tag: h1
- text: Until learning has no limits ®
- detected_in: low_vision
- reason: Computed foreground/background contrast is below the conservative 4.5:1 review threshold.

### 17. Rendered text may have low contrast

- Issue type: low_contrast_text
- Rule: Rendered text may have low contrast
- Category: Low Vision
- Severity: high
- Why it matters: Low-vision readers may not be able to read text when the computed foreground and background colors are too similar.
- Suggested fix: Increase foreground/background contrast and confirm the final design with manual review.
- Manual review: Confirm the sampled colors match what users actually see, especially over gradients, images, and layered components.
- Browser check limitation: The check samples browser-computed colors and does not prove full WCAG color contrast compliance.

Evidence:

- tag: p
- text: Until learning has no limits ®
- detected_in: low_vision
- reason: Computed foreground/background contrast is below the conservative 4.5:1 review threshold.

### 18. Rendered text may have low contrast

- Issue type: low_contrast_text
- Rule: Rendered text may have low contrast
- Category: Low Vision
- Severity: high
- Why it matters: Low-vision readers may not be able to read text when the computed foreground and background colors are too similar.
- Suggested fix: Increase foreground/background contrast and confirm the final design with manual review.
- Manual review: Confirm the sampled colors match what users actually see, especially over gradients, images, and layered components.
- Browser check limitation: The check samples browser-computed colors and does not prove full WCAG color contrast compliance.

Evidence:

- tag: p
- text: At CAST, we know that barriers to learning are in education design, not individual learners. We invented UDL to help bre
- detected_in: low_vision
- reason: Computed foreground/background contrast is below the conservative 4.5:1 review threshold.

### 19. Rendered text may have low contrast

- Issue type: low_contrast_text
- Rule: Rendered text may have low contrast
- Category: Low Vision
- Severity: high
- Why it matters: Low-vision readers may not be able to read text when the computed foreground and background colors are too similar.
- Suggested fix: Increase foreground/background contrast and confirm the final design with manual review.
- Manual review: Confirm the sampled colors match what users actually see, especially over gradients, images, and layered components.
- Browser check limitation: The check samples browser-computed colors and does not prove full WCAG color contrast compliance.

Evidence:

- tag: a
- text: Contact Us
- detected_in: low_vision
- reason: Computed foreground/background contrast is below the conservative 4.5:1 review threshold.

### 20. Rendered text may have low contrast

- Issue type: low_contrast_text
- Rule: Rendered text may have low contrast
- Category: Low Vision
- Severity: high
- Why it matters: Low-vision readers may not be able to read text when the computed foreground and background colors are too similar.
- Suggested fix: Increase foreground/background contrast and confirm the final design with manual review.
- Manual review: Confirm the sampled colors match what users actually see, especially over gradients, images, and layered components.
- Browser check limitation: The check samples browser-computed colors and does not prove full WCAG color contrast compliance.

Evidence:

- tag: a
- text: Donate Now
- detected_in: low_vision
- reason: Computed foreground/background contrast is below the conservative 4.5:1 review threshold.

### 21. Rendered text may have low contrast

- Issue type: low_contrast_text
- Rule: Rendered text may have low contrast
- Category: Low Vision
- Severity: high
- Why it matters: Low-vision readers may not be able to read text when the computed foreground and background colors are too similar.
- Suggested fix: Increase foreground/background contrast and confirm the final design with manual review.
- Manual review: Confirm the sampled colors match what users actually see, especially over gradients, images, and layered components.
- Browser check limitation: The check samples browser-computed colors and does not prove full WCAG color contrast compliance.

Evidence:

- tag: a
- text: Learn More about ReadSpeaker
- detected_in: low_vision
- reason: Computed foreground/background contrast is below the conservative 4.5:1 review threshold.

### 22. Rendered text may have low contrast

- Issue type: low_contrast_text
- Rule: Rendered text may have low contrast
- Category: Low Vision
- Severity: high
- Why it matters: Low-vision readers may not be able to read text when the computed foreground and background colors are too similar.
- Suggested fix: Increase foreground/background contrast and confirm the final design with manual review.
- Manual review: Confirm the sampled colors match what users actually see, especially over gradients, images, and layered components.
- Browser check limitation: The check samples browser-computed colors and does not prove full WCAG color contrast compliance.

Evidence:

- tag: a
- text: Join our community
- detected_in: low_vision
- reason: Computed foreground/background contrast is below the conservative 4.5:1 review threshold.

### 23. Rendered text may have low contrast

- Issue type: low_contrast_text
- Rule: Rendered text may have low contrast
- Category: Low Vision
- Severity: high
- Why it matters: Low-vision readers may not be able to read text when the computed foreground and background colors are too similar.
- Suggested fix: Increase foreground/background contrast and confirm the final design with manual review.
- Manual review: Confirm the sampled colors match what users actually see, especially over gradients, images, and layered components.
- Browser check limitation: The check samples browser-computed colors and does not prove full WCAG color contrast compliance.

Evidence:

- tag: a
- text: Subscribe to our newsletter
- detected_in: low_vision
- reason: Computed foreground/background contrast is below the conservative 4.5:1 review threshold.

### 24. Rendered text may have low contrast

- Issue type: low_contrast_text
- Rule: Rendered text may have low contrast
- Category: Low Vision
- Severity: high
- Why it matters: Low-vision readers may not be able to read text when the computed foreground and background colors are too similar.
- Suggested fix: Increase foreground/background contrast and confirm the final design with manual review.
- Manual review: Confirm the sampled colors match what users actually see, especially over gradients, images, and layered components.
- Browser check limitation: The check samples browser-computed colors and does not prove full WCAG color contrast compliance.

Evidence:

- tag: a
- text: UDL Guidelines
- detected_in: low_vision
- reason: Computed foreground/background contrast is below the conservative 4.5:1 review threshold.

### 25. Rendered text may have low contrast

- Issue type: low_contrast_text
- Rule: Rendered text may have low contrast
- Category: Low Vision
- Severity: high
- Why it matters: Low-vision readers may not be able to read text when the computed foreground and background colors are too similar.
- Suggested fix: Increase foreground/background contrast and confirm the final design with manual review.
- Manual review: Confirm the sampled colors match what users actually see, especially over gradients, images, and layered components.
- Browser check limitation: The check samples browser-computed colors and does not prove full WCAG color contrast compliance.

Evidence:

- tag: a
- text: Careers
- detected_in: low_vision
- reason: Computed foreground/background contrast is below the conservative 4.5:1 review threshold.

### 26. Rendered text may have low contrast

- Issue type: low_contrast_text
- Rule: Rendered text may have low contrast
- Category: Low Vision
- Severity: high
- Why it matters: Low-vision readers may not be able to read text when the computed foreground and background colors are too similar.
- Suggested fix: Increase foreground/background contrast and confirm the final design with manual review.
- Manual review: Confirm the sampled colors match what users actually see, especially over gradients, images, and layered components.
- Browser check limitation: The check samples browser-computed colors and does not prove full WCAG color contrast compliance.

Evidence:

- tag: a
- text: Financial information
- detected_in: low_vision
- reason: Computed foreground/background contrast is below the conservative 4.5:1 review threshold.

### 27. Fixed or wide content may prevent reflow

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
- text: We value your privacy We use cookies to enhance your browsing experience, serve 
- detected_in: low_vision
- reason: A rendered element is wider than the narrow viewport or uses a large fixed pixel width.

### 28. Fixed or wide content may prevent reflow

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
- text: We value your privacy We use cookies to enhance your browsing experience, serve 
- detected_in: low_vision
- reason: A rendered element is wider than the narrow viewport or uses a large fixed pixel width.

### 29. Fixed or wide content may prevent reflow

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
- text: We value your privacy We use cookies to enhance your browsing experience, serve 
- detected_in: low_vision
- reason: A rendered element is wider than the narrow viewport or uses a large fixed pixel width.

## Limitations

- This prototype runs static HTML checks plus a basic keyboard interaction audit.
- It does not replace a full human accessibility audit.
- Browser mode does not simulate a full screen reader, and accessible names are estimated.
- Low-vision browser checks are conservative heuristics and require manual review.

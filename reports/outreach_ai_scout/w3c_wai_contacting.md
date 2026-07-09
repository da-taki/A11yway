# A11yway Accessibility Report

## Summary

- Source: https://www.w3.org/WAI/about/contacting/
- Source type: url
- Issues found: 23
- Agents used: Keyboard-only student
- Checks run: html_form_labels, interactive_names, image_alt_text, heading_structure, page_metadata, media_accessibility, keyboard_focus_traversal, browser_dom_snapshot, rendered_color_contrast, zoom_reflow_200, focus_visibility

### Counts By Severity

- high: 20
- medium: 3

### Counts By Issue Type

- missing_button_name: 1
- browser_focused_control_missing_name: 1
- low_contrast_text: 16
- zoom_fixed_width_content: 3
- focus_indicator_missing: 2

### Source Metadata

- Final URL: https://www.w3.org/WAI/about/contacting/
- Status code: 200
- Content type: text/html; charset=utf-8

## Browser Mode Summary

- Analysis modes: static, browser, low_vision
- Browser audit success: true
- Checks run: keyboard_focus_traversal, browser_dom_snapshot
- Focus trace length: 60

## Browser Interaction Trace

| Step | Tag | Accessible name guess | ID/Name | Text/Href |
| ---: | --- | --- | --- | --- |
| 1 | a | Skip to Content |  | Skip to Content |
| 2 | a | Change Text Size or Colors |  | Change Text Size or Colors |
| 3 | a | All Translations |  | All Translations |
| 4 | a | W3C homepage |  | W3C homepage |
| 5 | a | Web Accessibility Initiative (WAI) homepage |  | Web Accessibility Initiative (WAI) homepage |
| 6 | a | Get Involved |  | Get Involved |
| 7 | a | About W3C WAI |  | About W3C WAI |
| 8 | input | Search | header-search |  |
| 9 | button |  |  |  |
| 10 | a | Accessibility Fundamentals |  | Accessibility Fundamentals |
| 11 | a | Planning & Policies |  | Planning & Policies |
| 12 | a | Design & Develop |  | Design & Develop |
| 13 | a | Test & Evaluate |  | Test & Evaluate |
| 14 | a | Teach & Advocate |  | Teach & Advocate |
| 15 | a | Standards/Guidelines |  | Standards/Guidelines |
| 16 | a | Home |  | Home |
| 17 | a | About W3C WAI |  | About W3C WAI |
| 18 | a | Contact WAI |  | Contact WAI |
| 19 | a | About WAI |  | About WAI |
| 20 | a | What We're Working On |  | What We're Working On |

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
- Focus indicator concerns: 2

### Low-Vision Limitations

- Low-vision checks use browser-computed styles and conservative heuristics.
- Rendered color contrast checks do not prove full WCAG conformance.
- Zoom/reflow uses a narrow viewport approximation rather than a full zoom compliance test.
- Focus indicator detection may miss custom focus styles.

## Visual Proof

- Screenshot path: reports/outreach_ai_scout/visual/w3c_wai_contacting/page.png
- Focus path overlay path: reports/outreach_ai_scout/visual/w3c_wai_contacting/focus_path.html
- Focus points count: 60

- Focus overlay shows observed Tab stops in this browser run.
- It does not represent every assistive technology experience.

### What the AI Found

- Status: ok
- Mode: suggest_only
- Model: llama-3.3-70b-versatile

Possible accessibility barriers found on the W3C WAI page, including low contrast text and missing button names

1. AI-suggested observation: Some text elements may have insufficient contrast with the background, potentially causing readability issues for users with visual impairments
   Related evidence, if any: Multiple instances of low contrast text were detected, including 'Accessibility Fundamentals', 'Planning & Policies', and 'Design & Develop'
   Human review needed: true
   Confidence: AI-only

2. AI-suggested observation: A button is missing an accessible name, which could cause issues for users relying on screen readers or other assistive technologies
   Related evidence, if any: A button with no visible text, aria-label, title, or image alt text was detected
   Human review needed: true
   Confidence: AI-only

3. AI-suggested observation: A focused control has no accessible name, which could cause issues for users relying on keyboard navigation
   Related evidence, if any: A focused control with no label, text, aria-label, or other usable name was detected at step 9
   Human review needed: true
   Confidence: AI-only

#### Outreach Notes

- We would appreciate the opportunity to discuss these potential accessibility barriers with your team and explore ways to improve the overall accessibility of the W3C WAI page

#### AI Scout Limitations

- AI Scout findings are suggestions and need human review.
- AI Scout output is not a confirmed accessibility finding.
- AI Scout does not determine legal compliance, WCAG compliance, or screen-reader behavior.
- AI Scout findings are suggestions and need human review
- AI Scout output is not a needs human review accessibility finding
- AI Scout does not determine legal compliance, WCAG compliance, or screen-reader behavior


## Issues Found

### 1. Button is missing an accessible name

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
- line: 82
- reason: Button has no visible text, aria-label, title, or image alt text.

```html
<button class="button button-icon button-nobg button-noborder">
```

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
- step: 9
- detected_in: browser_interaction
- reason: A keyboard user reached this control, but it has no label, text, aria-label, or other usable name.

### 3. Rendered text may have low contrast

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
- text: Accessibility Fundamentals
- detected_in: low_vision
- reason: Computed foreground/background contrast is below the conservative 4.5:1 review threshold.

### 4. Rendered text may have low contrast

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
- text: Planning & Policies
- detected_in: low_vision
- reason: Computed foreground/background contrast is below the conservative 4.5:1 review threshold.

### 5. Rendered text may have low contrast

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
- text: Design & Develop
- detected_in: low_vision
- reason: Computed foreground/background contrast is below the conservative 4.5:1 review threshold.

### 6. Rendered text may have low contrast

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
- text: Test & Evaluate
- detected_in: low_vision
- reason: Computed foreground/background contrast is below the conservative 4.5:1 review threshold.

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
- text: Teach & Advocate
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
- text: Standards/Guidelines
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
- text: About WAI
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
- text: What We're Working On
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
- text: Participate in WAI
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

- tag: li
- text: Groups
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

- tag: li
- text: Translate
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

- tag: li
- text: Support WAI
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

- tag: li
- text: Contact WAI
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

- tag: li
- text: Projects
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

- tag: li
- text: Accessibility Statement
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

- tag: li
- text: Use WAI Material
- detected_in: low_vision
- reason: Computed foreground/background contrast is below the conservative 4.5:1 review threshold.

### 19. Fixed or wide content may prevent reflow

- Issue type: zoom_fixed_width_content
- Rule: Fixed or wide content may prevent reflow
- Category: Low Vision
- Severity: medium
- Why it matters: Large fixed-width elements can force horizontal scrolling and hide content when users zoom or use narrow windows.
- Suggested fix: Replace fixed-width layout with responsive sizing such as max-width: 100%.
- Manual review: Confirm whether the wide element is essential and whether all content remains reachable without two-dimensional scrolling.
- Browser check limitation: The check flags obvious wide rendered elements and fixed pixel widths; it may miss complex layout problems.

Evidence:

- tag: nav
- id: controls
- text: Skip to Content Change Text Size or Colors All Translations
- detected_in: low_vision
- reason: A rendered element is wider than the narrow viewport or uses a large fixed pixel width.

### 20. Fixed or wide content may prevent reflow

- Issue type: zoom_fixed_width_content
- Rule: Fixed or wide content may prevent reflow
- Category: Low Vision
- Severity: medium
- Why it matters: Large fixed-width elements can force horizontal scrolling and hide content when users zoom or use narrow windows.
- Suggested fix: Replace fixed-width layout with responsive sizing such as max-width: 100%.
- Manual review: Confirm whether the wide element is essential and whether all content remains reachable without two-dimensional scrolling.
- Browser check limitation: The check flags obvious wide rendered elements and fixed pixel widths; it may miss complex layout problems.

Evidence:

- tag: ul
- text: Skip to Content Change Text Size or Colors All Translations
- detected_in: low_vision
- reason: A rendered element is wider than the narrow viewport or uses a large fixed pixel width.

### 21. Fixed or wide content may prevent reflow

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
- id: site-header
- text: MENU
- detected_in: low_vision
- reason: A rendered element is wider than the narrow viewport or uses a large fixed pixel width.

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
- text: Home
- step: 16
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
- text: About W3C WAI
- step: 17
- detected_in: low_vision
- reason: The focused element did not expose an obvious outline, box-shadow, or border focus style in computed CSS.

## Limitations

- This prototype runs static HTML checks plus a basic keyboard interaction audit.
- It does not replace a full human accessibility audit.
- Browser mode does not simulate a full screen reader, and accessible names are estimated.
- Low-vision browser checks are conservative heuristics and require manual review.

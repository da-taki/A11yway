# A11yway Accessibility Report

## Summary

- Source: https://knowbility.org/contact/
- Source type: url
- Issues found: 3
- Agents used: Keyboard-only student
- Checks run: html_form_labels, interactive_names, image_alt_text, heading_structure, page_metadata, media_accessibility, keyboard_focus_traversal, browser_dom_snapshot, rendered_color_contrast, zoom_reflow_200, focus_visibility

### Counts By Severity

- medium: 3

### Counts By Issue Type

- zoom_fixed_width_content: 3

### Source Metadata

- Final URL: https://knowbility.org/contact/
- Status code: 200
- Content type: text/html; charset=UTF-8

## Browser Mode Summary

- Analysis modes: static, browser, low_vision
- Browser audit success: true
- Checks run: keyboard_focus_traversal, browser_dom_snapshot
- Focus trace length: 47

## Browser Interaction Trace

| Step | Tag | Accessible name guess | ID/Name | Text/Href |
| ---: | --- | --- | --- | --- |
| 1 | a | Skip to Main Content |  | Skip to Main Content |
| 2 | a | Knowbility |  | https://knowbility.org |
| 3 | input | Search | search-query |  |
| 4 | button | Search |  |  |
| 5 | a | Donate |  | Donate |
| 6 | a | Programs |  | Programs |
| 7 | a | Services |  | Services |
| 8 | a | Learning Center |  | Learning Center |
| 9 | a | Blog |  | Blog |
| 10 | a | About Us |  | About Us |
| 11 | a | Contact Us |  | Contact Us |
| 12 | a | HOME |  | HOME |
| 13 | a | 512-527-3138 |  | 512-527-3138 |
| 14 | a | knowbility@knowbility.org |  | knowbility@knowbility.org |
| 15 | input | Name Required | name |  |
| 16 | input | Company | company |  |
| 17 | input | Email Required | email |  |
| 18 | input | Phone | pne-real |  |
| 19 | input | inquiring about accessibility services and training | interest_services-training |  |
| 20 | textarea | Message Required | message |  |

Trace truncated: showing the first 20 of 47 steps.

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
- Focus indicator concerns: 0

### Low-Vision Limitations

- Low-vision checks use browser-computed styles and conservative heuristics.
- Rendered color contrast checks do not prove full WCAG conformance.
- Zoom/reflow uses a narrow viewport approximation rather than a full zoom compliance test.
- Focus indicator detection may miss custom focus styles.

## Visual Proof

- Screenshot path: reports/outreach_ai_scout/visual/knowbility_contact/page.png
- Focus path overlay path: reports/outreach_ai_scout/visual/knowbility_contact/focus_path.html
- Focus points count: 47

- Focus overlay shows observed Tab stops in this browser run.
- It does not represent every assistive technology experience.

### What the AI Found

- Status: ok
- Mode: suggest_only
- Model: llama-3.3-70b-versatile

Possible barriers found on the Knowbility contact page, including fixed or wide content that may prevent reflow.

1. AI-suggested observation: The 'Skip to Main Content' link may have a fixed width that could cause issues with reflow on smaller screens.
   Related evidence, if any: Detected in low_vision mode, with a rendered element wider than the narrow viewport or using a large fixed pixel width.
   Human review needed: true
   Confidence: AI-only

2. AI-suggested observation: The header element containing 'MENU' may have a fixed width that could prevent reflow on smaller screens.
   Related evidence, if any: Detected in low_vision mode, with a rendered element wider than the narrow viewport or using a large fixed pixel width.
   Human review needed: true
   Confidence: AI-only

3. AI-suggested observation: The 'Donate' button may have a fixed width that could cause issues with reflow on smaller screens.
   Related evidence, if any: Detected in low_vision mode, with a rendered element wider than the narrow viewport or using a large fixed pixel width.
   Human review needed: true
   Confidence: AI-only

#### Outreach Notes

- We suggest reviewing the contact page for potential accessibility barriers, particularly regarding fixed or wide content that may prevent reflow on smaller screens.

#### AI Scout Limitations

- AI Scout findings are suggestions and need human review.
- AI Scout output is not a confirmed accessibility finding.
- AI Scout does not determine legal compliance, WCAG compliance, or screen-reader behavior.
- AI Scout output is not a needs human review accessibility finding.


## Issues Found

### 1. Fixed or wide content may prevent reflow

- Issue type: zoom_fixed_width_content
- Rule: Fixed or wide content may prevent reflow
- Category: Low Vision
- Severity: medium
- Why it matters: Large fixed-width elements can force horizontal scrolling and hide content when users zoom or use narrow windows.
- Suggested fix: Replace fixed-width layout with responsive sizing such as max-width: 100%.
- Manual review: Confirm whether the wide element is essential and whether all content remains reachable without two-dimensional scrolling.
- Browser check limitation: The check flags obvious wide rendered elements and fixed pixel widths; it may miss complex layout problems.

Evidence:

- tag: a
- text: Skip to Main Content
- detected_in: low_vision
- reason: A rendered element is wider than the narrow viewport or uses a large fixed pixel width.

### 2. Fixed or wide content may prevent reflow

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
- text: MENU
- detected_in: low_vision
- reason: A rendered element is wider than the narrow viewport or uses a large fixed pixel width.

### 3. Fixed or wide content may prevent reflow

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
- text: Donate
- detected_in: low_vision
- reason: A rendered element is wider than the narrow viewport or uses a large fixed pixel width.

## Limitations

- This prototype runs static HTML checks plus a basic keyboard interaction audit.
- It does not replace a full human accessibility audit.
- Browser mode does not simulate a full screen reader, and accessible names are estimated.
- Low-vision browser checks are conservative heuristics and require manual review.

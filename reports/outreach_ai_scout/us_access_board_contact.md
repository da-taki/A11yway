# A11yway Accessibility Report

## Summary

- Source: https://www.access-board.gov/contact/
- Source type: url
- Issues found: 4
- Agents used: Keyboard-only student
- Checks run: html_form_labels, interactive_names, image_alt_text, heading_structure, page_metadata, media_accessibility, keyboard_focus_traversal, browser_dom_snapshot, rendered_color_contrast, zoom_reflow_200, focus_visibility

### Counts By Severity

- low: 1
- medium: 3

### Counts By Issue Type

- multiple_h1: 1
- zoom_fixed_width_content: 3

### Source Metadata

- Final URL: https://www.access-board.gov/contact/
- Status code: 200
- Content type: text/html; charset=utf-8

## Browser Mode Summary

- Analysis modes: static, browser, low_vision
- Browser audit success: true
- Checks run: keyboard_focus_traversal, browser_dom_snapshot
- Focus trace length: 5

## Browser Interaction Trace

| Step | Tag | Accessible name guess | ID/Name | Text/Href |
| ---: | --- | --- | --- | --- |
| 1 | button | Close subscription dialog |  |  |
| 2 | input | stay connected - enter your email address to receive updates from the US Access Board | prefix-emailInput |  |
| 3 | input | Subscribe | prefix-submitButton |  |
| 4 | button | Not Interested | prefix-dismissButton | Not Interested |
| 5 | button | Remind Me Later | prefix-laterButton | Remind Me Later |

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

- Screenshot path: reports/outreach_ai_scout/visual/us_access_board_contact/page.png
- Focus path overlay path: reports/outreach_ai_scout/visual/us_access_board_contact/focus_path.html
- Focus points count: 5

- Focus overlay shows observed Tab stops in this browser run.
- It does not represent every assistive technology experience.

### What the AI Found

- Status: ok
- Mode: suggest_only
- Model: llama-3.3-70b-versatile

Possible accessibility barriers were identified on the U.S. Access Board contact page.

1. AI-suggested observation: The page may have multiple h1 headings, which could affect the structure and readability of the content for some users.
   Related evidence, if any: Multiple h1 headings were detected in the page's HTML structure.
   Human review needed: true
   Confidence: AI-only

2. AI-suggested observation: Some content on the page may not reflow properly when the viewport is narrowed, potentially causing issues for users with low vision or those who prefer a narrower viewport.
   Related evidence, if any: Elements with fixed widths were detected in the page's layout, which may prevent proper reflow.
   Human review needed: true
   Confidence: unclear

#### Outreach Notes

- We suggest reviewing the page's structure and layout to ensure that they are accessible and usable for all users, including those with disabilities.

#### AI Scout Limitations

- AI Scout findings are suggestions and need human review.
- AI Scout output is not a confirmed accessibility finding.
- AI Scout does not determine legal compliance, WCAG compliance, or screen-reader behavior.
- AI Scout output is not a needs human review accessibility finding.


## Issues Found

### 1. Page has multiple h1 headings

- Issue type: multiple_h1
- Rule: Page has multiple h1 headings
- Category: Headings & Structure
- Severity: low
- Why it matters: Several h1 headings make it harder for students to identify the single main topic of the page.
- Suggested fix: Use one main h1 for the page purpose, then organize sections with h2 and lower headings.
- Manual review: Some layouts intentionally use sectioned h1 elements; judge readability.
- Static check limitation: Static HTML cannot evaluate how the headings are presented visually.

Evidence:

- tag: h1
- reason: Document has multiple h1 headings.

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

- tag: div
- text: Skip to main content An official website of the United States government Here's 
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
- text: An official website of the United States government Here's how you know
- detected_in: low_vision
- reason: A rendered element is wider than the narrow viewport or uses a large fixed pixel width.

### 4. Fixed or wide content may prevent reflow

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
- text: An official website of the United States government Here's how you know
- detected_in: low_vision
- reason: A rendered element is wider than the narrow viewport or uses a large fixed pixel width.

## Limitations

- This prototype runs static HTML checks plus a basic keyboard interaction audit.
- It does not replace a full human accessibility audit.
- Browser mode does not simulate a full screen reader, and accessible names are estimated.
- Low-vision browser checks are conservative heuristics and require manual review.

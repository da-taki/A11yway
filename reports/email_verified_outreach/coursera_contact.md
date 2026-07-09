# A11yway Accessibility Report

## Summary

- Source: https://www.coursera.org/about/contact
- Source type: url
- Issues found: 15
- Agents used: Keyboard-only student
- Checks run: html_form_labels, interactive_names, image_alt_text, heading_structure, page_metadata, media_accessibility, keyboard_focus_traversal, browser_dom_snapshot, rendered_color_contrast, zoom_reflow_200, focus_visibility

### Counts By Severity

- medium: 8
- high: 7

### Counts By Issue Type

- generic_link_text: 4
- skipped_heading_level: 1
- low_contrast_text: 4
- zoom_fixed_width_content: 3
- focus_indicator_missing: 3

### Source Metadata

- Final URL: https://www.coursera.org/about/contact
- Status code: 200
- Content type: text/html

## Browser Mode Summary

- Analysis modes: static, browser, low_vision
- Browser audit success: true
- Checks run: keyboard_focus_traversal, browser_dom_snapshot
- Focus trace length: 60

## Browser Interaction Trace

| Step | Tag | Accessible name guess | ID/Name | Text/Href |
| ---: | --- | --- | --- | --- |
| 1 | a | For Individuals |  | For Individuals |
| 2 | a | For Businesses |  | For Businesses |
| 3 | a | For Universities |  | For Universities |
| 4 | a | For Governments |  | For Governments |
| 5 | a | Coursera |  | / |
| 6 | button | Explore our catalog |  | Explore |
| 7 | a | Degrees |  | Degrees |
| 8 | input | Search catalog | search-autocomplete-input |  |
| 9 | button | Search |  |  |
| 10 | a | Log In |  | Log In |
| 11 | a | Join for Free |  | Join for Free |
| 12 | a | Learner Help Center |  | Learner Help Center |
| 13 | a | Check and update your email communication preferences |  | Check and update your email communication preferences |
| 14 | a | Verify your ID |  | Verify your ID |
| 15 | a | How to solve problems with peer-graded assignments |  | How to solve problems with peer-graded assignments |
| 16 | a | Cancel a subscription |  | Cancel a subscription |
| 17 | a | Refund policies |  | Refund policies |
| 18 | a | Troubleshooting login and account issues |  | Troubleshooting login and account issues |
| 19 | a | here |  | here |
| 20 | a | Learn more |  | Learn more |

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
- Focus indicator concerns: 3

### Low-Vision Limitations

- Low-vision checks use browser-computed styles and conservative heuristics.
- Rendered color contrast checks do not prove full WCAG conformance.
- Zoom/reflow uses a narrow viewport approximation rather than a full zoom compliance test.
- Focus indicator detection may miss custom focus styles.

## Visual Proof

- Screenshot path: reports/email_verified_outreach/visual/coursera_contact/page.png
- Focus path overlay path: reports/email_verified_outreach/visual/coursera_contact/focus_path.html
- Focus points count: 60

- Focus overlay shows observed Tab stops in this browser run.
- It does not represent every assistive technology experience.

### What the AI Found

- Status: ok
- Mode: suggest_only
- Model: llama-3.3-70b-versatile

Possible accessibility barriers found on the Coursera contact page

1. AI-suggested observation: Some links may have generic text that does not explain their destination or action
   Related evidence, if any: Multiple instances of generic link text found, such as 'here' and 'Learn more'
   Human review needed: true
   Confidence: AI-only

2. AI-suggested observation: Some headings may have skipped levels, which could disrupt the page's structure
   Related evidence, if any: One instance of a skipped heading level found, from h1 to h3
   Human review needed: true
   Confidence: AI-only

3. AI-suggested observation: Some text may have low contrast with its background, which could make it difficult to read
   Related evidence, if any: Multiple instances of low contrast text found, with a contrast ratio below the conservative 4.5:1 review threshold
   Human review needed: true
   Confidence: AI-only

4. AI-suggested observation: Some content may not reflow properly when the page is zoomed in, which could make it difficult to read
   Related evidence, if any: Multiple instances of fixed or wide content found, which may prevent reflow
   Human review needed: true
   Confidence: AI-only

5. AI-suggested observation: Some focused elements may not have a visible focus indicator, which could make it difficult for users to navigate the page
   Related evidence, if any: Multiple instances of missing focus indicators found, including on input fields and links
   Human review needed: true
   Confidence: AI-only

#### Outreach Notes

- We suggest reviewing the Coursera contact page for potential accessibility barriers and making necessary improvements to ensure equal access for all users.

#### AI Scout Limitations

- AI Scout findings are suggestions and need human review.
- AI Scout output is not a confirmed accessibility finding.
- AI Scout does not determine legal compliance, WCAG compliance, or screen-reader behavior.
- AI Scout output is not a needs human review accessibility finding.


## Issues Found

### 1. Link text is too generic

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
- href: https://www.coursera.org/campus#form
- text: here
- line: 1638
- reason: Link text is generic and does not explain the destination or action.

```html
<a href="https://www.coursera.org/campus#form">here</a>
```

### 2. Link text is too generic

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
- href: https://www.coursera.org/google-certificates-community-colleges-cte
- text: Learn more
- line: 1638
- reason: Link text is generic and does not explain the destination or action.

```html
<a href="https://www.coursera.org/google-certificates-community-colleges-cte">Learn more</a>
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
- href: https://www.coursera.org/business/learn-more
- text: here
- line: 1638
- reason: Link text is generic and does not explain the destination or action.

```html
<a href="https://www.coursera.org/business/learn-more">here</a>
```

### 4. Link text is too generic

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
- href: https://www.coursera.org/government
- text: here
- line: 1638
- reason: Link text is generic and does not explain the destination or action.

```html
<a href="https://www.coursera.org/government">here</a>
```

### 5. Heading level is skipped

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
- text: Learner Support
- line: 1638
- reason: Heading level jumps from h1 to h3.

```html
<h3>
```

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
- text: For Individuals
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
- text: For Businesses
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
- text: For Universities
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
- text: For Governments
- detected_in: low_vision
- reason: Computed foreground/background contrast is below the conservative 4.5:1 review threshold.

### 10. Fixed or wide content may prevent reflow

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
- id: fb-root
- detected_in: low_vision
- reason: A rendered element is wider than the narrow viewport or uses a large fixed pixel width.

### 11. Fixed or wide content may prevent reflow

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
- id: rendered-content
- text: Join for Free Contact Us Have questions? The quickest way to get in touch with u
- detected_in: low_vision
- reason: A rendered element is wider than the narrow viewport or uses a large fixed pixel width.

### 12. Fixed or wide content may prevent reflow

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
- text: Join for Free Contact Us Have questions? The quickest way to get in touch with u
- detected_in: low_vision
- reason: A rendered element is wider than the narrow viewport or uses a large fixed pixel width.

### 13. Focused element may not show a visible focus indicator

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
- id: search-autocomplete-input
- name: query
- text: Search catalog
- step: 8
- detected_in: low_vision
- reason: The focused element did not expose an obvious outline, box-shadow, or border focus style in computed CSS.

### 14. Focused element may not show a visible focus indicator

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
- text: University Partnership Inquiries
- step: 26
- detected_in: low_vision
- reason: The focused element did not expose an obvious outline, box-shadow, or border focus style in computed CSS.

### 15. Focused element may not show a visible focus indicator

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
- text: Industry Partnership Inquiries
- step: 27
- detected_in: low_vision
- reason: The focused element did not expose an obvious outline, box-shadow, or border focus style in computed CSS.

## Limitations

- This prototype runs static HTML checks plus a basic keyboard interaction audit.
- It does not replace a full human accessibility audit.
- Browser mode does not simulate a full screen reader, and accessible names are estimated.
- Low-vision browser checks are conservative heuristics and require manual review.

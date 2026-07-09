# A11yway Accessibility Report

## Summary

- Source: https://www.accessibilityassociation.org/
- Source type: url
- Issues found: 19
- Agents used: Keyboard-only student
- Checks run: html_form_labels, interactive_names, image_alt_text, heading_structure, page_metadata, media_accessibility, keyboard_focus_traversal, browser_dom_snapshot, rendered_color_contrast, zoom_reflow_200, focus_visibility

### Counts By Severity

- medium: 16
- high: 3

### Counts By Issue Type

- missing_h1: 1
- browser_repeated_focus: 1
- generic_link_text: 1
- missing_image_alt: 7
- low_contrast_text: 2
- zoom_fixed_width_content: 3
- focus_indicator_missing: 4

### Source Metadata

- Final URL: https://www.accessibilityassociation.org/
- Status code: 200
- Content type: text/html; charset=utf-8

## Browser Mode Summary

- Analysis modes: static, browser, low_vision
- Browser audit success: true
- Checks run: keyboard_focus_traversal, browser_dom_snapshot
- Focus trace length: 50

## Browser Interaction Trace

| Step | Tag | Accessible name guess | ID/Name | Text/Href |
| ---: | --- | --- | --- | --- |
| 1 | c-skip-to-main-content | Skip to Main Content |  | Skip to Main Content |
| 2 | a | Subscribe to the IAAP Newsletter opens in a new tab |  | Subscribe to the IAAP Newsletter |
| 3 | input | Search | zhi9qdj |  |
| 4 | button | Search |  | Search |
| 5 | c-user-profile | JOIN LOGIN |  | JOIN LOGIN |
| 6 | c-user-profile | JOIN LOGIN |  | JOIN LOGIN |
| 7 | linkifyanything-linkify-anything |  |  |  |
| 8 | ccnavmenus-nav-menu2 | About Expand About Membership Expand Membership Certification Expand Certificati |  | About Expand About Membership Expand Membership Certification Expand Certificati |
| 9 | ccnavmenus-nav-menu2 | About Expand About Membership Expand Membership Certification Expand Certificati |  | About Expand About Membership Expand Membership Certification Expand Certificati |
| 10 | ccnavmenus-nav-menu2 | About Expand About Membership Expand Membership Certification Expand Certificati |  | About Expand About Membership Expand Membership Certification Expand Certificati |
| 11 | ccnavmenus-nav-menu2 | About Expand About Membership Expand Membership Certification Expand Certificati |  | About Expand About Membership Expand Membership Certification Expand Certificati |
| 12 | ccnavmenus-nav-menu2 | About Expand About Membership Expand Membership Certification Expand Certificati |  | About Expand About Membership Expand Membership Certification Expand Certificati |
| 13 | a | Join IAAP (Opens a new window or page) |  | Join IAAP |
| 14 | a | Visit Membership Overview Page |  | Visit Membership Overview Page |
| 15 | a | Visit Certification Overview Page |  | Visit Certification Overview Page |
| 16 | a | Visit Education Overview Page |  | Visit Education Overview Page |
| 17 | a | IAAP Resources |  | IAAP Resources |
| 18 | a | IAAP Resources |  | IAAP Resources |
| 19 | a | Certification Office Hours |  | Certification Office Hours |
| 20 | a | Sign up |  | Sign up |

Trace truncated: showing the first 20 of 50 steps.

### Browser Limitations

- Browser mode approximates keyboard interaction but does not simulate a full screen reader.
- Accessible names are estimated and require manual review.

## Low-Vision Checks

- Status: passed
- Checks run: rendered_color_contrast, zoom_reflow_200, focus_visibility
- Contrast samples analyzed: 83
- Viewport width for reflow check: 640
- Document scroll width: 640
- Horizontal overflow amount: 0
- Focus stops checked: 40
- Focus indicator concerns: 4

### Low-Vision Limitations

- Low-vision checks use browser-computed styles and conservative heuristics.
- Rendered color contrast checks do not prove full WCAG conformance.
- Zoom/reflow uses a narrow viewport approximation rather than a full zoom compliance test.
- Focus indicator detection may miss custom focus styles.

## Visual Proof

- Screenshot path: reports/outreach_ai_scout/visual/iaap_home/page.png
- Focus path overlay path: reports/outreach_ai_scout/visual/iaap_home/focus_path.html
- Focus points count: 50

- Focus overlay shows observed Tab stops in this browser run.
- It does not represent every assistive technology experience.

### What the AI Found

- Status: ok
- Mode: suggest_only
- Model: llama-3.3-70b-versatile

Possible accessibility barriers found on the IAAP website, including missing alt text, low contrast text, and potential keyboard navigation issues.

1. AI-suggested observation: Some images may not have descriptive alt text, which could make it difficult for users to understand the content.
   Related evidence, if any: Multiple instances of missing alt text were detected in the deterministic findings.
   Human review needed: true
   Confidence: AI-only

2. AI-suggested observation: Some text on the page may have low contrast, which could make it difficult for users to read.
   Related evidence, if any: Low contrast text was detected in the deterministic findings.
   Human review needed: true
   Confidence: AI-only

3. AI-suggested observation: The website may have issues with keyboard navigation, including repeated focus on the same element.
   Related evidence, if any: Keyboard navigation issues were detected in the deterministic findings.
   Human review needed: true
   Confidence: AI-only

#### Outreach Notes

- We suggest reviewing the website's accessibility features to ensure that all users can navigate and understand the content.

#### AI Scout Limitations

- AI Scout findings are suggestions and need human review.
- AI Scout output is not a confirmed accessibility finding.
- AI Scout does not determine legal compliance, WCAG compliance, or screen-reader behavior.
- AI Scout output is not a needs human review accessibility finding.


## Issues Found

### 1. Page is missing an h1

- Issue type: missing_h1
- Rule: Page missing an h1 heading
- Category: Headings & Structure
- Severity: medium
- Why it matters: Students using screen readers often jump to the main heading first; without an h1 they cannot quickly confirm what the page is about.
- Suggested fix: Add one clear h1 that matches the page purpose.
- Manual review: A large styled heading may exist visually without being a real h1 element.
- Static check limitation: Static HTML cannot detect headings rendered by JavaScript.

Evidence:

- tag: html
- line: 2
- reason: Document has no h1 heading.

```html
<html lang="en-US" dir="ltr">
```

### 2. Keyboard focus repeats on the same element

- Issue type: browser_repeated_focus
- Rule: Keyboard focus repeats on the same element
- Category: Keyboard Interaction
- Severity: medium
- Why it matters: Focus that keeps returning to the same element suggests a keyboard trap, which can strand students inside one control.
- Suggested fix: Review tabindex values and focus scripts so Tab moves through every control in a sensible order.
- Manual review: Some widgets (like editors) legitimately hold focus; confirm whether the student can escape with standard keys.
- Browser check limitation: The heuristic only watches repeated Tab stops and cannot prove a real trap.

Evidence:

- tag: c-social-media-links-list
- step: 46
- detected_in: browser_interaction
- reason: The same element stayed focused for 6 Tab presses in a row, which can indicate a keyboard trap.

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
- href: javascript:void(0);
- text: More
- line: 10380
- detected_in: browser_dom
- reason: Link text is generic and does not explain the destination or action.

```html
<a ccnavmenus-treeitem_treeitem="" class="menuLink" href="javascript:void(0);" tabindex="0" role="menuitem" aria-expanded="false" aria-labelledby="announceNavMenu-1783555757560-373" aria-label="Exp...
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
- src: /sfsites/c/cms/delivery/media/MC5U4IVOGEFREIZI62QBFRC3FEKI?version=1.1&channelId=0apIV0000000CKX
- line: 10380
- detected_in: browser_dom
- reason: Image is missing useful alt text.

```html
<img class="lwc-692s6j89ul6" src="/sfsites/c/cms/delivery/media/MC5U4IVOGEFREIZI62QBFRC3FEKI?version=1.1&amp;channelId=0apIV0000000CKX" alt="">
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
- src: /sfsites/c/cms/delivery/media/MCJEPO3KZMCBH5BPLKX7KNCK262Q?version=1.1&channelId=0apIV0000000CKX
- line: 10380
- detected_in: browser_dom
- reason: Image is missing useful alt text.

```html
<img class="lwc-6d0jmdgc6e8" src="/sfsites/c/cms/delivery/media/MCJEPO3KZMCBH5BPLKX7KNCK262Q?version=1.1&amp;channelId=0apIV0000000CKX" loading="eager" draggable="true">
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
- src: /sfsites/c/cms/delivery/media/MCNSDWGSDFJZDRNEX5MTP35NHILI?version=4.1&channelId=0apIV0000000CKX
- line: 10380
- detected_in: browser_dom
- reason: Image is missing useful alt text.

```html
<img class="lwc-6d0jmdgc6e8" src="/sfsites/c/cms/delivery/media/MCNSDWGSDFJZDRNEX5MTP35NHILI?version=4.1&amp;channelId=0apIV0000000CKX" loading="eager" draggable="true">
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
- src: /sfsites/c/cms/delivery/media/MCPFB7II4TFZFADINJCDADCHDOQE?version=2.1&channelId=0apIV0000000CKX
- line: 10380
- detected_in: browser_dom
- reason: Image is missing useful alt text.

```html
<img class="lwc-6d0jmdgc6e8" src="/sfsites/c/cms/delivery/media/MCPFB7II4TFZFADINJCDADCHDOQE?version=2.1&amp;channelId=0apIV0000000CKX" loading="eager" draggable="true">
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
- src: /sfsites/c/cms/delivery/media/MCTKI5ZADU2FCDRMTA6LRL322WAQ?version=2.1&channelId=0apIV0000000CKX
- line: 10380
- detected_in: browser_dom
- reason: Image is missing useful alt text.

```html
<img class="lwc-6d0jmdgc6e8" src="/sfsites/c/cms/delivery/media/MCTKI5ZADU2FCDRMTA6LRL322WAQ?version=2.1&amp;channelId=0apIV0000000CKX" loading="eager" draggable="true">
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
- src: /sfsites/c/cms/delivery/media/MC55Y4UT3M4JAXXFX4TMKYBB5UPI?version=2.1&channelId=0apIV0000000CKX
- line: 10400
- detected_in: browser_dom
- reason: Image is missing useful alt text.

```html
<img class="lwc-6d0jmdgc6e8" src="/sfsites/c/cms/delivery/media/MC55Y4UT3M4JAXXFX4TMKYBB5UPI?version=2.1&amp;channelId=0apIV0000000CKX" loading="eager" draggable="true">
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
- src: /sfsites/c/cms/delivery/media/MCLI6F2M5N45B5XHKV443QBYGDJQ?version=1.1&channelId=0apIV0000000CKX
- line: 10435
- detected_in: browser_dom
- reason: Image is missing useful alt text.

```html
<img src="/sfsites/c/cms/delivery/media/MCLI6F2M5N45B5XHKV443QBYGDJQ?version=1.1&amp;channelId=0apIV0000000CKX" alt="" width="122">
```

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

- tag: a
- text: Subscribe to the IAAP Newsletter
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

- tag: label
- text: Search
- detected_in: low_vision
- reason: Computed foreground/background contrast is below the conservative 4.5:1 review threshold.

### 13. Fixed or wide content may prevent reflow

- Issue type: zoom_fixed_width_content
- Rule: Fixed or wide content may prevent reflow
- Category: Low Vision
- Severity: medium
- Why it matters: Large fixed-width elements can force horizontal scrolling and hide content when users zoom or use narrow windows.
- Suggested fix: Replace fixed-width layout with responsive sizing such as max-width: 100%.
- Manual review: Confirm whether the wide element is essential and whether all content remains reachable without two-dimensional scrolling.
- Browser check limitation: The check flags obvious wide rendered elements and fixed pixel widths; it may miss complex layout problems.

Evidence:

- tag: community_byo-scoped-header-and-footer
- text: Skip to Main Content Subscribe to the IAAP Newsletter Search Search JOIN LOGIN W
- detected_in: low_vision
- reason: A rendered element is wider than the narrow viewport or uses a large fixed pixel width.

### 14. Fixed or wide content may prevent reflow

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
- text: Skip to Main Content Subscribe to the IAAP Newsletter Search Search JOIN LOGIN
- detected_in: low_vision
- reason: A rendered element is wider than the narrow viewport or uses a large fixed pixel width.

### 15. Fixed or wide content may prevent reflow

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
- text: Skip to Main Content Subscribe to the IAAP Newsletter Search Search JOIN LOGIN
- detected_in: low_vision
- reason: A rendered element is wider than the narrow viewport or uses a large fixed pixel width.

### 16. Focused element may not show a visible focus indicator

- Issue type: focus_indicator_missing
- Rule: Focused element may not show a visible focus indicator
- Category: Low Vision
- Severity: medium
- Why it matters: Keyboard users with low vision need a visible indicator to know which control currently has focus.
- Suggested fix: Provide a clear :focus or :focus-visible style with visible outline, border, or shadow.
- Manual review: Manually tab through the page; some custom focus styles may be visible but not detected by this heuristic.
- Browser check limitation: Focus indicator detection checks computed outline, border, and shadow heuristically and can miss custom visual treatments.

Evidence:

- tag: c-skip-to-main-content
- text: Skip to Main Content
- step: 1
- detected_in: low_vision
- reason: The focused element did not expose an obvious outline, box-shadow, or border focus style in computed CSS.

### 17. Focused element may not show a visible focus indicator

- Issue type: focus_indicator_missing
- Rule: Focused element may not show a visible focus indicator
- Category: Low Vision
- Severity: medium
- Why it matters: Keyboard users with low vision need a visible indicator to know which control currently has focus.
- Suggested fix: Provide a clear :focus or :focus-visible style with visible outline, border, or shadow.
- Manual review: Manually tab through the page; some custom focus styles may be visible but not detected by this heuristic.
- Browser check limitation: Focus indicator detection checks computed outline, border, and shadow heuristically and can miss custom visual treatments.

Evidence:

- tag: c-user-profile
- text: JOIN LOGIN
- step: 5
- detected_in: low_vision
- reason: The focused element did not expose an obvious outline, box-shadow, or border focus style in computed CSS.

### 18. Focused element may not show a visible focus indicator

- Issue type: focus_indicator_missing
- Rule: Focused element may not show a visible focus indicator
- Category: Low Vision
- Severity: medium
- Why it matters: Keyboard users with low vision need a visible indicator to know which control currently has focus.
- Suggested fix: Provide a clear :focus or :focus-visible style with visible outline, border, or shadow.
- Manual review: Manually tab through the page; some custom focus styles may be visible but not detected by this heuristic.
- Browser check limitation: Focus indicator detection checks computed outline, border, and shadow heuristically and can miss custom visual treatments.

Evidence:

- tag: linkifyanything-linkify-anything
- step: 7
- detected_in: low_vision
- reason: The focused element did not expose an obvious outline, box-shadow, or border focus style in computed CSS.

### 19. Focused element may not show a visible focus indicator

- Issue type: focus_indicator_missing
- Rule: Focused element may not show a visible focus indicator
- Category: Low Vision
- Severity: medium
- Why it matters: Keyboard users with low vision need a visible indicator to know which control currently has focus.
- Suggested fix: Provide a clear :focus or :focus-visible style with visible outline, border, or shadow.
- Manual review: Manually tab through the page; some custom focus styles may be visible but not detected by this heuristic.
- Browser check limitation: Focus indicator detection checks computed outline, border, and shadow heuristically and can miss custom visual treatments.

Evidence:

- tag: ccnavmenus-nav-menu2
- text: About Expand About Membership Expand Membership Certification Expand Certificati
- step: 8
- detected_in: low_vision
- reason: The focused element did not expose an obvious outline, box-shadow, or border focus style in computed CSS.

## Limitations

- This prototype runs static HTML checks plus a basic keyboard interaction audit.
- It does not replace a full human accessibility audit.
- Browser mode does not simulate a full screen reader, and accessible names are estimated.
- Low-vision browser checks are conservative heuristics and require manual review.

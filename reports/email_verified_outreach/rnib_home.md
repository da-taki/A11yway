# A11yway Accessibility Report

## Summary

- Source: https://www.rnib.org.uk/
- Source type: url
- Issues found: 15
- Agents used: Keyboard-only student
- Checks run: html_form_labels, interactive_names, image_alt_text, heading_structure, page_metadata, media_accessibility, keyboard_focus_traversal, browser_dom_snapshot, rendered_color_contrast, zoom_reflow_200, focus_visibility

### Counts By Severity

- medium: 15

### Counts By Issue Type

- generic_link_text: 2
- missing_image_alt: 10
- zoom_fixed_width_content: 3

### Source Metadata

- Final URL: https://www.rnib.org.uk/
- Status code: 200
- Content type: text/html; charset=utf-8

## Browser Mode Summary

- Analysis modes: static, browser, low_vision
- Browser audit success: true
- Checks run: keyboard_focus_traversal, browser_dom_snapshot
- Focus trace length: 3

## Browser Interaction Trace

| Step | Tag | Accessible name guess | ID/Name | Text/Href |
| ---: | --- | --- | --- | --- |
| 1 | button | Accept all cookies | cassie_accept_all_pre_banner | Accept all cookies |
| 2 | button | Reject all cookies | cassie_reject_all_pre_banner | Reject all cookies |
| 3 | button | Manage Cookies |  | Manage Cookies |

### Browser Limitations

- Browser mode approximates keyboard interaction but does not simulate a full screen reader.
- Accessible names are estimated and require manual review.

## Low-Vision Checks

- Status: passed
- Checks run: rendered_color_contrast, zoom_reflow_200, focus_visibility
- Contrast samples analyzed: 9
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

- Screenshot path: reports/email_verified_outreach/visual/rnib_home/page.png
- Focus path overlay path: reports/email_verified_outreach/visual/rnib_home/focus_path.html
- Focus points count: 3

- Focus overlay shows observed Tab stops in this browser run.
- It does not represent every assistive technology experience.

### What the AI Found

- Status: ok
- Mode: suggest_only
- Model: llama-3.3-70b-versatile

Possible accessibility barriers found on the RNIB website, including generic link text and missing image alt text

1. AI-suggested observation: Some links may have generic text that does not explain their destination or action
   Related evidence, if any: Generic link text found in HTML code
   Human review needed: true
   Confidence: AI-only

2. AI-suggested observation: Some images may be missing alt text, which could make it difficult for users to understand their content
   Related evidence, if any: Missing alt text found in HTML code
   Human review needed: true
   Confidence: AI-only

3. AI-suggested observation: Some content may not reflow properly when the viewport is narrowed, potentially causing issues for users with low vision
   Related evidence, if any: Fixed or wide content found in low-vision findings
   Human review needed: true
   Confidence: AI-only

#### Outreach Notes

- The RNIB website may have some accessibility barriers that could be improved to make it more usable for users with disabilities. We suggest reviewing the website's link text, image alt text, and content reflow to ensure that they are accessible to all users.

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
- href: https://www.rnib.org.uk/your-eyes/the-eye-care-support-pathway/
- text: Learn more
- line: 20804
- reason: Link text is generic and does not explain the destination or action.

```html
<a class="rnib-button rnib-button--primary " href="https://www.rnib.org.uk/your-eyes/the-eye-care-support-pathway/">Learn more</a>
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
- src: https://media.rnib.org.uk/images/Fundraising_Alba_ECLO_702x400.2e16d0ba.fill-1000x600.jpg
- line: 22137
- reason: Image is missing useful alt text.

```html
<img alt="" class="banner-cta__image" height="400" loading="lazy" src="https://media.rnib.org.uk/images/Fundraising_Alba_ECLO_702x400.2e16d0ba.fill-1000x600.jpg" width="668">
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
- src: https://media.rnib.org.uk/images/RNIB_Connect_RNIB_-_Getting_Involv.2e16d0ba.fill-400x220.jpg
- line: 22173
- reason: Image is missing useful alt text.

```html
<img alt="" class="large-image-card__img large-image-card__img--desktop" height="220" loading="lazy" src="https://media.rnib.org.uk/images/RNIB_Connect_RNIB_-_Getting_Involv.2e16d0ba.fill-400x220.j...
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
- src: https://media.rnib.org.uk/images/RNIB_Connect_RNIB_-_Getting_Involv.2e16d0ba.fill-260x145.jpg
- line: 22174
- reason: Image is missing useful alt text.

```html
<img alt="" class="large-image-card__img large-image-card__img--tablet" height="145" loading="lazy" src="https://media.rnib.org.uk/images/RNIB_Connect_RNIB_-_Getting_Involv.2e16d0ba.fill-260x145.jp...
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
- src: https://media.rnib.org.uk/images/RNIB_Connect_RNIB_-_Getting_Involv.2e16d0ba.fill-220x220.jpg
- line: 22175
- reason: Image is missing useful alt text.

```html
<img alt="" class="large-image-card__img large-image-card__img--mobile" height="220" loading="lazy" src="https://media.rnib.org.uk/images/RNIB_Connect_RNIB_-_Getting_Involv.2e16d0ba.fill-220x220.jp...
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
- src: https://media.rnib.org.uk/images/RNIB_Connect_RNIBs_Play_Your_Part.2e16d0ba.fill-400x220.png
- line: 22211
- reason: Image is missing useful alt text.

```html
<img alt="" class="large-image-card__img large-image-card__img--desktop" height="220" loading="lazy" src="https://media.rnib.org.uk/images/RNIB_Connect_RNIBs_Play_Your_Part.2e16d0ba.fill-400x220.pn...
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
- src: https://media.rnib.org.uk/images/RNIB_Connect_RNIBs_Play_Your_Part.2e16d0ba.fill-260x145.png
- line: 22212
- reason: Image is missing useful alt text.

```html
<img alt="" class="large-image-card__img large-image-card__img--tablet" height="145" loading="lazy" src="https://media.rnib.org.uk/images/RNIB_Connect_RNIBs_Play_Your_Part.2e16d0ba.fill-260x145.png...
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
- src: https://media.rnib.org.uk/images/RNIB_Connect_RNIBs_Play_Your_Part.2e16d0ba.fill-220x220.png
- line: 22213
- reason: Image is missing useful alt text.

```html
<img alt="" class="large-image-card__img large-image-card__img--mobile" height="220" loading="lazy" src="https://media.rnib.org.uk/images/RNIB_Connect_RNIBs_Play_Your_Part.2e16d0ba.fill-220x220.png...
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
- src: https://media.rnib.org.uk/images/Untitled_design_48.2e16d0ba.fill-400x220.jpg
- line: 22249
- reason: Image is missing useful alt text.

```html
<img alt="" class="large-image-card__img large-image-card__img--desktop" height="220" loading="lazy" src="https://media.rnib.org.uk/images/Untitled_design_48.2e16d0ba.fill-400x220.jpg" width="400">
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
- src: https://media.rnib.org.uk/images/Untitled_design_48.2e16d0ba.fill-260x145.jpg
- line: 22250
- reason: Image is missing useful alt text.

```html
<img alt="" class="large-image-card__img large-image-card__img--tablet" height="145" loading="lazy" src="https://media.rnib.org.uk/images/Untitled_design_48.2e16d0ba.fill-260x145.jpg" width="260">
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
- src: https://media.rnib.org.uk/images/Untitled_design_48.2e16d0ba.fill-220x220.jpg
- line: 22251
- reason: Image is missing useful alt text.

```html
<img alt="" class="large-image-card__img large-image-card__img--mobile" height="220" loading="lazy" src="https://media.rnib.org.uk/images/Untitled_design_48.2e16d0ba.fill-220x220.jpg" width="220">
```

### 12. Link text is too generic

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
- href: https://www.rnib.org.uk/your-eyes/the-eye-care-support-pathway/
- text: Learn more
- line: 19032
- detected_in: browser_dom
- reason: Link text is generic and does not explain the destination or action.

```html
<a class="rnib-button rnib-button--primary " href="https://www.rnib.org.uk/your-eyes/the-eye-care-support-pathway/" data-mida-tracked="true">Learn more</a>
```

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

- tag: div
- id: cassie-widget
- text: We use cookies on our website to give you the most relevant experience by rememb
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

- tag: div
- text: We use cookies on our website to give you the most relevant experience by rememb
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

- tag: p
- id: cassie_pre_banner_text
- text: We use cookies on our website to give you the most relevant experience by rememb
- detected_in: low_vision
- reason: A rendered element is wider than the narrow viewport or uses a large fixed pixel width.

## Limitations

- This prototype runs static HTML checks plus a basic keyboard interaction audit.
- It does not replace a full human accessibility audit.
- Browser mode does not simulate a full screen reader, and accessible names are estimated.
- Low-vision browser checks are conservative heuristics and require manual review.

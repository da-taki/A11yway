# A11yway Accessibility Report

## Summary

- Source: https://www.levelaccess.com/contact/
- Source type: url
- Issues found: 84
- Agents used: Keyboard-only student
- Checks run: html_form_labels, interactive_names, image_alt_text, heading_structure, page_metadata, media_accessibility, keyboard_focus_traversal, browser_dom_snapshot, rendered_color_contrast, zoom_reflow_200, focus_visibility

### Counts By Severity

- high: 64
- medium: 20

### Counts By Issue Type

- missing_image_alt: 64
- low_contrast_text: 16
- zoom_fixed_width_content: 3
- focus_indicator_missing: 1

### Source Metadata

- Final URL: https://www.levelaccess.com/contact/
- Status code: 200
- Content type: text/html; charset=UTF-8

## Browser Mode Summary

- Analysis modes: static, browser, low_vision
- Browser audit success: true
- Checks run: keyboard_focus_traversal, browser_dom_snapshot
- Focus trace length: 11

## Browser Interaction Trace

| Step | Tag | Accessible name guess | ID/Name | Text/Href |
| ---: | --- | --- | --- | --- |
| 1 | a | Skip To main content |  | Skip To main content |
| 2 | a | Level Access logo |  | https://www.levelaccess.com |
| 3 | button | Products |  | Products |
| 4 | button | Solutions |  | Solutions |
| 5 | button | Resources |  | Resources |
| 6 | button | Company |  | Company |
| 7 | button | Request a demo |  | Request a demo |
| 8 | button | Search |  | Open Search bar |
| 9 | a | Account, Login to Level Access Accessibility Platform |  | Account login |
| 10 | a | 1-800-889-9659 |  | 1-800-889-9659 |
| 11 | a | Send a Sales inquiry |  | Send a Sales inquiry |

### Browser Limitations

- Browser mode approximates keyboard interaction but does not simulate a full screen reader.
- Accessible names are estimated and require manual review.

## Low-Vision Checks

- Status: passed
- Checks run: rendered_color_contrast, zoom_reflow_200, focus_visibility
- Contrast samples analyzed: 22
- Viewport width for reflow check: 640
- Document scroll width: 640
- Horizontal overflow amount: 0
- Focus stops checked: 40
- Focus indicator concerns: 1

### Low-Vision Limitations

- Low-vision checks use browser-computed styles and conservative heuristics.
- Rendered color contrast checks do not prove full WCAG conformance.
- Zoom/reflow uses a narrow viewport approximation rather than a full zoom compliance test.
- Focus indicator detection may miss custom focus styles.

## Visual Proof

- Screenshot path: reports/email_verified_outreach/visual/level_access_contact/page.png
- Focus path overlay path: reports/email_verified_outreach/visual/level_access_contact/focus_path.html
- Focus points count: 11

- Focus overlay shows observed Tab stops in this browser run.
- It does not represent every assistive technology experience.

### What the AI Found

- Status: ok
- Mode: suggest_only
- Model: llama-3.3-70b-versatile

Possible accessibility barriers found on the Level Access contact page

1. AI-suggested observation: Multiple images may be missing alternative text, potentially causing issues for users who rely on screen readers or have visual impairments
   Related evidence, if any: 64 instances of missing image alt text were detected
   Human review needed: true
   Confidence: unclear

2. AI-suggested observation: Some text elements may have low contrast, potentially causing issues for users with visual impairments
   Related evidence, if any: 16 instances of low contrast text were detected
   Human review needed: true
   Confidence: AI-only

3. AI-suggested observation: The page may not be fully accessible when zoomed in or when using a keyboard for navigation
   Related evidence, if any: 3 instances of zoom fixed width content were detected, and 1 instance of missing focus indicator was detected
   Human review needed: true
   Confidence: AI-only

#### Outreach Notes

- We would appreciate the opportunity to discuss our findings and provide recommendations for improving the accessibility of the Level Access contact page

#### AI Scout Limitations

- AI Scout findings are suggestions and need human review.
- AI Scout output is not a confirmed accessibility finding.
- AI Scout does not determine legal compliance, WCAG compliance, or screen-reader behavior.
- AI Scout findings are suggestions and need human review
- AI Scout output is not a needs human review accessibility finding
- AI Scout does not determine legal compliance, WCAG compliance, or screen-reader behavior


## Issues Found

### 1. Image is missing useful alt text

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
- id: NDYwOjI5-1
- src: data:image/svg+xml;base64,PHN2ZyB2aWV3Qm94PSIwIDAgMzIgMzIiIHdpZHRoPSIzMiIgaGVpZ2h0PSIzMiIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48L3N2Zz4=
- line: 106
- reason: Image is missing useful alt text.

```html
<img alt="" nitro-lazy-src="https://cdn-ileifnf.nitrocdn.com/qnYhyygsAysFuGkRrxJtNxivHvhkDvyh/assets/images/optimized/rev-68d816b/www.levelaccess.com/wp-content/uploads/2025/05/Icon-Platform-32px-p...
```

### 2. Image is missing useful alt text

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
- id: NDc5OjI5-1
- src: data:image/svg+xml;base64,PHN2ZyB2aWV3Qm94PSIwIDAgMzIgMzIiIHdpZHRoPSIzMiIgaGVpZ2h0PSIzMiIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48L3N2Zz4=
- line: 106
- reason: Image is missing useful alt text.

```html
<img alt="" nitro-lazy-src="https://cdn-ileifnf.nitrocdn.com/qnYhyygsAysFuGkRrxJtNxivHvhkDvyh/assets/images/optimized/rev-68d816b/www.levelaccess.com/wp-content/uploads/2025/05/Icon-Audit-and-test-...
```

### 3. Image is missing useful alt text

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
- id: NDk4OjI5-1
- src: data:image/svg+xml;base64,PHN2ZyB2aWV3Qm94PSIwIDAgMzIgMzIiIHdpZHRoPSIzMiIgaGVpZ2h0PSIzMiIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48L3N2Zz4=
- line: 106
- reason: Image is missing useful alt text.

```html
<img alt="" nitro-lazy-src="https://cdn-ileifnf.nitrocdn.com/qnYhyygsAysFuGkRrxJtNxivHvhkDvyh/assets/images/optimized/rev-68d816b/www.levelaccess.com/wp-content/uploads/2025/05/Icon-Build-Fix-1.svg...
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
- id: NTE3OjI5-1
- src: data:image/svg+xml;base64,PHN2ZyB2aWV3Qm94PSIwIDAgMzIgMzIiIHdpZHRoPSIzMiIgaGVpZ2h0PSIzMiIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48L3N2Zz4=
- line: 106
- reason: Image is missing useful alt text.

```html
<img alt="" nitro-lazy-src="https://cdn-ileifnf.nitrocdn.com/qnYhyygsAysFuGkRrxJtNxivHvhkDvyh/assets/images/optimized/rev-68d816b/www.levelaccess.com/wp-content/uploads/2025/05/Icon-Governance-Repo...
```

### 5. Image is missing useful alt text

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
- id: NTU1OjI5-1
- src: data:image/svg+xml;base64,PHN2ZyB2aWV3Qm94PSIwIDAgMzIgMzIiIHdpZHRoPSIzMiIgaGVpZ2h0PSIzMiIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48L3N2Zz4=
- line: 106
- reason: Image is missing useful alt text.

```html
<img alt="" nitro-lazy-src="https://cdn-ileifnf.nitrocdn.com/qnYhyygsAysFuGkRrxJtNxivHvhkDvyh/assets/images/optimized/rev-68d816b/www.levelaccess.com/wp-content/uploads/2025/05/Access-Academy.svg" ...
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
- id: NTc0OjI5-1
- src: data:image/svg+xml;base64,PHN2ZyB2aWV3Qm94PSIwIDAgMzIgMzIiIHdpZHRoPSIzMiIgaGVpZ2h0PSIzMiIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48L3N2Zz4=
- line: 106
- reason: Image is missing useful alt text.

```html
<img alt="" nitro-lazy-src="https://cdn-ileifnf.nitrocdn.com/qnYhyygsAysFuGkRrxJtNxivHvhkDvyh/assets/images/optimized/rev-68d816b/www.levelaccess.com/wp-content/uploads/2025/05/CD.svg" class="nitro...
```

### 7. Image is missing useful alt text

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
- id: NTkzOjI5-1
- src: data:image/svg+xml;base64,PHN2ZyB2aWV3Qm94PSIwIDAgMzIgMzIiIHdpZHRoPSIzMiIgaGVpZ2h0PSIzMiIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48L3N2Zz4=
- line: 106
- reason: Image is missing useful alt text.

```html
<img alt="" nitro-lazy-src="https://cdn-ileifnf.nitrocdn.com/qnYhyygsAysFuGkRrxJtNxivHvhkDvyh/assets/images/optimized/rev-68d816b/www.levelaccess.com/wp-content/uploads/2025/05/Icon-Mobile-App-Test...
```

### 8. Image is missing useful alt text

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
- id: NjEyOjI5-1
- src: data:image/svg+xml;base64,PHN2ZyB2aWV3Qm94PSIwIDAgNDggNDgiIHdpZHRoPSI0OCIgaGVpZ2h0PSI0OCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48L3N2Zz4=
- line: 106
- reason: Image is missing useful alt text.

```html
<img alt="" nitro-lazy-src="https://cdn-ileifnf.nitrocdn.com/qnYhyygsAysFuGkRrxJtNxivHvhkDvyh/assets/images/optimized/rev-68d816b/www.levelaccess.com/wp-content/uploads/2025/06/Must-Have-WCAG-Check...
```

### 9. Image is missing useful alt text

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
- id: NjUwOjI5-1
- src: data:image/svg+xml;base64,PHN2ZyB2aWV3Qm94PSIwIDAgMzIgMzIiIHdpZHRoPSIzMiIgaGVpZ2h0PSIzMiIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48L3N2Zz4=
- line: 106
- reason: Image is missing useful alt text.

```html
<img alt="" nitro-lazy-src="https://cdn-ileifnf.nitrocdn.com/qnYhyygsAysFuGkRrxJtNxivHvhkDvyh/assets/images/optimized/rev-68d816b/www.levelaccess.com/wp-content/uploads/2025/05/Automated-Remediatio...
```

### 10. Image is missing useful alt text

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
- id: NjcwOjI5-1
- src: data:image/svg+xml;base64,PHN2ZyB2aWV3Qm94PSIwIDAgMzIgMzIiIHdpZHRoPSIzMiIgaGVpZ2h0PSIzMiIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48L3N2Zz4=
- line: 106
- reason: Image is missing useful alt text.

```html
<img alt="" nitro-lazy-src="https://cdn-ileifnf.nitrocdn.com/qnYhyygsAysFuGkRrxJtNxivHvhkDvyh/assets/images/optimized/rev-68d816b/www.levelaccess.com/wp-content/uploads/2025/05/AI-Summarization-Pri...
```

### 11. Image is missing useful alt text

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
- id: NjkwOjI5-1
- src: data:image/svg+xml;base64,PHN2ZyB2aWV3Qm94PSIwIDAgMzIgMzIiIHdpZHRoPSIzMiIgaGVpZ2h0PSIzMiIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48L3N2Zz4=
- line: 106
- reason: Image is missing useful alt text.

```html
<img alt="" nitro-lazy-src="https://cdn-ileifnf.nitrocdn.com/qnYhyygsAysFuGkRrxJtNxivHvhkDvyh/assets/images/optimized/rev-68d816b/www.levelaccess.com/wp-content/uploads/2025/05/VPATs-ACR.svg" class...
```

### 12. Image is missing useful alt text

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
- id: NzEwOjI5-1
- src: data:image/svg+xml;base64,PHN2ZyB2aWV3Qm94PSIwIDAgMzIgMzIiIHdpZHRoPSIzMiIgaGVpZ2h0PSIzMiIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48L3N2Zz4=
- line: 106
- reason: Image is missing useful alt text.

```html
<img alt="" nitro-lazy-src="https://cdn-ileifnf.nitrocdn.com/qnYhyygsAysFuGkRrxJtNxivHvhkDvyh/assets/images/optimized/rev-68d816b/www.levelaccess.com/wp-content/uploads/2025/05/Manual-Testing-Audit...
```

### 13. Image is missing useful alt text

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
- id: Nzc2OjI5-1
- src: data:image/svg+xml;base64,PHN2ZyB2aWV3Qm94PSIwIDAgMzIgMzIiIHdpZHRoPSIzMiIgaGVpZ2h0PSIzMiIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48L3N2Zz4=
- line: 106
- reason: Image is missing useful alt text.

```html
<img alt="" nitro-lazy-src="https://cdn-ileifnf.nitrocdn.com/qnYhyygsAysFuGkRrxJtNxivHvhkDvyh/assets/images/optimized/rev-68d816b/www.levelaccess.com/wp-content/uploads/2025/05/Enterprise-Businesse...
```

### 14. Image is missing useful alt text

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
- id: Nzk1OjI5-1
- src: data:image/svg+xml;base64,PHN2ZyB2aWV3Qm94PSIwIDAgMzIgMzIiIHdpZHRoPSIzMiIgaGVpZ2h0PSIzMiIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48L3N2Zz4=
- line: 106
- reason: Image is missing useful alt text.

```html
<img alt="" nitro-lazy-src="https://cdn-ileifnf.nitrocdn.com/qnYhyygsAysFuGkRrxJtNxivHvhkDvyh/assets/images/optimized/rev-68d816b/www.levelaccess.com/wp-content/uploads/2025/05/EAA.svg" class="nitr...
```

### 15. Image is missing useful alt text

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
- id: ODE0OjI5-1
- src: data:image/svg+xml;base64,PHN2ZyB2aWV3Qm94PSIwIDAgMzIgMzIiIHdpZHRoPSIzMiIgaGVpZ2h0PSIzMiIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48L3N2Zz4=
- line: 106
- reason: Image is missing useful alt text.

```html
<img alt="" nitro-lazy-src="https://cdn-ileifnf.nitrocdn.com/qnYhyygsAysFuGkRrxJtNxivHvhkDvyh/assets/images/optimized/rev-68d816b/www.levelaccess.com/wp-content/uploads/2025/05/Financial-Services-....
```

### 16. Image is missing useful alt text

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
- id: ODMzOjI5-1
- src: data:image/svg+xml;base64,PHN2ZyB2aWV3Qm94PSIwIDAgMzIgMzIiIHdpZHRoPSIzMiIgaGVpZ2h0PSIzMiIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48L3N2Zz4=
- line: 106
- reason: Image is missing useful alt text.

```html
<img alt="" nitro-lazy-src="https://cdn-ileifnf.nitrocdn.com/qnYhyygsAysFuGkRrxJtNxivHvhkDvyh/assets/images/optimized/rev-68d816b/www.levelaccess.com/wp-content/uploads/2025/05/Software-Vendors-.sv...
```

### 17. Image is missing useful alt text

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
- id: ODcxOjI5-1
- src: data:image/svg+xml;base64,PHN2ZyB2aWV3Qm94PSIwIDAgMzIgMzIiIHdpZHRoPSIzMiIgaGVpZ2h0PSIzMiIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48L3N2Zz4=
- line: 106
- reason: Image is missing useful alt text.

```html
<img alt="" nitro-lazy-src="https://cdn-ileifnf.nitrocdn.com/qnYhyygsAysFuGkRrxJtNxivHvhkDvyh/assets/images/optimized/rev-68d816b/www.levelaccess.com/wp-content/uploads/2025/05/Higher-Education-.sv...
```

### 18. Image is missing useful alt text

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
- id: ODkwOjI5-1
- src: data:image/svg+xml;base64,PHN2ZyB2aWV3Qm94PSIwIDAgMzIgMzIiIHdpZHRoPSIzMiIgaGVpZ2h0PSIzMiIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48L3N2Zz4=
- line: 106
- reason: Image is missing useful alt text.

```html
<img alt="" nitro-lazy-src="https://cdn-ileifnf.nitrocdn.com/qnYhyygsAysFuGkRrxJtNxivHvhkDvyh/assets/images/optimized/rev-68d816b/www.levelaccess.com/wp-content/uploads/2025/05/Retail-and-Consumer-...
```

### 19. Image is missing useful alt text

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
- id: OTA5OjI5-1
- src: data:image/svg+xml;base64,PHN2ZyB2aWV3Qm94PSIwIDAgMzIgMzIiIHdpZHRoPSIzMiIgaGVpZ2h0PSIzMiIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48L3N2Zz4=
- line: 106
- reason: Image is missing useful alt text.

```html
<img alt="" nitro-lazy-src="https://cdn-ileifnf.nitrocdn.com/qnYhyygsAysFuGkRrxJtNxivHvhkDvyh/assets/images/optimized/rev-68d816b/www.levelaccess.com/wp-content/uploads/2025/05/Public-Sector-.svg" ...
```

### 20. Image is missing useful alt text

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
- id: OTQ3OjI5-1
- src: data:image/svg+xml;base64,PHN2ZyB2aWV3Qm94PSIwIDAgMzIgMzIiIHdpZHRoPSIzMiIgaGVpZ2h0PSIzMiIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48L3N2Zz4=
- line: 106
- reason: Image is missing useful alt text.

```html
<img alt="" nitro-lazy-src="https://cdn-ileifnf.nitrocdn.com/qnYhyygsAysFuGkRrxJtNxivHvhkDvyh/assets/images/optimized/rev-68d816b/www.levelaccess.com/wp-content/uploads/2025/05/For-Developers-.svg"...
```

### 21. Image is missing useful alt text

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
- id: OTY3OjI5-1
- src: data:image/svg+xml;base64,PHN2ZyB2aWV3Qm94PSIwIDAgMzIgMzIiIHdpZHRoPSIzMiIgaGVpZ2h0PSIzMiIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48L3N2Zz4=
- line: 106
- reason: Image is missing useful alt text.

```html
<img alt="" nitro-lazy-src="https://cdn-ileifnf.nitrocdn.com/qnYhyygsAysFuGkRrxJtNxivHvhkDvyh/assets/images/optimized/rev-68d816b/www.levelaccess.com/wp-content/uploads/2025/05/For-Designers-.svg" ...
```

### 22. Image is missing useful alt text

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
- id: OTg3OjI5-1
- src: data:image/svg+xml;base64,PHN2ZyB2aWV3Qm94PSIwIDAgMzIgMzIiIHdpZHRoPSIzMiIgaGVpZ2h0PSIzMiIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48L3N2Zz4=
- line: 106
- reason: Image is missing useful alt text.

```html
<img alt="" nitro-lazy-src="https://cdn-ileifnf.nitrocdn.com/qnYhyygsAysFuGkRrxJtNxivHvhkDvyh/assets/images/optimized/rev-68d816b/www.levelaccess.com/wp-content/uploads/2025/05/For-Compliance-Teams...
```

### 23. Image is missing useful alt text

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
- id: MTAwNzoyOQ==-1
- src: data:image/svg+xml;base64,PHN2ZyB2aWV3Qm94PSIwIDAgMzIgMzIiIHdpZHRoPSIzMiIgaGVpZ2h0PSIzMiIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48L3N2Zz4=
- line: 106
- reason: Image is missing useful alt text.

```html
<img alt="" nitro-lazy-src="https://cdn-ileifnf.nitrocdn.com/qnYhyygsAysFuGkRrxJtNxivHvhkDvyh/assets/images/optimized/rev-68d816b/www.levelaccess.com/wp-content/uploads/2025/05/For-Accessibility-Te...
```

### 24. Image is missing useful alt text

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
- id: MTA3MzoyOQ==-1
- src: data:image/svg+xml;base64,PHN2ZyB2aWV3Qm94PSIwIDAgMzIgMzIiIHdpZHRoPSIzMiIgaGVpZ2h0PSIzMiIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48L3N2Zz4=
- line: 106
- reason: Image is missing useful alt text.

```html
<img alt="" nitro-lazy-src="https://cdn-ileifnf.nitrocdn.com/qnYhyygsAysFuGkRrxJtNxivHvhkDvyh/assets/images/optimized/rev-68d816b/www.levelaccess.com/wp-content/uploads/2025/05/Resource-Library.svg...
```

### 25. Image is missing useful alt text

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
- id: MTA5MjoyOQ==-1
- src: data:image/svg+xml;base64,PHN2ZyB2aWV3Qm94PSIwIDAgMzIgMzIiIHdpZHRoPSIzMiIgaGVpZ2h0PSIzMiIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48L3N2Zz4=
- line: 106
- reason: Image is missing useful alt text.

```html
<img alt="" nitro-lazy-src="https://cdn-ileifnf.nitrocdn.com/qnYhyygsAysFuGkRrxJtNxivHvhkDvyh/assets/images/optimized/rev-68d816b/www.levelaccess.com/wp-content/uploads/2025/05/Blog-1.svg" class="n...
```

### 26. Image is missing useful alt text

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
- id: MTExMToyOQ==-1
- src: data:image/svg+xml;base64,PHN2ZyB2aWV3Qm94PSIwIDAgMzIgMzIiIHdpZHRoPSIzMiIgaGVpZ2h0PSIzMiIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48L3N2Zz4=
- line: 106
- reason: Image is missing useful alt text.

```html
<img alt="" nitro-lazy-src="https://cdn-ileifnf.nitrocdn.com/qnYhyygsAysFuGkRrxJtNxivHvhkDvyh/assets/images/optimized/rev-68d816b/www.levelaccess.com/wp-content/uploads/2025/05/Icon-Complete-Guide-...
```

### 27. Image is missing useful alt text

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
- id: MTEzMDoyOQ==-1
- src: data:image/svg+xml;base64,PHN2ZyB2aWV3Qm94PSIwIDAgNDAgNDAiIHdpZHRoPSI0MCIgaGVpZ2h0PSI0MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48L3N2Zz4=
- line: 106
- reason: Image is missing useful alt text.

```html
<img alt="" nitro-lazy-src="https://cdn-ileifnf.nitrocdn.com/qnYhyygsAysFuGkRrxJtNxivHvhkDvyh/assets/images/optimized/rev-68d816b/www.levelaccess.com/wp-content/uploads/2025/12/expert_instruction_i...
```

### 28. Image is missing useful alt text

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
- id: MTE0OToyOQ==-1
- src: data:image/svg+xml;base64,PHN2ZyB2aWV3Qm94PSIwIDAgMzIgMzIiIHdpZHRoPSIzMiIgaGVpZ2h0PSIzMiIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48L3N2Zz4=
- line: 106
- reason: Image is missing useful alt text.

```html
<img alt="" nitro-lazy-src="https://cdn-ileifnf.nitrocdn.com/qnYhyygsAysFuGkRrxJtNxivHvhkDvyh/assets/images/optimized/rev-68d816b/www.levelaccess.com/wp-content/uploads/2025/05/Icon-The-Sixth-Annua...
```

### 29. Image is missing useful alt text

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
- id: MTE4NzoyOQ==-1
- src: data:image/svg+xml;base64,PHN2ZyB2aWV3Qm94PSIwIDAgMzIgMzIiIHdpZHRoPSIzMiIgaGVpZ2h0PSIzMiIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48L3N2Zz4=
- line: 106
- reason: Image is missing useful alt text.

```html
<img alt="" nitro-lazy-src="https://cdn-ileifnf.nitrocdn.com/qnYhyygsAysFuGkRrxJtNxivHvhkDvyh/assets/images/optimized/rev-68d816b/www.levelaccess.com/wp-content/uploads/2025/05/Help-Center.svg" cla...
```

### 30. Image is missing useful alt text

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
- id: MTIwNjoyOQ==-1
- src: data:image/svg+xml;base64,PHN2ZyB2aWV3Qm94PSIwIDAgMzIgMzIiIHdpZHRoPSIzMiIgaGVpZ2h0PSIzMiIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48L3N2Zz4=
- line: 106
- reason: Image is missing useful alt text.

```html
<img alt="" nitro-lazy-src="https://cdn-ileifnf.nitrocdn.com/qnYhyygsAysFuGkRrxJtNxivHvhkDvyh/assets/images/optimized/rev-68d816b/www.levelaccess.com/wp-content/uploads/2025/05/Icon-Audit-and-test-...
```

### 31. Image is missing useful alt text

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
- id: MTIyNToyOQ==-1
- src: data:image/svg+xml;base64,PHN2ZyB2aWV3Qm94PSIwIDAgMzIgMzIiIHdpZHRoPSIzMiIgaGVpZ2h0PSIzMiIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48L3N2Zz4=
- line: 106
- reason: Image is missing useful alt text.

```html
<img alt="" nitro-lazy-src="https://cdn-ileifnf.nitrocdn.com/qnYhyygsAysFuGkRrxJtNxivHvhkDvyh/assets/images/optimized/rev-68d816b/www.levelaccess.com/wp-content/uploads/2025/05/FAQ.svg" class="nitr...
```

### 32. Image is missing useful alt text

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
- id: MTI0NDoyOQ==-1
- src: data:image/svg+xml;base64,PHN2ZyB2aWV3Qm94PSIwIDAgMzIgMzIiIHdpZHRoPSIzMiIgaGVpZ2h0PSIzMiIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48L3N2Zz4=
- line: 106
- reason: Image is missing useful alt text.

```html
<img alt="" nitro-lazy-src="https://cdn-ileifnf.nitrocdn.com/qnYhyygsAysFuGkRrxJtNxivHvhkDvyh/assets/images/optimized/rev-68d816b/www.levelaccess.com/wp-content/uploads/2025/05/Trust-Center.svg" cl...
```

### 33. Image is missing useful alt text

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
- id: MTI2MzoyOQ==-1
- src: data:image/svg+xml;base64,PHN2ZyB2aWV3Qm94PSIwIDAgNDggNDkiIHdpZHRoPSI0OCIgaGVpZ2h0PSI0OSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48L3N2Zz4=
- line: 106
- reason: Image is missing useful alt text.

```html
<img alt="" nitro-lazy-src="https://cdn-ileifnf.nitrocdn.com/qnYhyygsAysFuGkRrxJtNxivHvhkDvyh/assets/images/optimized/rev-68d816b/www.levelaccess.com/wp-content/uploads/2025/12/build_together_icon-...
```

### 34. Image is missing useful alt text

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
- id: MTMwMToyOQ==-1
- src: data:image/svg+xml;base64,PHN2ZyB2aWV3Qm94PSIwIDAgMzIgMzIiIHdpZHRoPSIzMiIgaGVpZ2h0PSIzMiIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48L3N2Zz4=
- line: 106
- reason: Image is missing useful alt text.

```html
<img alt="" nitro-lazy-src="https://cdn-ileifnf.nitrocdn.com/qnYhyygsAysFuGkRrxJtNxivHvhkDvyh/assets/images/optimized/rev-68d816b/www.levelaccess.com/wp-content/uploads/2025/05/Webinars.svg" class=...
```

### 35. Image is missing useful alt text

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
- id: MTMyMToyOQ==-1
- src: data:image/svg+xml;base64,PHN2ZyB2aWV3Qm94PSIwIDAgMzIgMzIiIHdpZHRoPSIzMiIgaGVpZ2h0PSIzMiIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48L3N2Zz4=
- line: 106
- reason: Image is missing useful alt text.

```html
<img alt="" nitro-lazy-src="https://cdn-ileifnf.nitrocdn.com/qnYhyygsAysFuGkRrxJtNxivHvhkDvyh/assets/images/optimized/rev-68d816b/www.levelaccess.com/wp-content/uploads/2025/05/Calendar-1.svg" clas...
```

### 36. Image is missing useful alt text

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
- id: MTM0MToyOQ==-1
- src: data:image/svg+xml;base64,PHN2ZyB2aWV3Qm94PSIwIDAgMzIgMzIiIHdpZHRoPSIzMiIgaGVpZ2h0PSIzMiIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48L3N2Zz4=
- line: 106
- reason: Image is missing useful alt text.

```html
<img alt="" nitro-lazy-src="https://cdn-ileifnf.nitrocdn.com/qnYhyygsAysFuGkRrxJtNxivHvhkDvyh/assets/images/optimized/rev-68d816b/www.levelaccess.com/wp-content/uploads/2025/05/EAA.svg" class="nitr...
```

### 37. Image is missing useful alt text

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
- id: MTM2MToyOQ==-1
- src: data:image/svg+xml;base64,PHN2ZyB2aWV3Qm94PSIwIDAgMzIgMzIiIHdpZHRoPSIzMiIgaGVpZ2h0PSIzMiIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48L3N2Zz4=
- line: 106
- reason: Image is missing useful alt text.

```html
<img alt="" nitro-lazy-src="https://cdn-ileifnf.nitrocdn.com/qnYhyygsAysFuGkRrxJtNxivHvhkDvyh/assets/images/optimized/rev-68d816b/www.levelaccess.com/wp-content/uploads/2025/05/Press-Releases-.svg"...
```

### 38. Image is missing useful alt text

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
- id: MTM4MToyOQ==-1
- src: data:image/svg+xml;base64,PHN2ZyB2aWV3Qm94PSIwIDAgNjQgNjQiIHdpZHRoPSI2NCIgaGVpZ2h0PSI2NCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48L3N2Zz4=
- line: 106
- reason: Image is missing useful alt text.

```html
<img alt="" nitro-lazy-src="https://cdn-ileifnf.nitrocdn.com/qnYhyygsAysFuGkRrxJtNxivHvhkDvyh/assets/images/optimized/rev-68d816b/www.levelaccess.com/wp-content/uploads/2025/06/ADA-Compliance-and-D...
```

### 39. Image is missing useful alt text

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
- id: MTQ0NzoyOQ==-1
- src: data:image/svg+xml;base64,PHN2ZyB2aWV3Qm94PSIwIDAgNDggNDgiIHdpZHRoPSI0OCIgaGVpZ2h0PSI0OCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48L3N2Zz4=
- line: 106
- reason: Image is missing useful alt text.

```html
<img alt="" nitro-lazy-src="https://cdn-ileifnf.nitrocdn.com/qnYhyygsAysFuGkRrxJtNxivHvhkDvyh/assets/images/optimized/rev-68d816b/www.levelaccess.com/wp-content/uploads/2025/06/Sustained-momentum-i...
```

### 40. Image is missing useful alt text

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
- id: MTQ2NjoyOQ==-1
- src: data:image/svg+xml;base64,PHN2ZyB2aWV3Qm94PSIwIDAgNDggNDgiIHdpZHRoPSI0OCIgaGVpZ2h0PSI0OCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48L3N2Zz4=
- line: 106
- reason: Image is missing useful alt text.

```html
<img alt="" nitro-lazy-src="https://cdn-ileifnf.nitrocdn.com/qnYhyygsAysFuGkRrxJtNxivHvhkDvyh/assets/images/optimized/rev-68d816b/www.levelaccess.com/wp-content/uploads/2025/06/Blog-icon-48px-Plum-...
```

### 41. Image is missing useful alt text

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
- id: MTUwNDoyOQ==-1
- src: data:image/svg+xml;base64,PHN2ZyB2aWV3Qm94PSIwIDAgNDggNDgiIHdpZHRoPSI0OCIgaGVpZ2h0PSI0OCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48L3N2Zz4=
- line: 106
- reason: Image is missing useful alt text.

```html
<img alt="" nitro-lazy-src="https://cdn-ileifnf.nitrocdn.com/qnYhyygsAysFuGkRrxJtNxivHvhkDvyh/assets/images/optimized/rev-68d816b/www.levelaccess.com/wp-content/uploads/2025/06/User-Testing-48px-Pl...
```

### 42. Image is missing useful alt text

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
- id: MTUyMzoyOQ==-1
- src: data:image/svg+xml;base64,PHN2ZyB2aWV3Qm94PSIwIDAgNDggNDgiIHdpZHRoPSI0OCIgaGVpZ2h0PSI0OCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48L3N2Zz4=
- line: 106
- reason: Image is missing useful alt text.

```html
<img alt="" nitro-lazy-src="https://cdn-ileifnf.nitrocdn.com/qnYhyygsAysFuGkRrxJtNxivHvhkDvyh/assets/images/optimized/rev-68d816b/www.levelaccess.com/wp-content/uploads/2025/06/Software-vendors-ico...
```

### 43. Image is missing useful alt text

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
- id: MTYyMjoxMTM=-1
- src: data:image/svg+xml;base64,PHN2ZyB2aWV3Qm94PSIwIDAgMjggMjkiIHdpZHRoPSIyOCIgaGVpZ2h0PSIyOSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48L3N2Zz4=
- line: 106
- reason: Image is missing useful alt text.

```html
<img alt="" nitro-lazy-src="https://cdn-ileifnf.nitrocdn.com/qnYhyygsAysFuGkRrxJtNxivHvhkDvyh/assets/images/optimized/rev-68d816b/www.levelaccess.com/wp-content/themes/newptheme/assets/img/calendar...
```

### 44. Image is missing useful alt text

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
- id: MTY2MDoxMTM=-1
- src: data:image/svg+xml;base64,PHN2ZyB2aWV3Qm94PSIwIDAgMjggMjkiIHdpZHRoPSIyOCIgaGVpZ2h0PSIyOSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48L3N2Zz4=
- line: 106
- reason: Image is missing useful alt text.

```html
<img alt="" nitro-lazy-src="https://cdn-ileifnf.nitrocdn.com/qnYhyygsAysFuGkRrxJtNxivHvhkDvyh/assets/images/optimized/rev-68d816b/www.levelaccess.com/wp-content/themes/newptheme/assets/img/calendar...
```

### 45. Image is missing useful alt text

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
- id: MTY4MjoxMTM=-1
- src: data:image/svg+xml;base64,PHN2ZyB2aWV3Qm94PSIwIDAgMjggMjkiIHdpZHRoPSIyOCIgaGVpZ2h0PSIyOSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48L3N2Zz4=
- line: 106
- reason: Image is missing useful alt text.

```html
<img alt="" nitro-lazy-src="https://cdn-ileifnf.nitrocdn.com/qnYhyygsAysFuGkRrxJtNxivHvhkDvyh/assets/images/optimized/rev-68d816b/www.levelaccess.com/wp-content/themes/newptheme/assets/img/calendar...
```

### 46. Image is missing useful alt text

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
- id: MTcwNDoxMTM=-1
- src: data:image/svg+xml;base64,PHN2ZyB2aWV3Qm94PSIwIDAgMjggMjkiIHdpZHRoPSIyOCIgaGVpZ2h0PSIyOSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48L3N2Zz4=
- line: 106
- reason: Image is missing useful alt text.

```html
<img alt="" nitro-lazy-src="https://cdn-ileifnf.nitrocdn.com/qnYhyygsAysFuGkRrxJtNxivHvhkDvyh/assets/images/optimized/rev-68d816b/www.levelaccess.com/wp-content/themes/newptheme/assets/img/calendar...
```

### 47. Image is missing useful alt text

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
- id: MTcyNzoxMTM=-1
- src: data:image/svg+xml;base64,PHN2ZyB2aWV3Qm94PSIwIDAgMjggMjkiIHdpZHRoPSIyOCIgaGVpZ2h0PSIyOSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48L3N2Zz4=
- line: 106
- reason: Image is missing useful alt text.

```html
<img alt="" nitro-lazy-src="https://cdn-ileifnf.nitrocdn.com/qnYhyygsAysFuGkRrxJtNxivHvhkDvyh/assets/images/optimized/rev-68d816b/www.levelaccess.com/wp-content/themes/newptheme/assets/img/calendar...
```

### 48. Image is missing useful alt text

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
- id: MTc0OToxMjk=-1
- src: data:image/svg+xml;base64,PHN2ZyB2aWV3Qm94PSIwIDAgMjggMjkiIHdpZHRoPSIyOCIgaGVpZ2h0PSIyOSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48L3N2Zz4=
- line: 106
- reason: Image is missing useful alt text.

```html
<img alt="" nitro-lazy-src="https://cdn-ileifnf.nitrocdn.com/qnYhyygsAysFuGkRrxJtNxivHvhkDvyh/assets/images/optimized/rev-68d816b/www.levelaccess.com/wp-content/themes/newptheme/assets/img/calendar...
```

### 49. Image is missing useful alt text

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
- id: MTc3MjoxMjk=-1
- src: data:image/svg+xml;base64,PHN2ZyB2aWV3Qm94PSIwIDAgMjggMjkiIHdpZHRoPSIyOCIgaGVpZ2h0PSIyOSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48L3N2Zz4=
- line: 106
- reason: Image is missing useful alt text.

```html
<img alt="" nitro-lazy-src="https://cdn-ileifnf.nitrocdn.com/qnYhyygsAysFuGkRrxJtNxivHvhkDvyh/assets/images/optimized/rev-68d816b/www.levelaccess.com/wp-content/themes/newptheme/assets/img/calendar...
```

### 50. Image is missing useful alt text

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
- id: MTc5NToxMjk=-1
- src: data:image/svg+xml;base64,PHN2ZyB2aWV3Qm94PSIwIDAgMjggMjkiIHdpZHRoPSIyOCIgaGVpZ2h0PSIyOSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48L3N2Zz4=
- line: 106
- reason: Image is missing useful alt text.

```html
<img alt="" nitro-lazy-src="https://cdn-ileifnf.nitrocdn.com/qnYhyygsAysFuGkRrxJtNxivHvhkDvyh/assets/images/optimized/rev-68d816b/www.levelaccess.com/wp-content/themes/newptheme/assets/img/calendar...
```

### 51. Image is missing useful alt text

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
- id: MTgxODoxMjk=-1
- src: data:image/svg+xml;base64,PHN2ZyB2aWV3Qm94PSIwIDAgMjggMjkiIHdpZHRoPSIyOCIgaGVpZ2h0PSIyOSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48L3N2Zz4=
- line: 106
- reason: Image is missing useful alt text.

```html
<img alt="" nitro-lazy-src="https://cdn-ileifnf.nitrocdn.com/qnYhyygsAysFuGkRrxJtNxivHvhkDvyh/assets/images/optimized/rev-68d816b/www.levelaccess.com/wp-content/themes/newptheme/assets/img/calendar...
```

### 52. Image is missing useful alt text

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
- id: MTg0MToxMjk=-1
- src: data:image/svg+xml;base64,PHN2ZyB2aWV3Qm94PSIwIDAgMjggMjkiIHdpZHRoPSIyOCIgaGVpZ2h0PSIyOSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48L3N2Zz4=
- line: 106
- reason: Image is missing useful alt text.

```html
<img alt="" nitro-lazy-src="https://cdn-ileifnf.nitrocdn.com/qnYhyygsAysFuGkRrxJtNxivHvhkDvyh/assets/images/optimized/rev-68d816b/www.levelaccess.com/wp-content/themes/newptheme/assets/img/calendar...
```

### 53. Image is missing useful alt text

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
- id: MTg2NDoxMjk=-1
- src: data:image/svg+xml;base64,PHN2ZyB2aWV3Qm94PSIwIDAgMjggMjkiIHdpZHRoPSIyOCIgaGVpZ2h0PSIyOSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48L3N2Zz4=
- line: 106
- reason: Image is missing useful alt text.

```html
<img alt="" nitro-lazy-src="https://cdn-ileifnf.nitrocdn.com/qnYhyygsAysFuGkRrxJtNxivHvhkDvyh/assets/images/optimized/rev-68d816b/www.levelaccess.com/wp-content/themes/newptheme/assets/img/calendar...
```

### 54. Image is missing useful alt text

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
- id: MTg5OToxMjk=-1
- src: data:image/svg+xml;base64,PHN2ZyB2aWV3Qm94PSIwIDAgMjggMjkiIHdpZHRoPSIyOCIgaGVpZ2h0PSIyOSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48L3N2Zz4=
- line: 106
- reason: Image is missing useful alt text.

```html
<img alt="" nitro-lazy-src="https://cdn-ileifnf.nitrocdn.com/qnYhyygsAysFuGkRrxJtNxivHvhkDvyh/assets/images/optimized/rev-68d816b/www.levelaccess.com/wp-content/themes/newptheme/assets/img/calendar...
```

### 55. Image is missing useful alt text

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
- id: MTkzMjoxMjk=-1
- src: data:image/svg+xml;base64,PHN2ZyB2aWV3Qm94PSIwIDAgMjggMjkiIHdpZHRoPSIyOCIgaGVpZ2h0PSIyOSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48L3N2Zz4=
- line: 106
- reason: Image is missing useful alt text.

```html
<img alt="" nitro-lazy-src="https://cdn-ileifnf.nitrocdn.com/qnYhyygsAysFuGkRrxJtNxivHvhkDvyh/assets/images/optimized/rev-68d816b/www.levelaccess.com/wp-content/themes/newptheme/assets/img/calendar...
```

### 56. Image is missing useful alt text

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
- id: MjIxNzoyMTk=-1
- src: data:image/svg+xml;base64,PHN2ZyB2aWV3Qm94PSIwIDAgMjY5IDMxMyIgd2lkdGg9IjI2OSIgaGVpZ2h0PSIzMTMiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PC9zdmc+
- line: 117
- reason: Image is missing useful alt text.

```html
<img width="269" height="313" alt="" nitro-lazy-src="https://cdn-ileifnf.nitrocdn.com/qnYhyygsAysFuGkRrxJtNxivHvhkDvyh/assets/images/optimized/rev-68d816b/www.levelaccess.com/wp-content/uploads/202...
```

### 57. Image is missing useful alt text

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
- id: MjIxOToyMDU=-1
- src: data:image/svg+xml;base64,PHN2ZyB2aWV3Qm94PSIwIDAgOTMgMTA3IiB3aWR0aD0iOTMiIGhlaWdodD0iMTA3IiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPjwvc3ZnPg==
- line: 117
- reason: Image is missing useful alt text.

```html
<img width="1" height="1" alt="" nitro-lazy-src="https://cdn-ileifnf.nitrocdn.com/qnYhyygsAysFuGkRrxJtNxivHvhkDvyh/assets/images/optimized/rev-68d816b/www.levelaccess.com/wp-content/uploads/2025/12...
```

### 58. Image is missing useful alt text

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
- id: MjIyMToyMTI=-1
- src: data:image/svg+xml;base64,PHN2ZyB2aWV3Qm94PSIwIDAgOTMgMTA3IiB3aWR0aD0iOTMiIGhlaWdodD0iMTA3IiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPjwvc3ZnPg==
- line: 117
- reason: Image is missing useful alt text.

```html
<img width="1" height="1" alt="" nitro-lazy-src="https://cdn-ileifnf.nitrocdn.com/qnYhyygsAysFuGkRrxJtNxivHvhkDvyh/assets/images/optimized/rev-68d816b/www.levelaccess.com/wp-content/uploads/2025/12...
```

### 59. Image is missing useful alt text

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
- id: MjIyMzoyMTU=-1
- src: data:image/svg+xml;base64,PHN2ZyB2aWV3Qm94PSIwIDAgOTMgMTA3IiB3aWR0aD0iOTMiIGhlaWdodD0iMTA3IiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPjwvc3ZnPg==
- line: 117
- reason: Image is missing useful alt text.

```html
<img width="1" height="1" alt="" nitro-lazy-src="https://cdn-ileifnf.nitrocdn.com/qnYhyygsAysFuGkRrxJtNxivHvhkDvyh/assets/images/optimized/rev-68d816b/www.levelaccess.com/wp-content/uploads/2025/12...
```

### 60. Image is missing useful alt text

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
- id: NTc0OjI5-1
- src: https://cdn-ileifnf.nitrocdn.com/qnYhyygsAysFuGkRrxJtNxivHvhkDvyh/assets/images/optimized/rev-68d816b/www.levelaccess.com/wp-content/uploads/2025/05/CD.svg
- line: 1
- detected_in: browser_dom
- reason: Image is missing useful alt text.

```html
<img alt="" nitro-lazy-src="https://cdn-ileifnf.nitrocdn.com/qnYhyygsAysFuGkRrxJtNxivHvhkDvyh/assets/images/optimized/rev-68d816b/www.levelaccess.com/wp-content/uploads/2025/05/CD.svg" class="lazyl...
```

### 61. Image is missing useful alt text

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
- id: Nzk1OjI5-1
- src: https://cdn-ileifnf.nitrocdn.com/qnYhyygsAysFuGkRrxJtNxivHvhkDvyh/assets/images/optimized/rev-68d816b/www.levelaccess.com/wp-content/uploads/2025/05/EAA.svg
- line: 1
- detected_in: browser_dom
- reason: Image is missing useful alt text.

```html
<img alt="" nitro-lazy-src="https://cdn-ileifnf.nitrocdn.com/qnYhyygsAysFuGkRrxJtNxivHvhkDvyh/assets/images/optimized/rev-68d816b/www.levelaccess.com/wp-content/uploads/2025/05/EAA.svg" class="lazy...
```

### 62. Image is missing useful alt text

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
- id: MTA5MjoyOQ==-1
- src: https://cdn-ileifnf.nitrocdn.com/qnYhyygsAysFuGkRrxJtNxivHvhkDvyh/assets/images/optimized/rev-68d816b/www.levelaccess.com/wp-content/uploads/2025/05/Blog-1.svg
- line: 1
- detected_in: browser_dom
- reason: Image is missing useful alt text.

```html
<img alt="" nitro-lazy-src="https://cdn-ileifnf.nitrocdn.com/qnYhyygsAysFuGkRrxJtNxivHvhkDvyh/assets/images/optimized/rev-68d816b/www.levelaccess.com/wp-content/uploads/2025/05/Blog-1.svg" class="l...
```

### 63. Image is missing useful alt text

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
- id: MTIyNToyOQ==-1
- src: https://cdn-ileifnf.nitrocdn.com/qnYhyygsAysFuGkRrxJtNxivHvhkDvyh/assets/images/optimized/rev-68d816b/www.levelaccess.com/wp-content/uploads/2025/05/FAQ.svg
- line: 1
- detected_in: browser_dom
- reason: Image is missing useful alt text.

```html
<img alt="" nitro-lazy-src="https://cdn-ileifnf.nitrocdn.com/qnYhyygsAysFuGkRrxJtNxivHvhkDvyh/assets/images/optimized/rev-68d816b/www.levelaccess.com/wp-content/uploads/2025/05/FAQ.svg" class="lazy...
```

### 64. Image is missing useful alt text

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
- id: MTM0MToyOQ==-1
- src: https://cdn-ileifnf.nitrocdn.com/qnYhyygsAysFuGkRrxJtNxivHvhkDvyh/assets/images/optimized/rev-68d816b/www.levelaccess.com/wp-content/uploads/2025/05/EAA.svg
- line: 1
- detected_in: browser_dom
- reason: Image is missing useful alt text.

```html
<img alt="" nitro-lazy-src="https://cdn-ileifnf.nitrocdn.com/qnYhyygsAysFuGkRrxJtNxivHvhkDvyh/assets/images/optimized/rev-68d816b/www.levelaccess.com/wp-content/uploads/2025/05/EAA.svg" class="lazy...
```

### 65. Rendered text may have low contrast

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
- text: Products
- detected_in: low_vision
- reason: Computed foreground/background contrast is below the conservative 4.5:1 review threshold.

### 66. Rendered text may have low contrast

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
- text: Solutions
- detected_in: low_vision
- reason: Computed foreground/background contrast is below the conservative 4.5:1 review threshold.

### 67. Rendered text may have low contrast

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
- text: Resources
- detected_in: low_vision
- reason: Computed foreground/background contrast is below the conservative 4.5:1 review threshold.

### 68. Rendered text may have low contrast

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
- text: Company
- detected_in: low_vision
- reason: Computed foreground/background contrast is below the conservative 4.5:1 review threshold.

### 69. Rendered text may have low contrast

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
- text: Open Search bar
- detected_in: low_vision
- reason: Computed foreground/background contrast is below the conservative 4.5:1 review threshold.

### 70. Rendered text may have low contrast

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
- text: Account login
- detected_in: low_vision
- reason: Computed foreground/background contrast is below the conservative 4.5:1 review threshold.

### 71. Rendered text may have low contrast

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
- text: Contact Us
- detected_in: low_vision
- reason: Computed foreground/background contrast is below the conservative 4.5:1 review threshold.

### 72. Rendered text may have low contrast

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
- text: Level Access is your end-to-end digital accessibility solution—combining an AI-powered platform with the market’s deepes
- detected_in: low_vision
- reason: Computed foreground/background contrast is below the conservative 4.5:1 review threshold.

### 73. Rendered text may have low contrast

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
- text: Connect with our team to learn how we can help you create effective, inclusive digital experiences.
- detected_in: low_vision
- reason: Computed foreground/background contrast is below the conservative 4.5:1 review threshold.

### 74. Rendered text may have low contrast

- Issue type: low_contrast_text
- Rule: Rendered text may have low contrast
- Category: Low Vision
- Severity: high
- Why it matters: Low-vision readers may not be able to read text when the computed foreground and background colors are too similar.
- Suggested fix: Increase foreground/background contrast and confirm the final design with manual review.
- Manual review: Confirm the sampled colors match what users actually see, especially over gradients, images, and layered components.
- Browser check limitation: The check samples browser-computed colors and does not prove full WCAG color contrast compliance.

Evidence:

- tag: h2
- text: Locations
- detected_in: low_vision
- reason: Computed foreground/background contrast is below the conservative 4.5:1 review threshold.

### 75. Rendered text may have low contrast

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
- text: USA: 800 Corporate Drive Suite 301 PMB#645 Stafford, VA 22554
- detected_in: low_vision
- reason: Computed foreground/background contrast is below the conservative 4.5:1 review threshold.

### 76. Rendered text may have low contrast

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
- text: Canada: 658 Danforth Avenue, Suite 200, Toronto, ON M4J 5B9 Canada
- detected_in: low_vision
- reason: Computed foreground/background contrast is below the conservative 4.5:1 review threshold.

### 77. Rendered text may have low contrast

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
- text: United Kingdom: Suite 4B Whitefriars, Lewins Mead, Bristol, UK BS1 2NT
- detected_in: low_vision
- reason: Computed foreground/background contrast is below the conservative 4.5:1 review threshold.

### 78. Rendered text may have low contrast

- Issue type: low_contrast_text
- Rule: Rendered text may have low contrast
- Category: Low Vision
- Severity: high
- Why it matters: Low-vision readers may not be able to read text when the computed foreground and background colors are too similar.
- Suggested fix: Increase foreground/background contrast and confirm the final design with manual review.
- Manual review: Confirm the sampled colors match what users actually see, especially over gradients, images, and layered components.
- Browser check limitation: The check samples browser-computed colors and does not prove full WCAG color contrast compliance.

Evidence:

- tag: h2
- text: Get in touch
- detected_in: low_vision
- reason: Computed foreground/background contrast is below the conservative 4.5:1 review threshold.

### 79. Rendered text may have low contrast

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
- text: 1-800-889-9659
- detected_in: low_vision
- reason: Computed foreground/background contrast is below the conservative 4.5:1 review threshold.

### 80. Rendered text may have low contrast

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
- text: Send a Sales inquiry
- detected_in: low_vision
- reason: Computed foreground/background contrast is below the conservative 4.5:1 review threshold.

### 81. Fixed or wide content may prevent reflow

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
- text: Skip To main content Open Search bar Main Menu Contact Us Level Access is your e
- detected_in: low_vision
- reason: A rendered element is wider than the narrow viewport or uses a large fixed pixel width.

### 82. Fixed or wide content may prevent reflow

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
- text: Skip To main content
- detected_in: low_vision
- reason: A rendered element is wider than the narrow viewport or uses a large fixed pixel width.

### 83. Fixed or wide content may prevent reflow

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
- text: Open Search bar Main Menu
- detected_in: low_vision
- reason: A rendered element is wider than the narrow viewport or uses a large fixed pixel width.

### 84. Focused element may not show a visible focus indicator

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
- text: Skip To main content
- step: 1
- detected_in: low_vision
- reason: The focused element did not expose an obvious outline, box-shadow, or border focus style in computed CSS.

## Limitations

- This prototype runs static HTML checks plus a basic keyboard interaction audit.
- It does not replace a full human accessibility audit.
- Browser mode does not simulate a full screen reader, and accessible names are estimated.
- Low-vision browser checks are conservative heuristics and require manual review.

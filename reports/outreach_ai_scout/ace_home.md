# A11yway Accessibility Report

## Summary

- Source: https://www.acenet.edu/
- Source type: url
- Issues found: 14
- Agents used: Keyboard-only student
- Checks run: html_form_labels, interactive_names, image_alt_text, heading_structure, page_metadata, media_accessibility, keyboard_focus_traversal, browser_dom_snapshot, rendered_color_contrast, zoom_reflow_200, focus_visibility

### Counts By Severity

- high: 6
- medium: 8

### Counts By Issue Type

- missing_link_name: 4
- generic_link_text: 3
- missing_image_alt: 7

### Source Metadata

- Final URL: https://www.acenet.edu/Pages/default.aspx
- Status code: 200
- Content type: text/html; charset=utf-8

## Browser Mode Summary

- Analysis modes: static, browser, low_vision
- Browser audit success: false
- Error: Page.goto: Timeout 30000ms exceeded.
- Checks run: keyboard_focus_traversal, browser_dom_snapshot
- Focus trace length: 0

### Browser Limitations

- Browser mode approximates keyboard interaction but does not simulate a full screen reader.
- Accessible names are estimated and require manual review.

## Low-Vision Checks

- Status: failed
- Checks run: rendered_color_contrast, zoom_reflow_200, focus_visibility
- Contrast samples analyzed: 0
- Viewport width for reflow check: 
- Document scroll width: 
- Horizontal overflow amount: 
- Focus stops checked: 0
- Focus indicator concerns: 0

- Error: Page.goto: Timeout 30000ms exceeded.

### Low-Vision Limitations

- Low-vision checks use browser-computed styles and conservative heuristics.
- Rendered color contrast checks do not prove full WCAG conformance.
- Zoom/reflow uses a narrow viewport approximation rather than a full zoom compliance test.
- Focus indicator detection may miss custom focus styles.

### What the AI Found

- Status: ok
- Mode: suggest_only
- Model: llama-3.3-70b-versatile

Possible accessibility barriers found in navigation and image alt text

1. AI-suggested observation: Some links may not have descriptive text for users who rely on assistive technologies
   Related evidence, if any: Links with missing or generic text were detected
   Human review needed: true
   Confidence: AI-only

2. AI-suggested observation: Some images may be missing alternative text, which could impact users who rely on screen readers or have low vision
   Related evidence, if any: Images with missing alt text were detected
   Human review needed: true
   Confidence: AI-only

#### Outreach Notes

- The American Council on Education website may have accessibility barriers that could impact users with disabilities. A human review of the site is recommended to ensure that all users can access and navigate the content.

#### AI Scout Limitations

- AI Scout findings are suggestions and need human review.
- AI Scout output is not a confirmed accessibility finding.
- AI Scout does not determine legal compliance, WCAG compliance, or screen-reader behavior.
- AI Scout output is not a needs human review accessibility finding.


## Issues Found

### 1. Link is missing an accessible name

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
- id: HiddenAnchor
- href: javascript:;
- line: 265
- reason: Link has no usable text, aria-label, title, or image alt text.

```html
<a id="HiddenAnchor" href="javascript:;" style="display:none;">
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
- id: dropdownMenuSearch
- href: #
- line: 299
- reason: Link has no usable text, aria-label, title, or image alt text.

```html
<a href="#" class="dropdown-toggle" id="dropdownMenuSearch" data-toggle="dropdown" aria-haspopup="true" aria-expanded="true">
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
- id: ctl00_megaMenu_ctl00_rptTopLevel_ctl01_hypReadMore
- href: /Policy-Advocacy/Pages/National-Engagement/Economic-Impact-Higher-Ed.aspx
- text: Learn More
- line: 446
- reason: Link text is generic and does not explain the destination or action.

```html
<a id="ctl00_megaMenu_ctl00_rptTopLevel_ctl01_hypReadMore" class="read-more" href="/Policy-Advocacy/Pages/National-Engagement/Economic-Impact-Higher-Ed.aspx">Learn More</a>
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
- href: https://www.acenet.edu/Programs-Services/Pages/Credit-Transcripts/Credit-Transcripts.aspx
- text: Learn more
- line: 2928
- reason: Link text is generic and does not explain the destination or action.

```html
<a class="read-more" href="https://www.acenet.edu/Programs-Services/Pages/Credit-Transcripts/Credit-Transcripts.aspx" aria-label="CREDIT Evaluations">Learn more</a>
```

### 5. Link text is too generic

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
- href: https://www.acenet.edu/Programs-Services/Pages/Credit-Transcripts/Military-Evaluations.aspx
- text: Learn More
- line: 2928
- reason: Link text is generic and does not explain the destination or action.

```html
<a class="read-more" href="https://www.acenet.edu/Programs-Services/Pages/Credit-Transcripts/Military-Evaluations.aspx" aria-label="Military Evaluations">Learn More</a>
```

### 6. Link is missing an accessible name

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
- href: https://twitter.com/ACEducation
- line: 2966
- reason: Link has no usable text, aria-label, title, or image alt text.

```html
<a href="https://twitter.com/ACEducation" class="footer-twitter-logo">
```

### 7. Link is missing an accessible name

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
- href: https://bsky.app/profile/aceducation.bsky.social
- line: 2966
- reason: Link has no usable text, aria-label, title, or image alt text.

```html
<a href="https://bsky.app/profile/aceducation.bsky.social" class="footer-bluesky-logo">
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
- src: /_layouts/15/images/spcommon.png?rev=40
- line: 224
- reason: Image is missing useful alt text.

```html
<img src="/_layouts/15/images/spcommon.png?rev=40" />
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
- src: /_catalogs/masterpage/ACE/img/ACELogo.svg?rev=41
- line: 225
- reason: Image is missing useful alt text.

```html
<img src="/_catalogs/masterpage/ACE/img/ACELogo.svg?rev=41" />
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
- src: /PublishingImages/CreditEval-528x326.jpg
- line: 2928
- reason: Image is missing useful alt text.

```html
<img class="image" src="/PublishingImages/CreditEval-528x326.jpg" title="Picture of two women smiling in an office setting" />
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
- src: /PublishingImages/Military-528x326.jpg
- line: 2928
- reason: Image is missing useful alt text.

```html
<img class="image" src="/PublishingImages/Military-528x326.jpg" title="Picture of a classroom setting focused on a woman in a military uniform" />
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
- src: /PublishingImages/ged-test-528x326.png
- line: 2928
- reason: Image is missing useful alt text.

```html
<img class="image" src="/PublishingImages/ged-test-528x326.png" title="Women looking at a computer monitor" />
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
- src: /_catalogs/masterpage/ACE/img/x-twitter.png
- line: 2966
- reason: Image is missing useful alt text.

```html
<img src="/_catalogs/masterpage/ACE/img/x-twitter.png" style="height:18.75px !important; margin-top: -5px;" />
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
- src: /_catalogs/masterpage/ACE/img/Bluesky_Logo.png
- line: 2966
- reason: Image is missing useful alt text.

```html
<img src="/_catalogs/masterpage/ACE/img/Bluesky_Logo.png" style="height:18.75px !important; margin-top: -5px;" />
```

## Limitations

- This prototype runs static HTML checks plus a basic keyboard interaction audit.
- It does not replace a full human accessibility audit.
- Browser mode does not simulate a full screen reader, and accessible names are estimated.
- Low-vision browser checks are conservative heuristics and require manual review.

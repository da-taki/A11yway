# A11yway Accessibility Report

## Summary

- Source: https://makeitfable.com/contact-fable/
- Source type: url
- Issues found: 35
- Agents used: Keyboard-only student
- Checks run: html_form_labels, interactive_names, image_alt_text, heading_structure, page_metadata, media_accessibility, keyboard_focus_traversal, browser_dom_snapshot, rendered_color_contrast, zoom_reflow_200, focus_visibility

### Counts By Severity

- medium: 8
- high: 27

### Counts By Issue Type

- missing_image_alt: 5
- low_contrast_text: 27
- zoom_fixed_width_content: 3

### Source Metadata

- Final URL: https://makeitfable.com/contact-fable/
- Status code: 200
- Content type: text/html; charset=UTF-8

## Browser Mode Summary

- Analysis modes: static, browser, low_vision
- Browser audit success: true
- Checks run: keyboard_focus_traversal, browser_dom_snapshot
- Focus trace length: 3

## Browser Interaction Trace

| Step | Tag | Accessible name guess | ID/Name | Text/Href |
| ---: | --- | --- | --- | --- |
| 1 | a | Privacy Policy |  | Privacy Policy |
| 2 | button | Accept | hs-eu-confirmation-button | Accept |
| 3 | button | Decline | hs-eu-decline-button | Decline |

### Browser Limitations

- Browser mode approximates keyboard interaction but does not simulate a full screen reader.
- Accessible names are estimated and require manual review.

## Low-Vision Checks

- Status: passed
- Checks run: rendered_color_contrast, zoom_reflow_200, focus_visibility
- Contrast samples analyzed: 99
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

- Screenshot path: reports/email_verified_outreach/visual/fable_contact/page.png
- Focus path overlay path: reports/email_verified_outreach/visual/fable_contact/focus_path.html
- Focus points count: 3

- Focus overlay shows observed Tab stops in this browser run.
- It does not represent every assistive technology experience.

### What the AI Found

- Status: ok
- Mode: suggest_only
- Model: llama-3.3-70b-versatile

Possible accessibility barriers found in the contact page of Fable

1. AI-suggested observation: Some images may not have useful alt text
   Related evidence, if any: Multiple instances of missing image alt text were detected in the page
   Human review needed: true
   Confidence: AI-only

2. AI-suggested observation: Some text may have low contrast with its background
   Related evidence, if any: Multiple instances of low contrast text were detected in the page
   Human review needed: true
   Confidence: AI-only

#### Outreach Notes

- We suggest reviewing the contact page for potential accessibility issues, particularly with regards to image alt text and text contrast

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
- Severity: medium
- Why it matters: Students using screen readers miss the image content entirely, which can hide instructions, diagrams, or required information.
- Suggested fix: Add alt text that describes the image purpose, or mark decorative images as presentation.
- Manual review: Confirm whether the image is informative or decorative; only a human can judge if existing alt text is actually useful.
- Static check limitation: Static checks cannot judge alt text quality, only whether it exists.

Evidence:

- tag: img
- src: https://px.ads.linkedin.com/collect/?pid=4088292&fmt=gif
- line: 1268
- reason: Image is missing useful alt text.

```html
<img loading="eager" decoding="sync" fetchpriority="high" height="1" width="1" style="display:none;" alt="" src="https://px.ads.linkedin.com/collect/?pid=4088292&fmt=gif" />
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
- src: https://makeitfable.com/wp-content/uploads/2025/05/IconUser-Interview-ColourDefault-SizeLarge-1-e1747762350986.png
- line: 1460
- reason: Image is missing useful alt text.

```html
<img loading="eager" decoding="sync" fetchpriority="high" decoding="async" width="441" height="368" title="Icon=User Interview, Colour=Default, Size=Large (1)" src="https://makeitfable.com/wp-conte...
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
- src: https://t.co/1/i/adsct?bci=4&dv=Asia%2FCalcutta%26en-US%26Google%20Inc.%26Win32%26255%261280%26720%2612%2624%261280%26720%260%26na&eci=3&event=%7B%7D&event_id=4729e7e5-f0d3-4502-95c8-7170bbcd3c5b&integration=gtm&p_id=Twitter&p_user_id=0&pl_id=7a50f611-4bd3-4fc7-bf15-db7b8a5e886a&pt=Contact%20us%20%7C%20Fable&tw_document_href=https%3A%2F%2Fmakeitfable.com%2Fcontact-fable%2F&tw_iframe_status=0&tw_pid_src=1&twpid=tw.1783557490544.621947913184148882&txn_id=ocg70&type=javascript&version=2.3.53
- line: 1692
- detected_in: browser_dom
- reason: Image is missing useful alt text.

```html
<img src="https://t.co/1/i/adsct?bci=4&amp;dv=Asia%2FCalcutta%26en-US%26Google%20Inc.%26Win32%26255%261280%26720%2612%2624%261280%26720%260%26na&amp;eci=3&amp;event=%7B%7D&amp;event_id=4729e7e5-f0d...
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
- src: https://analytics.twitter.com/1/i/adsct?bci=4&dv=Asia%2FCalcutta%26en-US%26Google%20Inc.%26Win32%26255%261280%26720%2612%2624%261280%26720%260%26na&eci=3&event=%7B%7D&event_id=4729e7e5-f0d3-4502-95c8-7170bbcd3c5b&integration=gtm&p_id=Twitter&p_user_id=0&pl_id=7a50f611-4bd3-4fc7-bf15-db7b8a5e886a&pt=Contact%20us%20%7C%20Fable&tw_document_href=https%3A%2F%2Fmakeitfable.com%2Fcontact-fable%2F&tw_iframe_status=0&tw_pid_src=1&twpid=tw.1783557490544.621947913184148882&txn_id=ocg70&type=javascript&version=2.3.53
- line: 1692
- detected_in: browser_dom
- reason: Image is missing useful alt text.

```html
<img src="https://analytics.twitter.com/1/i/adsct?bci=4&amp;dv=Asia%2FCalcutta%26en-US%26Google%20Inc.%26Win32%26255%261280%26720%2612%2624%261280%26720%260%26na&amp;eci=3&amp;event=%7B%7D&amp;even...
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
- id: batBeacon903616634268
- src: https://bat.bing.com/action/0?ti=97036113&tm=gtm002&Ver=2&mid=a568ed54-c838-4e19-a2e4-d7c4ea3422f6&bo=1&sid=768396707b2e11f19b9b37e66aa9fa93&vid=7683ba207b2e11f1a0652baa6ec48062&vids=1&msclkid=N&uach=pv%3D19.0.0&pi=0&lg=en-US&sw=1280&sh=720&sc=24&nwd=1&tl=Contact%20us%20%7C%20Fable&p=https%3A%2F%2Fmakeitfable.com%2Fcontact-fable%2F&r=&lt=6559&evt=pageLoad&sv=2&cdb=ARoR&rn=736564
- line: 1692
- detected_in: browser_dom
- reason: Image is missing useful alt text.

```html
<img id="batBeacon903616634268" width="0" height="0" alt="" src="https://bat.bing.com/action/0?ti=97036113&amp;tm=gtm002&amp;Ver=2&amp;mid=a568ed54-c838-4e19-a2e4-d7c4ea3422f6&amp;bo=1&amp;sid=7683...
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
- text: Accessibility testing
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
- text: Accessibility training
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
- text: AUS
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
- text: Accessibility leaders
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
- text: UX designers
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
- text: UX researchers
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
- text: Product managers
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
- text: Engineers and QA analysts
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
- text: About our testers
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
- text: Become a tester
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
- text: Fable Pathways
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
- text: Case studies
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
- text: Fable blog
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

- tag: li
- text: Webinars
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

- tag: li
- text: AT glossary
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

- tag: li
- text: About Fable
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

- tag: li
- text: News
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

- tag: li
- text: Careers
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

- tag: li
- text: Partnerships
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

- tag: li
- text: Contact us
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

- tag: p
- text: LinkedIn
- detected_in: low_vision
- reason: Computed foreground/background contrast is below the conservative 4.5:1 review threshold.

### 27. Rendered text may have low contrast

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
- text: YouTube
- detected_in: low_vision
- reason: Computed foreground/background contrast is below the conservative 4.5:1 review threshold.

### 28. Rendered text may have low contrast

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
- text: © Copyright Fable Tech Labs Inc 2026. All rights reserved.
- detected_in: low_vision
- reason: Computed foreground/background contrast is below the conservative 4.5:1 review threshold.

### 29. Rendered text may have low contrast

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
- text: Trust and Security
- detected_in: low_vision
- reason: Computed foreground/background contrast is below the conservative 4.5:1 review threshold.

### 30. Rendered text may have low contrast

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
- text: Accessibility Statement
- detected_in: low_vision
- reason: Computed foreground/background contrast is below the conservative 4.5:1 review threshold.

### 31. Rendered text may have low contrast

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
- text: Terms of Use
- detected_in: low_vision
- reason: Computed foreground/background contrast is below the conservative 4.5:1 review threshold.

### 32. Rendered text may have low contrast

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
- text: Privacy Policy
- detected_in: low_vision
- reason: Computed foreground/background contrast is below the conservative 4.5:1 review threshold.

### 33. Fixed or wide content may prevent reflow

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
- id: hs-banner-parent
- text: Fable uses cookies and other tracking technologies to collect information about 
- detected_in: low_vision
- reason: A rendered element is wider than the narrow viewport or uses a large fixed pixel width.

### 34. Fixed or wide content may prevent reflow

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
- id: hs-eu-cookie-confirmation
- text: Fable uses cookies and other tracking technologies to collect information about 
- detected_in: low_vision
- reason: A rendered element is wider than the narrow viewport or uses a large fixed pixel width.

### 35. Fixed or wide content may prevent reflow

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
- id: hs-eu-cookie-confirmation-inner
- text: Fable uses cookies and other tracking technologies to collect information about 
- detected_in: low_vision
- reason: A rendered element is wider than the narrow viewport or uses a large fixed pixel width.

## Limitations

- This prototype runs static HTML checks plus a basic keyboard interaction audit.
- It does not replace a full human accessibility audit.
- Browser mode does not simulate a full screen reader, and accessible names are estimated.
- Low-vision browser checks are conservative heuristics and require manual review.

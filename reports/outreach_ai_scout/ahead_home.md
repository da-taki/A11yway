# A11yway Accessibility Report

## Summary

- Source: https://www.ahead.org/
- Source type: url
- Issues found: 54
- Agents used: Keyboard-only student
- Checks run: html_form_labels, interactive_names, image_alt_text, heading_structure, page_metadata, media_accessibility, keyboard_focus_traversal, browser_dom_snapshot, rendered_color_contrast, zoom_reflow_200, focus_visibility

### Counts By Severity

- high: 40
- low: 1
- medium: 13

### Counts By Issue Type

- missing_link_name: 17
- missing_image_alt: 1
- multiple_h1: 1
- skipped_heading_level: 4
- browser_focused_control_missing_name: 9
- browser_focus_on_hidden_element: 7
- low_contrast_text: 6
- zoom_fixed_width_content: 3
- focus_indicator_missing: 6

### Source Metadata

- Final URL: https://www.ahead.org/home
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
| 1 | a | Skip to main content (Press Enter). | skiplink | Skip to main content (Press Enter). |
| 2 | a | SIGN IN | Welcome_LoginLink | SIGN IN |
| 3 | button | Search Button |  | Search Button |
| 4 | a | Skip auxiliary navigation (Press Enter). | auxskiplink | Skip auxiliary navigation (Press Enter). |
| 5 | ul | ABOUT US CONTACT US |  | ABOUT US CONTACT US |
| 6 | a | AHEAD Linkedin page |  | https://www.linkedin.com/company/association-on-higher-education-and-disability/ |
| 7 | a | AHEAD Facebook page |  | https://www.facebook.com/AHEAD.org/ |
| 8 | a | AHEAD Youtube channel |  | https://www.youtube.com/channel/UCCpOb89XX_o-pBKS5sgna8A |
| 9 | a | AHEAD Instagram page |  | https://www.instagram.com/aheadorg_1977/ |
| 10 | a | AHEAD - Association on Higher Education And Disability logo. This will take you to the homepage |  | https://www.ahead.org/home |
| 11 | a | Skip main navigation (Press Enter). | navskiplink | Skip main navigation (Press Enter). |
| 12 | a | Home | megaanchor1 | Home |
| 13 | a | About | megaanchor2 | About |
| 14 | a | Membership | megaanchor3 | Membership |
| 15 | a | Programming | megaanchor4 | Programming |
| 16 | a | Professional Resources | megaanchor5 | Professional Resources |
| 17 | a | Research | megaanchor6 | Research |
| 18 | a | Communities | megaanchor7 | Communities |
| 19 | a | 2026 AHEAD Virtual Conference Info and Registration Now Available! |  | 2026 AHEAD Virtual Conference Info and Registration Now Available! |
| 20 | a | graphic of interconnected points in space |  | https://www.ahead.org/events-programming/conferences/2026-virtual |

Trace truncated: showing the first 20 of 60 steps.

### Browser Limitations

- Browser mode approximates keyboard interaction but does not simulate a full screen reader.
- Accessible names are estimated and require manual review.

## Low-Vision Checks

- Status: passed
- Checks run: rendered_color_contrast, zoom_reflow_200, focus_visibility
- Contrast samples analyzed: 63
- Viewport width for reflow check: 640
- Document scroll width: 640
- Horizontal overflow amount: 0
- Focus stops checked: 40
- Focus indicator concerns: 6

### Low-Vision Limitations

- Low-vision checks use browser-computed styles and conservative heuristics.
- Rendered color contrast checks do not prove full WCAG conformance.
- Zoom/reflow uses a narrow viewport approximation rather than a full zoom compliance test.
- Focus indicator detection may miss custom focus styles.

## Visual Proof

- Screenshot path: reports/outreach_ai_scout/visual/ahead_home/page.png
- Focus path overlay path: reports/outreach_ai_scout/visual/ahead_home/focus_path.html
- Focus points count: 60

- Focus overlay shows observed Tab stops in this browser run.
- It does not represent every assistive technology experience.

### What the AI Found

- Status: ok
- Mode: suggest_only
- Model: llama-3.3-70b-versatile

Possible accessibility barriers found on the AHEAD website, including missing link names and image alt text, which may impact users with disabilities.

1. AI-suggested observation: Links may be missing accessible names, potentially causing navigation difficulties for users relying on assistive technologies.
   Related evidence, if any: Multiple instances of missing link names were detected, such as in the snippets <a id="MainCopy_ctl05_BlogList_ProfileLink_0" href="https://www.ahead.org/people/ahead"> and <a href="http://accessinghigherground.org/">.
   Human review needed: true
   Confidence: AI-only

2. AI-suggested observation: An image may be missing useful alt text, which could hinder users who rely on screen readers or have low vision from understanding the content.
   Related evidence, if any: An image with an empty alt attribute was found: <img src="https://higherlogicdownload.s3.amazonaws.com/AHEAD/38b602f4-ec53-451c-9be0-5c0bf5d27c0a/UploadedImages/Partner_Logos/ahg.png" alt="" class="img-responsive">.
   Human review needed: true
   Confidence: AI-only

3. AI-suggested observation: The page structure may have skipped heading levels, potentially causing confusion for users navigating the content using assistive technologies.
   Related evidence, if any: Heading level jumps from h3 to h5 were detected, as indicated by snippets like <h5>.
   Human review needed: true
   Confidence: AI-only

#### Outreach Notes

- We suggest reviewing the website for accessibility barriers, particularly focusing on link names, image alt text, and heading structure, to ensure an inclusive experience for all users.

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
- id: MainCopy_ctl05_BlogList_ProfileLink_0
- href: https://www.ahead.org/people/ahead
- line: 473
- reason: Link has no usable text, aria-label, title, or image alt text.

```html
<a id="MainCopy_ctl05_BlogList_ProfileLink_0" href="https://www.ahead.org/people/ahead">
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
- id: MainCopy_ctl05_BlogList_ProfileLink_1
- href: https://www.ahead.org/people/ahead
- line: 577
- reason: Link has no usable text, aria-label, title, or image alt text.

```html
<a id="MainCopy_ctl05_BlogList_ProfileLink_1" href="https://www.ahead.org/people/ahead">
```

### 3. Link is missing an accessible name

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
- id: MainCopy_ctl05_BlogList_ProfileLink_2
- href: https://www.ahead.org/people/ahead
- line: 679
- reason: Link has no usable text, aria-label, title, or image alt text.

```html
<a id="MainCopy_ctl05_BlogList_ProfileLink_2" href="https://www.ahead.org/people/ahead">
```

### 4. Link is missing an accessible name

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
- id: MainCopy_ctl11_DocumentsList_ProfileLink_0
- href: https://www.ahead.org/membership/network/members/profile?UserKey=80924270-8dc7-4e28-a294-019a83e6f89c
- line: 985
- reason: Link has no usable text, aria-label, title, or image alt text.

```html
<a id="MainCopy_ctl11_DocumentsList_ProfileLink_0" href="https://www.ahead.org/membership/network/members/profile?UserKey=80924270-8dc7-4e28-a294-019a83e6f89c">
```

### 5. Link is missing an accessible name

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
- id: MainCopy_ctl11_DocumentsList_ProfileLink_1
- href: https://www.ahead.org/membership/network/members/profile?UserKey=c03dd8e5-a84a-474d-8649-a2d38d6e54ab
- line: 1105
- reason: Link has no usable text, aria-label, title, or image alt text.

```html
<a id="MainCopy_ctl11_DocumentsList_ProfileLink_1" href="https://www.ahead.org/membership/network/members/profile?UserKey=c03dd8e5-a84a-474d-8649-a2d38d6e54ab">
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
- id: MainCopy_ctl11_DocumentsList_ProfileLink_2
- href: https://www.ahead.org/membership/network/members/profile?UserKey=c03dd8e5-a84a-474d-8649-a2d38d6e54ab
- line: 1225
- reason: Link has no usable text, aria-label, title, or image alt text.

```html
<a id="MainCopy_ctl11_DocumentsList_ProfileLink_2" href="https://www.ahead.org/membership/network/members/profile?UserKey=c03dd8e5-a84a-474d-8649-a2d38d6e54ab">
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
- id: MainCopy_ctl11_DocumentsList_ProfileLink_3
- href: https://www.ahead.org/membership/network/members/profile?UserKey=01cb0141-971b-419b-8de1-5b0796a000f4
- line: 1345
- reason: Link has no usable text, aria-label, title, or image alt text.

```html
<a id="MainCopy_ctl11_DocumentsList_ProfileLink_3" href="https://www.ahead.org/membership/network/members/profile?UserKey=01cb0141-971b-419b-8de1-5b0796a000f4">
```

### 8. Link is missing an accessible name

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
- href: http://accessinghigherground.org/
- line: 1499
- reason: Link has no usable text, aria-label, title, or image alt text.

```html
<a href="http://accessinghigherground.org/">
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
- src: https://higherlogicdownload.s3.amazonaws.com/AHEAD/38b602f4-ec53-451c-9be0-5c0bf5d27c0a/UploadedImages/Partner_Logos/ahg.png
- line: 1499
- reason: Image is missing useful alt text.

```html
<img src="https://higherlogicdownload.s3.amazonaws.com/AHEAD/38b602f4-ec53-451c-9be0-5c0bf5d27c0a/UploadedImages/Partner_Logos/ahg.png" alt="" caption="false" class="img-responsive">
```

### 10. Page has multiple h1 headings

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

### 11. Heading level is skipped

- Issue type: skipped_heading_level
- Rule: Heading level is skipped
- Category: Headings & Structure
- Severity: medium
- Why it matters: Jumping from h1 to h3 breaks the page outline that screen reader users rely on to understand and navigate content.
- Suggested fix: Do not skip heading levels; move from h1 to h2 before h3.
- Manual review: Check whether the heading order still makes sense when read as an outline.
- Static check limitation: The check follows document order only; visual layout may differ.

Evidence:

- tag: h5
- line: 1010
- reason: Heading level jumps from h3 to h5.

```html
<h5>
```

### 12. Heading level is skipped

- Issue type: skipped_heading_level
- Rule: Heading level is skipped
- Category: Headings & Structure
- Severity: medium
- Why it matters: Jumping from h1 to h3 breaks the page outline that screen reader users rely on to understand and navigate content.
- Suggested fix: Do not skip heading levels; move from h1 to h2 before h3.
- Manual review: Check whether the heading order still makes sense when read as an outline.
- Static check limitation: The check follows document order only; visual layout may differ.

Evidence:

- tag: h5
- line: 1130
- reason: Heading level jumps from h3 to h5.

```html
<h5>
```

### 13. Heading level is skipped

- Issue type: skipped_heading_level
- Rule: Heading level is skipped
- Category: Headings & Structure
- Severity: medium
- Why it matters: Jumping from h1 to h3 breaks the page outline that screen reader users rely on to understand and navigate content.
- Suggested fix: Do not skip heading levels; move from h1 to h2 before h3.
- Manual review: Check whether the heading order still makes sense when read as an outline.
- Static check limitation: The check follows document order only; visual layout may differ.

Evidence:

- tag: h5
- line: 1250
- reason: Heading level jumps from h3 to h5.

```html
<h5>
```

### 14. Heading level is skipped

- Issue type: skipped_heading_level
- Rule: Heading level is skipped
- Category: Headings & Structure
- Severity: medium
- Why it matters: Jumping from h1 to h3 breaks the page outline that screen reader users rely on to understand and navigate content.
- Suggested fix: Do not skip heading levels; move from h1 to h2 before h3.
- Manual review: Check whether the heading order still makes sense when read as an outline.
- Static check limitation: The check follows document order only; visual layout may differ.

Evidence:

- tag: h5
- line: 1370
- reason: Heading level jumps from h3 to h5.

```html
<h5>
```

### 15. Focused control has no accessible name

- Issue type: browser_focused_control_missing_name
- Rule: Focused control has no accessible name
- Category: Keyboard Interaction
- Severity: high
- Why it matters: A keyboard user can reach the control, but without a name a screen reader announces nothing useful about what it does.
- Suggested fix: Add a visible label, text content, or aria-label so students know what the control does.
- Manual review: The accessible name is estimated; confirm with browser dev tools or a screen reader what is actually announced.
- Browser check limitation: Accessible names are estimated from labels, text, and common attributes, not from a full accessibility tree computation.

Evidence:

- tag: a
- href: https://www.ahead.org/events-programming/conferences/2026-virtual
- step: 21
- detected_in: browser_interaction
- reason: A keyboard user reached this control, but it has no label, text, aria-label, or other usable name.

### 16. Focused control has no accessible name

- Issue type: browser_focused_control_missing_name
- Rule: Focused control has no accessible name
- Category: Keyboard Interaction
- Severity: high
- Why it matters: A keyboard user can reach the control, but without a name a screen reader announces nothing useful about what it does.
- Suggested fix: Add a visible label, text content, or aria-label so students know what the control does.
- Manual review: The accessible name is estimated; confirm with browser dev tools or a screen reader what is actually announced.
- Browser check limitation: Accessible names are estimated from labels, text, and common attributes, not from a full accessibility tree computation.

Evidence:

- tag: a
- id: MainCopy_ctl05_BlogList_ProfileLink_0
- href: https://www.ahead.org/people/ahead
- step: 22
- detected_in: browser_interaction
- reason: A keyboard user reached this control, but it has no label, text, aria-label, or other usable name.

### 17. Keyboard focus landed on a hidden element

- Issue type: browser_focus_on_hidden_element
- Rule: Keyboard focus landed on a hidden element
- Category: Keyboard Interaction
- Severity: high
- Why it matters: When focus moves to an invisible element, keyboard users lose track of where they are on the page.
- Suggested fix: Remove hidden elements from the Tab order with tabindex="-1" or make them visible when focused.
- Manual review: Check whether the element becomes visible on focus (like a skip link); that pattern is fine.
- Browser check limitation: Visibility is estimated from element size and CSS and may not match what users actually see.

Evidence:

- tag: a
- id: MainCopy_ctl05_BlogList_ProfileLink_0
- href: https://www.ahead.org/people/ahead
- step: 22
- detected_in: browser_interaction
- reason: This element received keyboard focus but does not appear to be visible on the page.

### 18. Focused control has no accessible name

- Issue type: browser_focused_control_missing_name
- Rule: Focused control has no accessible name
- Category: Keyboard Interaction
- Severity: high
- Why it matters: A keyboard user can reach the control, but without a name a screen reader announces nothing useful about what it does.
- Suggested fix: Add a visible label, text content, or aria-label so students know what the control does.
- Manual review: The accessible name is estimated; confirm with browser dev tools or a screen reader what is actually announced.
- Browser check limitation: Accessible names are estimated from labels, text, and common attributes, not from a full accessibility tree computation.

Evidence:

- tag: a
- id: MainCopy_ctl05_BlogList_ProfileLink_1
- href: https://www.ahead.org/people/ahead
- step: 26
- detected_in: browser_interaction
- reason: A keyboard user reached this control, but it has no label, text, aria-label, or other usable name.

### 19. Keyboard focus landed on a hidden element

- Issue type: browser_focus_on_hidden_element
- Rule: Keyboard focus landed on a hidden element
- Category: Keyboard Interaction
- Severity: high
- Why it matters: When focus moves to an invisible element, keyboard users lose track of where they are on the page.
- Suggested fix: Remove hidden elements from the Tab order with tabindex="-1" or make them visible when focused.
- Manual review: Check whether the element becomes visible on focus (like a skip link); that pattern is fine.
- Browser check limitation: Visibility is estimated from element size and CSS and may not match what users actually see.

Evidence:

- tag: a
- id: MainCopy_ctl05_BlogList_ProfileLink_1
- href: https://www.ahead.org/people/ahead
- step: 26
- detected_in: browser_interaction
- reason: This element received keyboard focus but does not appear to be visible on the page.

### 20. Focused control has no accessible name

- Issue type: browser_focused_control_missing_name
- Rule: Focused control has no accessible name
- Category: Keyboard Interaction
- Severity: high
- Why it matters: A keyboard user can reach the control, but without a name a screen reader announces nothing useful about what it does.
- Suggested fix: Add a visible label, text content, or aria-label so students know what the control does.
- Manual review: The accessible name is estimated; confirm with browser dev tools or a screen reader what is actually announced.
- Browser check limitation: Accessible names are estimated from labels, text, and common attributes, not from a full accessibility tree computation.

Evidence:

- tag: a
- id: MainCopy_ctl05_BlogList_ProfileLink_2
- href: https://www.ahead.org/people/ahead
- step: 30
- detected_in: browser_interaction
- reason: A keyboard user reached this control, but it has no label, text, aria-label, or other usable name.

### 21. Keyboard focus landed on a hidden element

- Issue type: browser_focus_on_hidden_element
- Rule: Keyboard focus landed on a hidden element
- Category: Keyboard Interaction
- Severity: high
- Why it matters: When focus moves to an invisible element, keyboard users lose track of where they are on the page.
- Suggested fix: Remove hidden elements from the Tab order with tabindex="-1" or make them visible when focused.
- Manual review: Check whether the element becomes visible on focus (like a skip link); that pattern is fine.
- Browser check limitation: Visibility is estimated from element size and CSS and may not match what users actually see.

Evidence:

- tag: a
- id: MainCopy_ctl05_BlogList_ProfileLink_2
- href: https://www.ahead.org/people/ahead
- step: 30
- detected_in: browser_interaction
- reason: This element received keyboard focus but does not appear to be visible on the page.

### 22. Focused control has no accessible name

- Issue type: browser_focused_control_missing_name
- Rule: Focused control has no accessible name
- Category: Keyboard Interaction
- Severity: high
- Why it matters: A keyboard user can reach the control, but without a name a screen reader announces nothing useful about what it does.
- Suggested fix: Add a visible label, text content, or aria-label so students know what the control does.
- Manual review: The accessible name is estimated; confirm with browser dev tools or a screen reader what is actually announced.
- Browser check limitation: Accessible names are estimated from labels, text, and common attributes, not from a full accessibility tree computation.

Evidence:

- tag: a
- id: MainCopy_ctl11_DocumentsList_ProfileLink_0
- href: https://www.ahead.org/membership/network/members/profile?UserKey=80924270-8dc7-4e28-a294-019a83e6f89c
- step: 38
- detected_in: browser_interaction
- reason: A keyboard user reached this control, but it has no label, text, aria-label, or other usable name.

### 23. Keyboard focus landed on a hidden element

- Issue type: browser_focus_on_hidden_element
- Rule: Keyboard focus landed on a hidden element
- Category: Keyboard Interaction
- Severity: high
- Why it matters: When focus moves to an invisible element, keyboard users lose track of where they are on the page.
- Suggested fix: Remove hidden elements from the Tab order with tabindex="-1" or make them visible when focused.
- Manual review: Check whether the element becomes visible on focus (like a skip link); that pattern is fine.
- Browser check limitation: Visibility is estimated from element size and CSS and may not match what users actually see.

Evidence:

- tag: a
- id: MainCopy_ctl11_DocumentsList_ProfileLink_0
- href: https://www.ahead.org/membership/network/members/profile?UserKey=80924270-8dc7-4e28-a294-019a83e6f89c
- step: 38
- detected_in: browser_interaction
- reason: This element received keyboard focus but does not appear to be visible on the page.

### 24. Focused control has no accessible name

- Issue type: browser_focused_control_missing_name
- Rule: Focused control has no accessible name
- Category: Keyboard Interaction
- Severity: high
- Why it matters: A keyboard user can reach the control, but without a name a screen reader announces nothing useful about what it does.
- Suggested fix: Add a visible label, text content, or aria-label so students know what the control does.
- Manual review: The accessible name is estimated; confirm with browser dev tools or a screen reader what is actually announced.
- Browser check limitation: Accessible names are estimated from labels, text, and common attributes, not from a full accessibility tree computation.

Evidence:

- tag: a
- id: MainCopy_ctl11_DocumentsList_ProfileLink_1
- href: https://www.ahead.org/membership/network/members/profile?UserKey=c03dd8e5-a84a-474d-8649-a2d38d6e54ab
- step: 42
- detected_in: browser_interaction
- reason: A keyboard user reached this control, but it has no label, text, aria-label, or other usable name.

### 25. Keyboard focus landed on a hidden element

- Issue type: browser_focus_on_hidden_element
- Rule: Keyboard focus landed on a hidden element
- Category: Keyboard Interaction
- Severity: high
- Why it matters: When focus moves to an invisible element, keyboard users lose track of where they are on the page.
- Suggested fix: Remove hidden elements from the Tab order with tabindex="-1" or make them visible when focused.
- Manual review: Check whether the element becomes visible on focus (like a skip link); that pattern is fine.
- Browser check limitation: Visibility is estimated from element size and CSS and may not match what users actually see.

Evidence:

- tag: a
- id: MainCopy_ctl11_DocumentsList_ProfileLink_1
- href: https://www.ahead.org/membership/network/members/profile?UserKey=c03dd8e5-a84a-474d-8649-a2d38d6e54ab
- step: 42
- detected_in: browser_interaction
- reason: This element received keyboard focus but does not appear to be visible on the page.

### 26. Focused control has no accessible name

- Issue type: browser_focused_control_missing_name
- Rule: Focused control has no accessible name
- Category: Keyboard Interaction
- Severity: high
- Why it matters: A keyboard user can reach the control, but without a name a screen reader announces nothing useful about what it does.
- Suggested fix: Add a visible label, text content, or aria-label so students know what the control does.
- Manual review: The accessible name is estimated; confirm with browser dev tools or a screen reader what is actually announced.
- Browser check limitation: Accessible names are estimated from labels, text, and common attributes, not from a full accessibility tree computation.

Evidence:

- tag: a
- id: MainCopy_ctl11_DocumentsList_ProfileLink_2
- href: https://www.ahead.org/membership/network/members/profile?UserKey=c03dd8e5-a84a-474d-8649-a2d38d6e54ab
- step: 46
- detected_in: browser_interaction
- reason: A keyboard user reached this control, but it has no label, text, aria-label, or other usable name.

### 27. Keyboard focus landed on a hidden element

- Issue type: browser_focus_on_hidden_element
- Rule: Keyboard focus landed on a hidden element
- Category: Keyboard Interaction
- Severity: high
- Why it matters: When focus moves to an invisible element, keyboard users lose track of where they are on the page.
- Suggested fix: Remove hidden elements from the Tab order with tabindex="-1" or make them visible when focused.
- Manual review: Check whether the element becomes visible on focus (like a skip link); that pattern is fine.
- Browser check limitation: Visibility is estimated from element size and CSS and may not match what users actually see.

Evidence:

- tag: a
- id: MainCopy_ctl11_DocumentsList_ProfileLink_2
- href: https://www.ahead.org/membership/network/members/profile?UserKey=c03dd8e5-a84a-474d-8649-a2d38d6e54ab
- step: 46
- detected_in: browser_interaction
- reason: This element received keyboard focus but does not appear to be visible on the page.

### 28. Focused control has no accessible name

- Issue type: browser_focused_control_missing_name
- Rule: Focused control has no accessible name
- Category: Keyboard Interaction
- Severity: high
- Why it matters: A keyboard user can reach the control, but without a name a screen reader announces nothing useful about what it does.
- Suggested fix: Add a visible label, text content, or aria-label so students know what the control does.
- Manual review: The accessible name is estimated; confirm with browser dev tools or a screen reader what is actually announced.
- Browser check limitation: Accessible names are estimated from labels, text, and common attributes, not from a full accessibility tree computation.

Evidence:

- tag: a
- id: MainCopy_ctl11_DocumentsList_ProfileLink_3
- href: https://www.ahead.org/membership/network/members/profile?UserKey=01cb0141-971b-419b-8de1-5b0796a000f4
- step: 50
- detected_in: browser_interaction
- reason: A keyboard user reached this control, but it has no label, text, aria-label, or other usable name.

### 29. Keyboard focus landed on a hidden element

- Issue type: browser_focus_on_hidden_element
- Rule: Keyboard focus landed on a hidden element
- Category: Keyboard Interaction
- Severity: high
- Why it matters: When focus moves to an invisible element, keyboard users lose track of where they are on the page.
- Suggested fix: Remove hidden elements from the Tab order with tabindex="-1" or make them visible when focused.
- Manual review: Check whether the element becomes visible on focus (like a skip link); that pattern is fine.
- Browser check limitation: Visibility is estimated from element size and CSS and may not match what users actually see.

Evidence:

- tag: a
- id: MainCopy_ctl11_DocumentsList_ProfileLink_3
- href: https://www.ahead.org/membership/network/members/profile?UserKey=01cb0141-971b-419b-8de1-5b0796a000f4
- step: 50
- detected_in: browser_interaction
- reason: This element received keyboard focus but does not appear to be visible on the page.

### 30. Focused control has no accessible name

- Issue type: browser_focused_control_missing_name
- Rule: Focused control has no accessible name
- Category: Keyboard Interaction
- Severity: high
- Why it matters: A keyboard user can reach the control, but without a name a screen reader announces nothing useful about what it does.
- Suggested fix: Add a visible label, text content, or aria-label so students know what the control does.
- Manual review: The accessible name is estimated; confirm with browser dev tools or a screen reader what is actually announced.
- Browser check limitation: Accessible names are estimated from labels, text, and common attributes, not from a full accessibility tree computation.

Evidence:

- tag: a
- href: http://accessinghigherground.org/
- step: 58
- detected_in: browser_interaction
- reason: A keyboard user reached this control, but it has no label, text, aria-label, or other usable name.

### 31. Link is missing an accessible name

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
- href: https://www.ahead.org/events-programming/conferences/2026-virtual
- line: 487
- detected_in: browser_dom
- reason: Link has no usable text, aria-label, title, or image alt text.

```html
<a href="https://www.ahead.org/events-programming/conferences/2026-virtual" tabindex="0" data-feathr-click-track="true" data-feathr-link-aids="5c8293d30d21f34805e168ef">
```

### 32. Link is missing an accessible name

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
- id: MainCopy_ctl05_BlogList_ProfileLink_0
- href: https://www.ahead.org/people/ahead
- line: 511
- detected_in: browser_dom
- reason: Link has no usable text, aria-label, title, or image alt text.

```html
<a id="MainCopy_ctl05_BlogList_ProfileLink_0" href="https://www.ahead.org/people/ahead" data-feathr-click-track="true" data-feathr-link-aids="5c8293d30d21f34805e168ef">
```

### 33. Link is missing an accessible name

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
- id: MainCopy_ctl05_BlogList_ProfileLink_1
- href: https://www.ahead.org/people/ahead
- line: 615
- detected_in: browser_dom
- reason: Link has no usable text, aria-label, title, or image alt text.

```html
<a id="MainCopy_ctl05_BlogList_ProfileLink_1" href="https://www.ahead.org/people/ahead" data-feathr-click-track="true" data-feathr-link-aids="5c8293d30d21f34805e168ef">
```

### 34. Link is missing an accessible name

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
- id: MainCopy_ctl05_BlogList_ProfileLink_2
- href: https://www.ahead.org/people/ahead
- line: 717
- detected_in: browser_dom
- reason: Link has no usable text, aria-label, title, or image alt text.

```html
<a id="MainCopy_ctl05_BlogList_ProfileLink_2" href="https://www.ahead.org/people/ahead" data-feathr-click-track="true" data-feathr-link-aids="5c8293d30d21f34805e168ef">
```

### 35. Link is missing an accessible name

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
- id: MainCopy_ctl11_DocumentsList_ProfileLink_0
- href: https://www.ahead.org/membership/network/members/profile?UserKey=80924270-8dc7-4e28-a294-019a83e6f89c
- line: 1023
- detected_in: browser_dom
- reason: Link has no usable text, aria-label, title, or image alt text.

```html
<a id="MainCopy_ctl11_DocumentsList_ProfileLink_0" href="https://www.ahead.org/membership/network/members/profile?UserKey=80924270-8dc7-4e28-a294-019a83e6f89c" data-feathr-click-track="true" data-f...
```

### 36. Link is missing an accessible name

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
- id: MainCopy_ctl11_DocumentsList_ProfileLink_1
- href: https://www.ahead.org/membership/network/members/profile?UserKey=c03dd8e5-a84a-474d-8649-a2d38d6e54ab
- line: 1143
- detected_in: browser_dom
- reason: Link has no usable text, aria-label, title, or image alt text.

```html
<a id="MainCopy_ctl11_DocumentsList_ProfileLink_1" href="https://www.ahead.org/membership/network/members/profile?UserKey=c03dd8e5-a84a-474d-8649-a2d38d6e54ab" data-feathr-click-track="true" data-f...
```

### 37. Link is missing an accessible name

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
- id: MainCopy_ctl11_DocumentsList_ProfileLink_2
- href: https://www.ahead.org/membership/network/members/profile?UserKey=c03dd8e5-a84a-474d-8649-a2d38d6e54ab
- line: 1263
- detected_in: browser_dom
- reason: Link has no usable text, aria-label, title, or image alt text.

```html
<a id="MainCopy_ctl11_DocumentsList_ProfileLink_2" href="https://www.ahead.org/membership/network/members/profile?UserKey=c03dd8e5-a84a-474d-8649-a2d38d6e54ab" data-feathr-click-track="true" data-f...
```

### 38. Link is missing an accessible name

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
- id: MainCopy_ctl11_DocumentsList_ProfileLink_3
- href: https://www.ahead.org/membership/network/members/profile?UserKey=01cb0141-971b-419b-8de1-5b0796a000f4
- line: 1383
- detected_in: browser_dom
- reason: Link has no usable text, aria-label, title, or image alt text.

```html
<a id="MainCopy_ctl11_DocumentsList_ProfileLink_3" href="https://www.ahead.org/membership/network/members/profile?UserKey=01cb0141-971b-419b-8de1-5b0796a000f4" data-feathr-click-track="true" data-f...
```

### 39. Link is missing an accessible name

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
- href: http://accessinghigherground.org/
- line: 1537
- detected_in: browser_dom
- reason: Link has no usable text, aria-label, title, or image alt text.

```html
<a href="http://accessinghigherground.org/" data-feathr-click-track="true" data-feathr-link-aids="5c8293d30d21f34805e168ef">
```

### 40. Rendered text may have low contrast

- Issue type: low_contrast_text
- Rule: Rendered text may have low contrast
- Category: Low Vision
- Severity: medium
- Why it matters: Low-vision readers may not be able to read text when the computed foreground and background colors are too similar.
- Suggested fix: Increase foreground/background contrast and confirm the final design with manual review.
- Manual review: Confirm the sampled colors match what users actually see, especially over gradients, images, and layered components.
- Browser check limitation: The check samples browser-computed colors and does not prove full WCAG color contrast compliance.

Evidence:

- tag: a
- text: About
- detected_in: low_vision
- reason: Computed foreground/background contrast is below the conservative 4.5:1 review threshold.

### 41. Rendered text may have low contrast

- Issue type: low_contrast_text
- Rule: Rendered text may have low contrast
- Category: Low Vision
- Severity: medium
- Why it matters: Low-vision readers may not be able to read text when the computed foreground and background colors are too similar.
- Suggested fix: Increase foreground/background contrast and confirm the final design with manual review.
- Manual review: Confirm the sampled colors match what users actually see, especially over gradients, images, and layered components.
- Browser check limitation: The check samples browser-computed colors and does not prove full WCAG color contrast compliance.

Evidence:

- tag: a
- text: Membership
- detected_in: low_vision
- reason: Computed foreground/background contrast is below the conservative 4.5:1 review threshold.

### 42. Rendered text may have low contrast

- Issue type: low_contrast_text
- Rule: Rendered text may have low contrast
- Category: Low Vision
- Severity: medium
- Why it matters: Low-vision readers may not be able to read text when the computed foreground and background colors are too similar.
- Suggested fix: Increase foreground/background contrast and confirm the final design with manual review.
- Manual review: Confirm the sampled colors match what users actually see, especially over gradients, images, and layered components.
- Browser check limitation: The check samples browser-computed colors and does not prove full WCAG color contrast compliance.

Evidence:

- tag: a
- text: Programming
- detected_in: low_vision
- reason: Computed foreground/background contrast is below the conservative 4.5:1 review threshold.

### 43. Rendered text may have low contrast

- Issue type: low_contrast_text
- Rule: Rendered text may have low contrast
- Category: Low Vision
- Severity: medium
- Why it matters: Low-vision readers may not be able to read text when the computed foreground and background colors are too similar.
- Suggested fix: Increase foreground/background contrast and confirm the final design with manual review.
- Manual review: Confirm the sampled colors match what users actually see, especially over gradients, images, and layered components.
- Browser check limitation: The check samples browser-computed colors and does not prove full WCAG color contrast compliance.

Evidence:

- tag: a
- text: Professional Resources
- detected_in: low_vision
- reason: Computed foreground/background contrast is below the conservative 4.5:1 review threshold.

### 44. Rendered text may have low contrast

- Issue type: low_contrast_text
- Rule: Rendered text may have low contrast
- Category: Low Vision
- Severity: medium
- Why it matters: Low-vision readers may not be able to read text when the computed foreground and background colors are too similar.
- Suggested fix: Increase foreground/background contrast and confirm the final design with manual review.
- Manual review: Confirm the sampled colors match what users actually see, especially over gradients, images, and layered components.
- Browser check limitation: The check samples browser-computed colors and does not prove full WCAG color contrast compliance.

Evidence:

- tag: a
- text: Research
- detected_in: low_vision
- reason: Computed foreground/background contrast is below the conservative 4.5:1 review threshold.

### 45. Rendered text may have low contrast

- Issue type: low_contrast_text
- Rule: Rendered text may have low contrast
- Category: Low Vision
- Severity: medium
- Why it matters: Low-vision readers may not be able to read text when the computed foreground and background colors are too similar.
- Suggested fix: Increase foreground/background contrast and confirm the final design with manual review.
- Manual review: Confirm the sampled colors match what users actually see, especially over gradients, images, and layered components.
- Browser check limitation: The check samples browser-computed colors and does not prove full WCAG color contrast compliance.

Evidence:

- tag: a
- text: Communities
- detected_in: low_vision
- reason: Computed foreground/background contrast is below the conservative 4.5:1 review threshold.

### 46. Fixed or wide content may prevent reflow

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
- id: MPOuterMost
- text: Skip to main content (Press Enter). SIGN IN Search Button Skip auxiliary navigat
- detected_in: low_vision
- reason: A rendered element is wider than the narrow viewport or uses a large fixed pixel width.

### 47. Fixed or wide content may prevent reflow

- Issue type: zoom_fixed_width_content
- Rule: Fixed or wide content may prevent reflow
- Category: Low Vision
- Severity: medium
- Why it matters: Large fixed-width elements can force horizontal scrolling and hide content when users zoom or use narrow windows.
- Suggested fix: Replace fixed-width layout with responsive sizing such as max-width: 100%.
- Manual review: Confirm whether the wide element is essential and whether all content remains reachable without two-dimensional scrolling.
- Browser check limitation: The check flags obvious wide rendered elements and fixed pixel widths; it may miss complex layout problems.

Evidence:

- tag: form
- id: MasterPageForm
- text: Skip to main content (Press Enter). SIGN IN Search Button Skip auxiliary navigat
- detected_in: low_vision
- reason: A rendered element is wider than the narrow viewport or uses a large fixed pixel width.

### 48. Fixed or wide content may prevent reflow

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
- detected_in: low_vision
- reason: A rendered element is wider than the narrow viewport or uses a large fixed pixel width.

### 49. Focused element may not show a visible focus indicator

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
- id: megaanchor2
- text: About
- step: 13
- detected_in: low_vision
- reason: The focused element did not expose an obvious outline, box-shadow, or border focus style in computed CSS.

### 50. Focused element may not show a visible focus indicator

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
- id: megaanchor3
- text: Membership
- step: 14
- detected_in: low_vision
- reason: The focused element did not expose an obvious outline, box-shadow, or border focus style in computed CSS.

### 51. Focused element may not show a visible focus indicator

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
- id: megaanchor4
- text: Programming
- step: 15
- detected_in: low_vision
- reason: The focused element did not expose an obvious outline, box-shadow, or border focus style in computed CSS.

### 52. Focused element may not show a visible focus indicator

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
- id: megaanchor5
- text: Professional Resources
- step: 16
- detected_in: low_vision
- reason: The focused element did not expose an obvious outline, box-shadow, or border focus style in computed CSS.

### 53. Focused element may not show a visible focus indicator

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
- id: megaanchor6
- text: Research
- step: 17
- detected_in: low_vision
- reason: The focused element did not expose an obvious outline, box-shadow, or border focus style in computed CSS.

### 54. Focused element may not show a visible focus indicator

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
- id: megaanchor7
- text: Communities
- step: 18
- detected_in: low_vision
- reason: The focused element did not expose an obvious outline, box-shadow, or border focus style in computed CSS.

## Limitations

- This prototype runs static HTML checks plus a basic keyboard interaction audit.
- It does not replace a full human accessibility audit.
- Browser mode does not simulate a full screen reader, and accessible names are estimated.
- Low-vision browser checks are conservative heuristics and require manual review.

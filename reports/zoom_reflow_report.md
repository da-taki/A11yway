# A11yway Accessibility Report

## Summary

- Source: examples/sample_zoom_reflow.html
- Source type: file
- Issues found: 3
- Agents used: Keyboard-only student
- Checks run: html_form_labels, interactive_names, image_alt_text, heading_structure, page_metadata, media_accessibility, keyboard_focus_traversal, browser_dom_snapshot, accessibility_tree_announce, rendered_color_contrast, zoom_reflow_200_400, focus_visibility

### Counts By Severity

- high: 2
- medium: 1

### Counts By Issue Type

- reflow_horizontal_scroll: 1
- reflow_clipped_content: 1
- reflow_overlap: 1

## Browser Mode Summary

- Analysis modes: static, browser, low_vision
- Browser audit success: true
- Checks run: keyboard_focus_traversal, browser_dom_snapshot, accessibility_tree_announce
- Focus trace length: 2

## Browser Interaction Trace

| Step | Tag | Accessible name guess | ID/Name | Text/Href |
| ---: | --- | --- | --- | --- |
| 1 | button | Print timetable |  | Print timetable |
| 2 | button | Download timetable |  | Download timetable |

## Announce Transcript

What Chromium's computed accessibility tree exposes at each observed focus stop. This approximates what a screen reader would announce; real screen readers can differ.

1. button, "Print timetable"
2. button, "Download timetable"

### Browser Limitations

- Browser mode approximates keyboard interaction but does not simulate a full screen reader.
- Accessible names are estimated and require manual review.
- The announce transcript comes from Chromium's computed accessibility tree in one browser run.
- Real screen readers (NVDA, JAWS, VoiceOver) apply their own rules and can announce things differently.

## Low-Vision Checks

- Status: passed
- Checks run: rendered_color_contrast, zoom_reflow_200_400, focus_visibility
- Contrast samples analyzed: 7
- Viewport width for reflow check: 320
- Document scroll width: 926
- Horizontal overflow amount: 606
- Focus stops checked: 2
- Focus indicator concerns: 0

### Zoom Reflow Levels

| Zoom | Viewport width | Scroll width | Overflow | Clipped | Overlaps |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 200% | 640 | 926 | 286 | 1 | 0 |
| 400% | 320 | 926 | 606 | 1 | 1 |

### Low-Vision Limitations

- Low-vision checks use browser-computed styles and conservative heuristics.
- Rendered color contrast checks do not prove full WCAG conformance.
- Zoom checks emulate browser zoom through the equivalent CSS viewport widths (WCAG 1.4.10 uses 320 CSS px at 400%); gradients, images, and intentional horizontal-scroll regions need manual review.
- Focus indicator detection may miss custom focus styles.

## Issues Found

### 1. Page requires horizontal scrolling under zoom

- Issue type: reflow_horizontal_scroll
- Rule: Page requires horizontal scrolling under zoom
- Category: Low Vision
- Severity: high
- Why it matters: At high zoom, readers must scroll horizontally for every line when the page does not reflow into one column, which makes reading exhausting or impossible.
- Suggested fix: Use responsive layout and max-width: 100% so content reflows into one column at high zoom. Intentional horizontal-scroll regions (data tables, maps) are allowed by WCAG and need manual review.
- Manual review: Data tables, maps, and similar two-dimensional content may scroll horizontally by design; WCAG allows that, so confirm the overflow is not essential content.
- Browser check limitation: Zoom is emulated through the equivalent CSS viewport widths (1280 base at 200% and 400%) in one Chromium run; gradients and image-heavy layouts need manual review.

Evidence:

- detected_in: low_vision
- reason: The document is wider than the viewport at 200%, 400% zoom, so zoomed readers must scroll horizontally for every line (WCAG 1.4.10 reflow reference: 320 CSS px at 400%).

### 2. Content is clipped outside the zoomed viewport

- Issue type: reflow_clipped_content
- Rule: Content is clipped outside the zoomed viewport
- Category: Low Vision
- Severity: high
- Why it matters: Text or controls cut off beyond the reachable area disappear entirely for zoomed readers; they cannot scroll to them.
- Suggested fix: Avoid fixed offsets and overflow: hidden cut-offs; let content wrap within the viewport width.
- Manual review: Confirm the clipped element holds real content; decorative elements cut by design are not a barrier.
- Browser check limitation: Bounding boxes come from one Chromium run at emulated zoom widths; animation and lazy layout can shift results.

Evidence:

- tag: p
- text: Bring your student card to every exam.
- detected_in: low_vision
- zoom_percent: 200
- viewport_width: 640
- clipped_by: document
- reason: At 200% zoom this element extends beyond the reachable area, so zoomed readers cannot see or use it.

### 3. Interactive elements overlap under zoom

- Issue type: reflow_overlap
- Rule: Interactive elements overlap under zoom
- Category: Low Vision
- Severity: medium
- Why it matters: Controls that collide at high zoom can cover each other, so zoomed readers cannot see or activate the one underneath.
- Suggested fix: Let controls wrap or stack at narrow widths instead of using absolute positions that collide under zoom.
- Manual review: Confirm the overlap visually; intentional stacking such as a badge over a button can be fine.
- Browser check limitation: Overlap uses bounding-box intersection of visible controls in one Chromium run and cannot judge visual intent.

Evidence:

- detected_in: low_vision
- zoom_percent: 400
- viewport_width: 320
- first_element: button "Print timetable"
- second_element: button "Download timetable"
- reason: At 400% zoom these two controls overlap, which can hide one of them or make both hard to activate.

## Limitations

- This prototype runs static HTML checks plus a basic keyboard interaction audit.
- It does not replace a full human accessibility audit.
- Browser mode does not simulate a full screen reader, and accessible names are estimated.
- Low-vision browser checks are conservative heuristics and require manual review.

# A11yway Accessibility Report

## Summary

- Source: examples/sample_zoom_reflow_fixed.html
- Source type: file
- Issues found: 0
- Agents used: Keyboard-only student
- Checks run: html_form_labels, interactive_names, image_alt_text, heading_structure, page_metadata, media_accessibility, keyboard_focus_traversal, browser_dom_snapshot, accessibility_tree_announce, rendered_color_contrast, zoom_reflow_200_400, focus_visibility

### Counts By Severity

- None

### Counts By Issue Type

- None

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
- Document scroll width: 320
- Horizontal overflow amount: 0
- Focus stops checked: 2
- Focus indicator concerns: 0

### Zoom Reflow Levels

| Zoom | Viewport width | Scroll width | Overflow | Clipped | Overlaps |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 200% | 640 | 640 | 0 | 0 | 0 |
| 400% | 320 | 320 | 0 | 0 | 0 |

### Low-Vision Limitations

- Low-vision checks use browser-computed styles and conservative heuristics.
- Rendered color contrast checks do not prove full WCAG conformance.
- Zoom checks emulate browser zoom through the equivalent CSS viewport widths (WCAG 1.4.10 uses 320 CSS px at 400%); gradients, images, and intentional horizontal-scroll regions need manual review.
- Focus indicator detection may miss custom focus styles.

## Issues Found

No issues found by the current static checks.
## Limitations

- This prototype runs static HTML checks plus a basic keyboard interaction audit.
- It does not replace a full human accessibility audit.
- Browser mode does not simulate a full screen reader, and accessible names are estimated.
- Low-vision browser checks are conservative heuristics and require manual review.

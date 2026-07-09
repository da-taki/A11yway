# A11yway Accessibility Report

## Summary

- Source: examples/sample_keyboard_trap_fixed.html
- Source type: file
- Issues found: 0
- Agents used: Keyboard-only student
- Checks run: html_form_labels, interactive_names, image_alt_text, heading_structure, page_metadata, media_accessibility, keyboard_focus_traversal, browser_dom_snapshot, accessibility_tree_announce

### Counts By Severity

- None

### Counts By Issue Type

- None

## Browser Mode Summary

- Analysis modes: static, browser
- Browser audit success: true
- Checks run: keyboard_focus_traversal, browser_dom_snapshot, accessibility_tree_announce
- Focus trace length: 6

## Browser Interaction Trace

| Step | Tag | Accessible name guess | ID/Name | Text/Href |
| ---: | --- | --- | --- | --- |
| 1 | select | How was the last lesson? | rating | Choose a rating Good Okay |
| 2 | button | Send feedback | send_feedback | Send feedback |
| 3 | button | Dismiss | dismiss_feedback | Dismiss |
| 4 | input | Favorite topic this term | favorite_topic |  |
| 5 | textarea | Comments | comments |  |
| 6 | button | Submit survey |  | Submit survey |

## Announce Transcript

What Chromium's computed accessibility tree exposes at each observed focus stop. This approximates what a screen reader would announce; real screen readers can differ.

1. combobox, "How was the last lesson?", collapsed
2. button, "Send feedback"
3. button, "Dismiss"
4. textbox, "Favorite topic this term"
5. textbox, "Comments"
6. button, "Submit survey"

### Browser Limitations

- Browser mode approximates keyboard interaction but does not simulate a full screen reader.
- Accessible names are estimated and require manual review.
- The announce transcript comes from Chromium's computed accessibility tree in one browser run.
- Real screen readers (NVDA, JAWS, VoiceOver) apply their own rules and can announce things differently.

## Issues Found

No issues found by the current static checks.
## Limitations

- This prototype runs static HTML checks plus a basic keyboard interaction audit.
- It does not replace a full human accessibility audit.
- Browser mode does not simulate a full screen reader, and accessible names are estimated.

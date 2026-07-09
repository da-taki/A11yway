# A11yway Accessibility Report

## Summary

- Source: examples/sample_keyboard_trap.html
- Source type: file
- Issues found: 1
- Agents used: Keyboard-only student
- Checks run: html_form_labels, interactive_names, image_alt_text, heading_structure, page_metadata, media_accessibility, keyboard_focus_traversal, browser_dom_snapshot, accessibility_tree_announce

### Counts By Severity

- high: 1

### Counts By Issue Type

- keyboard_trap: 1

## Browser Mode Summary

- Analysis modes: static, browser
- Browser audit success: true
- Checks run: keyboard_focus_traversal, browser_dom_snapshot, accessibility_tree_announce
- Focus trace length: 40

## Browser Interaction Trace

| Step | Tag | Accessible name guess | ID/Name | Text/Href |
| ---: | --- | --- | --- | --- |
| 1 | select | How was the last lesson? | rating | Choose a rating Good Okay |
| 2 | button | Send feedback | send_feedback | Send feedback |
| 3 | button | Dismiss | dismiss_feedback | Dismiss |
| 4 | select | How was the last lesson? | rating | Choose a rating Good Okay |
| 5 | button | Send feedback | send_feedback | Send feedback |
| 6 | button | Dismiss | dismiss_feedback | Dismiss |
| 7 | select | How was the last lesson? | rating | Choose a rating Good Okay |
| 8 | button | Send feedback | send_feedback | Send feedback |
| 9 | button | Dismiss | dismiss_feedback | Dismiss |
| 10 | select | How was the last lesson? | rating | Choose a rating Good Okay |
| 11 | button | Send feedback | send_feedback | Send feedback |
| 12 | button | Dismiss | dismiss_feedback | Dismiss |
| 13 | select | How was the last lesson? | rating | Choose a rating Good Okay |
| 14 | button | Send feedback | send_feedback | Send feedback |
| 15 | button | Dismiss | dismiss_feedback | Dismiss |
| 16 | select | How was the last lesson? | rating | Choose a rating Good Okay |
| 17 | button | Send feedback | send_feedback | Send feedback |
| 18 | button | Dismiss | dismiss_feedback | Dismiss |
| 19 | select | How was the last lesson? | rating | Choose a rating Good Okay |
| 20 | button | Send feedback | send_feedback | Send feedback |

Trace truncated: showing the first 20 of 40 steps.

## Announce Transcript

What Chromium's computed accessibility tree exposes at each observed focus stop. This approximates what a screen reader would announce; real screen readers can differ.

1. combobox, "How was the last lesson?", collapsed
2. button, "Send feedback"
3. button, "Dismiss"
4. combobox, "How was the last lesson?", collapsed
5. button, "Send feedback"
6. button, "Dismiss"
7. combobox, "How was the last lesson?", collapsed
8. button, "Send feedback"
9. button, "Dismiss"
10. combobox, "How was the last lesson?", collapsed
11. button, "Send feedback"
12. button, "Dismiss"
13. combobox, "How was the last lesson?", collapsed
14. button, "Send feedback"
15. button, "Dismiss"
16. combobox, "How was the last lesson?", collapsed
17. button, "Send feedback"
18. button, "Dismiss"
19. combobox, "How was the last lesson?", collapsed
20. button, "Send feedback"
21. button, "Dismiss"
22. combobox, "How was the last lesson?", collapsed
23. button, "Send feedback"
24. button, "Dismiss"
25. combobox, "How was the last lesson?", collapsed
26. button, "Send feedback"
27. button, "Dismiss"
28. combobox, "How was the last lesson?", collapsed
29. button, "Send feedback"
30. button, "Dismiss"
31. combobox, "How was the last lesson?", collapsed
32. button, "Send feedback"
33. button, "Dismiss"
34. combobox, "How was the last lesson?", collapsed
35. button, "Send feedback"
36. button, "Dismiss"
37. combobox, "How was the last lesson?", collapsed
38. button, "Send feedback"
39. button, "Dismiss"
40. combobox, "How was the last lesson?", collapsed

### Browser Limitations

- Browser mode approximates keyboard interaction but does not simulate a full screen reader.
- Accessible names are estimated and require manual review.
- The announce transcript comes from Chromium's computed accessibility tree in one browser run.
- Real screen readers (NVDA, JAWS, VoiceOver) apply their own rules and can announce things differently.

## Issues Found

### 1. Keyboard focus is trapped in a loop

- Issue type: keyboard_trap
- Rule: Keyboard focus is trapped in a loop
- Category: Keyboard Interaction
- Severity: high
- Why it matters: Tab kept cycling through the same subset of elements without ever reaching the rest of the page, so a keyboard-only user is stuck and cannot finish anything beyond the loop.
- Suggested fix: Let Tab move past the widget, or provide a standard way out, such as closing a modal with Escape and returning focus. Related to WCAG 2.1.2 No Keyboard Trap.
- Manual review: Confirm the loop by hand and check for documented escape mechanisms (Escape, arrow keys, custom shortcuts) that Tab-only traversal cannot see.
- Browser check limitation: Based on observed Tab behavior in one Chromium run. It cannot verify custom escape mechanisms, and the count of unreached elements is an estimate from visible focusable elements.

Evidence:

- detected_in: browser_interaction
- loop_sequence: button#send_feedback -> button#dismiss_feedback -> select#rating
- loop_length: 3
- unreached_focusable_count: 3
- tab_presses: 40
- reason: Tab keeps cycling through the same 3 element(s) without passing through the rest of the page; about 3 focusable element(s) were never reached within 40 Tab presses.

## Limitations

- This prototype runs static HTML checks plus a basic keyboard interaction audit.
- It does not replace a full human accessibility audit.
- Browser mode does not simulate a full screen reader, and accessible names are estimated.

# A11yway Accessibility Report

## Summary

- Source: examples/sample_announce_transcript.html
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
| 1 | a | Read the library rules |  | Read the library rules |
| 2 | input | Full name | full_name |  |
| 3 | select | Grade level | grade_level | Choose a grade Grade 9 Grade 10 |
| 4 | input | Send me the monthly reading list | newsletter |  |
| 5 | button | Show opening hours |  | Show opening hours |
| 6 | button | Sign up for a library card |  | Sign up for a library card |

## Announce Transcript

What Chromium's computed accessibility tree exposes at each observed focus stop. This approximates what a screen reader would announce; real screen readers can differ.

1. link, "Read the library rules"
2. textbox, "Full name", required
3. combobox, "Grade level", collapsed
4. checkbox, "Send me the monthly reading list", checked
5. button, "Show opening hours", collapsed
6. button, "Sign up for a library card"

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

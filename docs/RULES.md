# A11yway Check Rules

A11yway is a prototype. The static checks below inspect HTML with the Python
standard library; the optional browser checks approximate keyboard navigation
in headless Chromium. Both are useful for finding common, high-impact barriers
on education pages, but they are not a complete accessibility audit and do not
replace human review or testing with disabled users.

Run `python -m a11yway.main --list-rules` for a quick listing, or
`python -m a11yway.main --rule missing_form_label` for details on one rule.

## Static Rule Overview

| Issue type | Category | Default severity | What it detects | Why it matters | Current limitation |
| --- | --- | --- | --- | --- | --- |
| `missing_form_label` | Forms | high | Inputs, textareas, and selects without a label, aria-label/labelledby, or title | Students cannot tell what information a field expects | Cannot see labels created dynamically by JavaScript |
| `missing_button_name` | Interactive Elements | high | Buttons without text, aria-label, title, or image alt text | Screen readers announce an unnamed button with no purpose | Cannot see names added by JavaScript or icon fonts |
| `missing_link_name` | Interactive Elements | high | Links without usable text, aria-label, title, or image alt text | Students cannot decide whether to follow an unnamed link | Cannot detect names injected by JavaScript |
| `generic_link_text` | Interactive Elements | medium | Link text like "click here" or "read more" | Links heard out of context are indistinguishable | Only matches a small list of generic phrases |
| `missing_image_alt` | Images | medium (high inside links/buttons) | Images with missing or empty alt that are not marked decorative | Screen reader users miss image content entirely | Cannot judge whether existing alt text is useful |
| `missing_h1` | Headings & Structure | medium | Pages without an h1 heading | Students cannot quickly confirm the page purpose | Cannot see headings rendered by JavaScript |
| `skipped_heading_level` | Headings & Structure | medium | Heading jumps such as h1 directly to h3 | Breaks the outline screen reader users navigate by | Follows document order only, not visual layout |
| `multiple_h1` | Headings & Structure | low | More than one h1 on the page | Makes the main topic harder to identify | Cannot evaluate visual presentation |
| `missing_page_title` | Page Metadata | medium | Missing or empty title element | The title is the first thing screen readers announce | Cannot see titles set by JavaScript |
| `missing_html_lang` | Page Metadata | medium | html element without a lang attribute | Screen readers may mispronounce the page content | Only inspects the html element, not mixed-language sections |
| `missing_video_captions` | Media | high | Video elements without a captions/subtitles track | Deaf and hard-of-hearing students cannot access spoken content | Cannot see player-level or burned-in captions |
| `missing_audio_transcript` | Media | high | Audio elements on pages with no visible "transcript" text | Audio-only content needs a text alternative | The "transcript" text search is a rough heuristic |

## Current Static Checks

The analyzer currently runs these check groups over the raw HTML:

- **Form labels** — form controls must have a programmatic label.
- **Interactive names** — links and buttons need clear accessible names.
- **Image alt text** — images need useful alternatives or a decorative marker.
- **Heading structure** — one h1, no skipped levels.
- **Page metadata** — page title and document language.
- **Media accessibility** — captions tracks for video, transcripts for audio.

Findings include an evidence snippet, the reason the check fired, and an
approximate source line number so reviewers can verify each result manually.

## Browser Interaction Checks (optional)

With `--browser` and Playwright installed, A11yway loads the page in headless
Chromium, presses Tab repeatedly to trace keyboard focus, and re-runs the
static checks on the JavaScript-rendered DOM. Rendered-DOM findings reuse the
static issue types above with `detected_in: "browser_dom"` in their evidence.

| Issue type | Category | Default severity | What it detects | Why it matters | Current limitation |
| --- | --- | --- | --- | --- | --- |
| `browser_no_focusable_elements` | Keyboard Interaction | high | Interactive-looking elements exist but nothing can receive keyboard focus | Keyboard-only students are completely blocked | Counts common focusable selectors; may miss unusual custom widgets |
| `browser_focus_not_moving` | Keyboard Interaction | high | Pressing Tab never focuses page content despite focusable elements | Keyboard-only students cannot start the task | Headless Tab behavior can differ slightly from a real browser |
| `browser_repeated_focus` | Keyboard Interaction | medium | The same element stays focused across several Tab presses | Suggests a keyboard trap that strands students | A heuristic; cannot prove a real trap |
| `browser_focused_control_missing_name` | Keyboard Interaction | high | A focused link/button/form control has no estimated accessible name | Screen readers announce nothing useful about the control | Accessible names are estimated, not computed from the accessibility tree |
| `browser_focus_on_hidden_element` | Keyboard Interaction | high | Focus lands on an element that appears invisible | Keyboard users lose track of where they are | Visibility is estimated from size and CSS |

Browser mode limitations:

- It approximates keyboard interaction; it does not simulate a full screen reader.
- Accessible names are estimated and require manual review.
- It does not crawl websites or log into private portals.
- Use it only on public pages or pages you have permission to test.

## Not Yet Covered

These areas are out of scope for the current prototype:

- Full screen-reader simulation (browser mode only estimates accessible names)
- Complex keyboard interaction beyond Tab traversal (arrow keys, shortcuts, modals)
- Authenticated portals and login-protected pages
- PDFs and other documents
- Mobile app accessibility
- Color contrast and visual presentation checks
- Full WCAG certification — A11yway results are hints for human reviewers,
  not conformance claims

If a page passes every current check, that only means these specific checks
found nothing. Manual review is still required.

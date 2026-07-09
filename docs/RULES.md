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

- **Form labels**: form controls must have a programmatic label.
- **Interactive names**: links and buttons need clear accessible names.
- **Image alt text**: images need useful alternatives or a decorative marker.
- **Heading structure**: one h1, no skipped levels.
- **Page metadata**: page title and document language.
- **Media accessibility**: captions tracks for video, transcripts for audio.

Findings include an evidence snippet, the reason the check fired, and an
approximate source line number so reviewers can verify each result manually.

## Indic-Language Checks (static)

These checks run in every static analysis with no browser or external
dependency. They detect Indic-script text through Unicode ranges
(Devanagari, Bengali, Gurmukhi, Gujarati, Oriya, Tamil, Telugu, Kannada,
Malayalam) and compare it against the declared language markup, because
text-to-speech picks its voice from the lang attribute.

| Issue type | Category | Default severity | What it detects | Why it matters | Current limitation |
| --- | --- | --- | --- | --- | --- |
| `missing_lang_indic` | Language | high | Indic-script text whose effective lang is missing or non-matching (e.g. Gurmukhi under `lang="en"`) | TTS reads the text with the wrong voice, producing garbled speech | Unicode-range heuristic; languages sharing a script cannot be told apart, and transliterated text is invisible to it |
| `lang_mismatch` | Language | high | An element's own lang attribute contradicts the dominant script of its text (e.g. `lang="ta"` over Devanagari) | A wrong declaration is worse than none; screen readers pick the wrong voice | Only fires when the script itself contradicts the declaration |
| `mixed_script_element` | Language | medium | One text node mixing several Latin words with Indic text and no lang boundary | Speech engines cannot switch voices mid-node and commonly garble one language | Conservative heuristic: ignores numbers, short acronyms, and single loanwords; may flag intentional bilingual lines |

Indic-language limitations:

- Script detection is a heuristic on Unicode ranges, not language
  identification.
- Transliterated text (Hindi written in Latin script) cannot be detected.
- The right lang value for a shared script (Hindi vs Marathi) needs a
  human decision.

## Browser Interaction Checks (optional)

With `--browser` and Playwright installed, A11yway loads the page in headless
Chromium, presses Tab repeatedly to trace keyboard focus, and re-runs the
static checks on the JavaScript-rendered DOM. Rendered-DOM findings reuse the
static issue types above with `detected_in: "browser_dom"` in their evidence.

At each focus stop, A11yway also asks Chromium's computed accessibility tree
(over the Chrome DevTools Protocol) for the element's role, accessible name,
and states (disabled, required, invalid, checked, expanded), and renders the
result as a numbered announce transcript in every report format. When the
tree is available for an element, `unnamed_focus_stop` supersedes the older
heuristic `browser_focused_control_missing_name` check for that element; the
heuristic only runs as a fallback when tree data cannot be captured.

| Issue type | Category | Default severity | What it detects | Why it matters | Current limitation |
| --- | --- | --- | --- | --- | --- |
| `browser_no_focusable_elements` | Keyboard Interaction | high | Interactive-looking elements exist but nothing can receive keyboard focus | Keyboard-only students are completely blocked | Counts common focusable selectors; may miss unusual custom widgets |
| `browser_focus_not_moving` | Keyboard Interaction | high | Pressing Tab never focuses page content despite focusable elements | Keyboard-only students cannot start the task | Headless Tab behavior can differ slightly from a real browser |
| `browser_repeated_focus` | Keyboard Interaction | medium | The same element stays focused across several Tab presses | Suggests a keyboard trap that strands students | A heuristic; cannot prove a real trap |
| `browser_focused_control_missing_name` | Keyboard Interaction | high | A focused link/button/form control has no estimated accessible name | Screen readers announce nothing useful about the control | Heuristic fallback; only used when accessibility tree data is unavailable for the element |
| `browser_focus_on_hidden_element` | Keyboard Interaction | high | Focus lands on an element that appears invisible | Keyboard users lose track of where they are | Visibility is estimated from size and CSS |
| `unnamed_focus_stop` | Keyboard Interaction | high | Chromium's accessibility tree computed an empty accessible name for a focus stop | A screen reader user hears at most a bare role and cannot tell what the element does | One Chromium run's computed tree, not a screen reader; NVDA, JAWS, and VoiceOver can differ |
| `keyboard_trap` | Keyboard Interaction | high | Tab cycles through the same subset of elements (confirmed twice, never passing the body) while other focusable elements are never reached | Keyboard-only users are stuck and cannot finish anything beyond the loop (WCAG 2.1.2 No Keyboard Trap) | Observed Tab behavior in one Chromium run; cannot verify custom escape mechanisms such as Escape handlers or shortcuts |
| `focus_lost` | Keyboard Interaction | medium | Tab lands on the document body repeatedly and focus never returns to page content | Keyboard users lose their place and cannot continue | One headless Chromium run; a single body pass between last and first element is normal and not flagged |

Browser mode limitations:

- It approximates keyboard interaction; it does not simulate a full screen reader.
- The announce transcript is Chromium's computed accessibility tree from one
  browser run; real screen readers (NVDA, JAWS, VoiceOver) apply their own
  rules and can announce things differently.
- When accessibility tree data cannot be captured, accessible names fall
  back to estimates and require manual review.
- It does not crawl websites or log into private portals.
- Use it only on public pages or pages you have permission to test.

## Low-Vision Browser Checks (optional)

With `--browser --low-vision`, A11yway samples browser-computed styles and
uses conservative heuristics for low-vision review. These checks are useful
signals for reviewers, not full WCAG certification.

| Issue type | Category | Default severity | What it detects | Why it matters | Current limitation |
| --- | --- | --- | --- | --- | --- |
| `low_contrast_text` | Low Vision | medium/high | Rendered text samples whose computed color contrast is below a conservative threshold | Low-vision readers may not be able to read the content | Does not prove full color-contrast compliance, especially over images or gradients |
| `reflow_horizontal_scroll` | Low Vision | high (400%) / medium (200% only) | The document is wider than the zoomed viewport at 200% or 400% zoom-equivalent widths | Zoomed readers must scroll horizontally for every line (WCAG 1.4.10 Reflow, reference 320 CSS px) | Zoom is emulated through equivalent viewport widths in one Chromium run; intentional scroll regions such as data tables are allowed by WCAG and need manual review |
| `reflow_clipped_content` | Low Vision | high | Text or controls whose bounding box sits beyond every reachable area at a zoom level | Clipped content disappears entirely for zoomed readers | Bounding boxes from one run; decorative cut-offs need manual confirmation |
| `reflow_overlap` | Low Vision | medium | Interactive elements whose bounding boxes collide at a zoom level | An overlapped control can be hidden or impossible to activate | Cannot judge visual intent; intentional stacking such as badges can be fine |
| `zoom_horizontal_overflow` | Low Vision | medium/high | (Legacy, no longer emitted) narrow-viewport overflow approximation | Kept so reports from older versions stay documented | Replaced by `reflow_horizontal_scroll` |
| `zoom_fixed_width_content` | Low Vision | medium | (Legacy, no longer emitted) wide or fixed-width rendered elements | Kept so reports from older versions stay documented | Replaced by the `reflow_*` checks |
| `focus_indicator_missing` | Low Vision | high | Focused elements without an obvious computed outline, border, or shadow | Keyboard users with low vision can lose track of focus | Heuristic; custom focus styles may need manual confirmation |

Low-vision limitations:

- Rendered contrast checks sample visible text and computed colors; they do
  not replace design review.
- Zoom checks lay the page out at the CSS widths browser zoom produces
  (640 px at 200%, 320 px at 400% from a 1280 px base, matching the WCAG
  1.4.10 reference); they run in one Chromium engine and do not prove full
  reflow compliance. Gradients, images, and intentional horizontal-scroll
  regions need manual review.
- Focus indicator detection may miss custom visual treatments.

## Browser Task Execution Checks (optional)

With `--browser --execute-task <task>` (or `--execute-tasks` in batch mode),
A11yway attempts a task's `browser_steps` using keyboard-only interaction:
focus moves with Tab, text is typed with the keyboard, and controls are
activated with Enter. The report states whether the task COMPLETED or was
BLOCKED, with per-step evidence. Steps are deterministic scripts defined in
the task JSON; this is not AI and does not infer extra actions. Supported
actions: `expect_visible_text`,
`assert_visible_text`, `wait_for_text`, `focus_by_label_or_name`,
`focus_by_selector`, `type_text`, `select_first_non_empty_option`,
`activate_by_role_or_text`, `press_key`, `assert_url_contains`.

When accessibility tree data is available, each step also records what the
focused element announces (computed role, name, and states) in an Announced
column, so reviewers can see the screen reader context per step.

These checks are produced when A11yway runs an explicit browser task
scenario, such as completing a scholarship application form using
keyboard-style steps. They provide evidence that one defined workflow did
or did not complete under specific conditions. They do not prove every user
can complete the task, and results still need human review.

| Issue type | Category | Default severity | What it detects | Why it matters | Current limitation |
| --- | --- | --- | --- | --- | --- |
| `task_step_blocked` | Task Execution | high | A required task step failed under keyboard-only interaction | The student workflow is likely blocked at that step | Deterministic scripts; a human may find a workaround |
| `task_control_not_keyboard_reachable` | Task Execution | high | A step only succeeded via programmatic focus, never via Tab | A real keyboard-only student would be stuck | The Tab search has a fixed press budget |
| `task_expected_content_missing` | Task Execution | medium | Expected page text (purpose or confirmation) was not visible | Students may not know where they are or whether the task worked | Compares normalized visible text only |

When a step's control sits beyond a confirmed focus loop, the task result
says `BLOCKED at step <id> (reason: keyboard_trap)` and a `keyboard_trap`
finding identifies the looping elements.

Task execution limitations:

- Steps prove keyboard operability of one scripted path, not every way a
  human might attempt the task.
- Step results are evidence for reviewers, not a certification of the
  whole workflow.
- It is not a full screen-reader simulation and does not replace testing
  with disabled users.

## Not Yet Covered

These areas are out of scope for the current prototype:

- Full screen-reader simulation (browser mode only estimates accessible names)
- Complex keyboard interaction beyond Tab traversal (arrow keys, shortcuts, modals)
- Authenticated portals and login-protected pages
- PDFs and other documents
- Mobile app accessibility
- Full WCAG certification: A11yway results are hints for human reviewers,
  not conformance claims

If a page passes every current check, that only means these specific checks
found nothing. Manual review is still required.

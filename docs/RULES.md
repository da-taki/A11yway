# A11yway Check Rules

A11yway is a prototype. The static checks below inspect HTML with the Python
standard library; the optional browser checks approximate keyboard navigation
in headless Chromium. Both are useful for finding common, high-impact barriers
on education pages, but they are not a complete accessibility audit and do not
replace human review or testing with disabled users.

Run `python -m a11yway.main --list-rules` for a quick listing, or
`python -m a11yway.main --rule missing_form_label` for details on one rule.
Run `python -m a11yway.main --wcag-coverage` for the WCAG 2.2 coverage map;
the full matrix lives in [WCAG_2_2_COVERAGE.md](WCAG_2_2_COVERAGE.md).

## Extended Module Evidence

The opt-in modules for screen-reader transcripts, mobile emulation, document
inspection, media review, workflows, forms, cognitive review, multilingual
content, components, and passive security add evidence channels and report
sections. They do not automatically increase WCAG coverage counts, and
heuristic findings default to `needs_review`. Passive security observations
use a separate namespace and are never merged with accessibility findings.

## Confidence Model

Every finding carries a backward-compatible confidence value and a richer
reviewer-facing `confidence_level` so reviewers know how much weight to give
it. Compatibility confidence remains:

- `confirmed`: deterministic observed blockage or state (for example, a
  scripted task step failed under keyboard-only interaction, or Tab was
  observed cycling in a trap). Even confirmed findings describe one run in
  one browser engine.
- `likely`: strong single-source evidence with known blind spots (for
  example, a form control with no label association in the parsed HTML).
- `needs_review`: heuristic evidence a human must judge (for example, a
  sensory-language pattern match or unresolved contrast over an image).
- `informational`: context for reviewers, not a suspected failure (for
  example, multiple h1 headings, which are valid HTML).

The post-collection validation pass also adds one of:

- `confirmed_by_multiple_engines`: the same root concern was found by more
  than one deterministic source, such as native checks and axe-core.
- `strong`: deterministic browser, accessibility-tree, or task evidence
  strongly supports the finding.
- `likely`: single-source deterministic evidence supports the finding.
- `needs_review`: the result needs human judgment before it is treated as a
  failure.
- `weak_heuristic`: useful review signal, but too weak to prioritize as a
  confirmed barrier by itself.
- `suppressed`: retained for audit transparency when a finding is
  intentionally downgraded or removed from priority views.

AI Scout suggestions never upgrade or validate deterministic findings.

Rules define a default confidence (shown by `--rule <issue_type>`); checks
can override it per finding when their evidence is weaker or stronger.
`--review-only-rules rule1,rule2` downgrades listed rules to `needs_review`
in a run's reports without disabling them, for rules whose reviewer
precision is poor.

`--calibrate-rules-from reviewed_report.json` derives the review-only list
from previous reviewed reports. A rule reliability profile records sample
size, precision, false-positive rate, unable-to-reproduce rate, and any
recommended `needs_review` confidence cap. The cap is advisory and visible in
precision reports; findings are not hidden.

For browser-backed dynamic checks, `--verify-runs N` repeats browser and
low-vision checks and adds reproducibility evidence. With three runs, a
dynamic finding seen in all three runs is `confirmed`, two of three is
`likely`, and primary-run-only evidence is `needs_review`.

## Finding Deduplication

Static analysis, the rendered-DOM re-check, browser interaction, the
accessibility tree, and axe-core can see the same barrier. Findings that
share a stable fingerprint (rule + normalized element identity) are merged
into one primary finding whose evidence lists every `evidence_sources`
entry and a `merged_finding_count`. Merged confidence is the strongest of
the sources, because independent detection strengthens the evidence.

After element-level merging, reports also calculate root issue clusters.
Each issue gets `occurrence_count`, `affected_page_count`, a
`component_signature` when available, and a `deduplication_fingerprint`.
Reports show both raw occurrences and unique root issues so repeated shared
components do not overwhelm the reviewer queue.

## WCAG 2.2 Mapping Language

Reports and rules deliberately say "related to WCAG 2.2 SC x.y.z", never
"WCAG failure confirmed" or "WCAG compliant". Coverage levels (`direct`,
`partial`, `supporting_evidence`, `axe_only`, `manual_only`, `unsupported`)
describe what the tool observes, not the conformance of a page. WCAG evidence
coverage is not the same as WCAG conformance coverage. See
[WCAG_2_2_COVERAGE.md](WCAG_2_2_COVERAGE.md).

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
| `image_empty_alt_suspicious` | Images | low | `alt=""` on images whose filename suggests informative content (chart, diagram, map, screenshot) | An informative image hidden behind an empty alt is lost to screen readers | Filename heuristic only; review-only evidence |
| `radio_group_missing_fieldset` | Forms | medium | Two or more same-name radios with no fieldset/legend or named radiogroup (WCAG 1.3.1) | The shared question is not announced with each option | Other grouping idioms (nearby heading, aria-labelledby containers) may be missed |
| `table_missing_headers` | Structure | medium | Tables with 2+ rows and 2+ columns of data cells, no `th`, no `headers` attrs, not `role="presentation"` (WCAG 1.3.1) | Data cells announce with no column/row context | Cannot always tell a data table from a layout table |
| `visual_required_not_programmatic` | Forms | medium | Labels showing `*` or "required" whose control lacks `required`/`aria-required` (WCAG 1.3.1, 3.3.2) | Screen reader users are not told the field is mandatory | Markers outside associated labels are not seen |
| `fake_heading` | Headings & Structure | low | Inline-styled large bold `div`/`span` text that may act as a heading (WCAG 1.3.1, review-only) | Styled pseudo-headings are invisible to heading navigation | Only inline styles are inspected; decorated non-heading text can match |
| `sensory_instruction` | Content | low | Instructions referencing only shape, color, position, or sound, e.g. "click the red button" (WCAG 1.3.3, review-only) | Users who cannot perceive the characteristic are lost | English keyword patterns; the sentence may also name the target |
| `missing_autocomplete` | Forms | medium | Common personal-data fields (name, email, tel, postal code, username, passwords, birthday) without an autocomplete token (WCAG 1.3.5) | Autofill and comprehension support break for people with memory or motor difficulties | Conservative token map; search boxes, one-time codes, and ambiguous fields are skipped |
| `no_bypass_mechanism` | Structure | medium | A navigation block of 5+ links with no skip link, no main landmark, and fewer than two headings (WCAG 2.4.1) | Keyboard users must re-traverse repeated links on every page | Static heuristic; pages with heading structure or a main landmark are never flagged |
| `label_in_name_mismatch` | Interactive Elements | medium | Visible text missing from an overriding aria-label after normalization (WCAG 2.5.3) | Speech-input users saying the visible label cannot activate the control | aria-labelledby chains are only partially resolved |
| `meaningful_sequence_reorder` | Structure | low | Inline CSS `order` or grid placement that may make visual order differ from DOM order (WCAG 1.3.2, review-only) | DOM/focus order can become confusing when order conveys meaning | Supporting evidence only; final visual/focus order needs browser review |
| `orientation_restriction` | Responsive Layout | medium | Rotate-device messages, orientation-lock code, or content hidden by orientation media queries (WCAG 1.3.4) | Users with mounted or fixed displays may be blocked | Requires restriction evidence; ordinary responsive CSS is ignored |
| `color_only_indicator` | Low Vision | low | Status/selection/error/required cues that appear color-only after common non-color exceptions are checked (WCAG 1.4.1) | Users who cannot distinguish color may miss the cue | Static styles only; computed visual review is needed |
| `autoplay_audio_no_control` | Media | medium | Native autoplay audio without controls (WCAG 1.4.2) | Audio can interfere with screen readers and concentration | Duration and custom controls require manual confirmation |
| `image_of_text` | Images | low | SVG text or image filenames suggesting embedded text (WCAG 1.4.5, review-only) | Image text may not adapt to user settings | No OCR; exceptions such as logos need review |
| `hover_focus_content` | Interaction | low | Custom hover/focus-revealed content evidence (WCAG 1.4.13) | Content can disappear or obscure essential content | Static behavior evidence only |
| `single_character_shortcut` | Keyboard Interaction | medium | Unmodified single-character keyboard listeners (WCAG 2.1.4) | Users can trigger shortcuts accidentally | Minified scripts and text-entry scoping need review |
| `timing_adjustable_missing` | Timing | medium | Meta refresh, timeout scripts, or countdown text without visible adjustment controls (WCAG 2.2.1) | Users may need more time | Exceptions and runtime behavior need review |
| `moving_content_no_pause` | Motion | medium | Auto-moving/updating content without visible pause/stop/hide controls (WCAG 2.2.2) | Movement can distract or block reading | Duration and process exceptions need review |
| `possible_flashing_content` | Motion | medium | Fast flash/blink CSS animation evidence (WCAG 2.3.1, review-only) | Flashing may trigger seizures | Does not measure luminance area or exact threshold |
| `interaction_motion_no_reduced_motion` | Motion | low | Interaction-triggered transform/animation without reduced-motion evidence (WCAG 2.3.3) | Motion can cause vestibular discomfort | CSS heuristic only |
| `pointer_gesture_no_alternative` | Pointer Interaction | medium | Swipe/pinch/path gesture event evidence without obvious simple alternatives (WCAG 2.5.1) | Complex gestures can be hard to perform | Must confirm the gesture is required |
| `pointer_down_activation` | Pointer Interaction | medium | Pointer-down activation without obvious up/cancel path (WCAG 2.5.2) | Users may be unable to abort accidental actions | Runtime behavior and undo need review |
| `dragging_no_alternative` | Pointer Interaction | medium | Drag/drop evidence without obvious non-drag alternative (WCAG 2.5.7) | Dragging can be inaccessible to limited dexterity users | Must confirm dragging is required |
| `focus_context_change` | Interaction | medium | Inline focus handlers that appear to navigate, submit, open UI, or move focus (WCAG 3.2.1) | Focus alone can unexpectedly change context | Inline handlers only |
| `input_context_change` | Interaction | medium | Inline input/change handlers that appear to navigate, submit, open UI, reload, or move focus (WCAG 3.2.2) | Input alone can unexpectedly change context | Inline handlers only |
| `error_not_identified` | Forms | medium | Static error messages not associated with controls by `aria-invalid` or `aria-describedby` (WCAG 3.3.1) | Users may not know which field failed | Runtime validation may differ |
| `error_suggestion_missing` | Forms | low | Static error messages without obvious correction guidance (WCAG 3.3.3, review-only) | Users need practical correction guidance where possible | Heuristic text check only |

## Current Static Checks

The analyzer currently runs these check groups over the raw HTML:

- **Form labels**: form controls must have a programmatic label. Hidden or
  non-user-facing controls (hidden attribute, `aria-hidden`, inline
  `display:none`, hidden ancestors) are ignored; a placeholder is treated
  as weak evidence, never as a valid label.
- **Interactive names**: links and buttons need clear accessible names.
  Generic phrases ("learn more") are not flagged when aria-label or
  aria-labelledby gives the link a specific computed name.
- **Image alt text**: images need useful alternatives. `alt=""` is
  respected as the standard decorative marker; an empty alt is flagged
  only when the image is the sole content of an unnamed link/button, or
  reported review-only when the filename suggests informative content.
- **Heading structure**: one h1, no skipped levels. Multiple h1 elements
  are informational review evidence, not a suspected failure. Skips are
  not flagged across independent regions (articles, labeled landmark
  regions), whose headings legitimately restart.
- **Page metadata**: page title and document language.
- **Media accessibility**: captions tracks for video, transcripts for audio.
- **Structure relationships (WCAG 1.3.1)**: radio groups without
  fieldset/legend, data tables without headers, visual-only required
  markers, and (review-only) styled fake headings.
- **Sensory instructions (WCAG 1.3.3)**: review-only detection of
  instructions that rely on shape, color, position, or sound.
- **Input purpose (WCAG 1.3.5)**: conservative autocomplete-token checks
  for common personal-data fields.
- **Bypass blocks (WCAG 2.4.1)**: substantial repeated navigation with no
  skip link, main landmark, or heading structure.
- **Label in name (WCAG 2.5.3)**: visible labels missing from overriding
  aria-labels.
- **Additional WCAG evidence (review-first)**: conservative static evidence
  for meaningful sequence, orientation restrictions, color-only cues,
  autoplay audio, images of text, hover/focus content, character shortcuts,
  timing, moving/flashing/interaction-triggered motion, pointer gestures,
  pointer cancellation, dragging, context changes on focus/input, and error
  identification/suggestions. These checks default to `needs_review`.

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
| `low_contrast_text` | Low Vision | medium/high | Rendered text samples whose computed color contrast is below a conservative threshold, with a fully resolved opaque background stack | Low-vision readers may not be able to read the content | Does not prove full color-contrast compliance; disabled controls are exempt and skipped |
| `contrast_unresolved_background` | Low Vision | medium | Text whose background stack contains an image, gradient, or transparency, so the ratio cannot be computed reliably (needs_review, WCAG 1.4.3) | The real contrast may be too low, but CSS colors alone cannot tell | Explicitly a review observation, never a suspected failure |
| `small_target_size` | Low Vision | medium | Interactive targets under 24x24 CSS px whose 24 px circle intersects another target (WCAG 2.5.8) | Small crowded targets are hard to hit for people with tremor or limited dexterity | Inline text links and spaced targets are excluded; equivalent-control and essential exceptions need human judgment |
| `focus_obscured` | Low Vision | high (fully covered) / medium (partial) | Focused controls covered by sticky/fixed overlays (headers, footers, banners, floating widgets), via bounding-box hit-testing (WCAG 2.4.11) | Keyboard users cannot see where focus is | One run; overlays that appear only after user actions are not seen |
| `text_spacing_content_loss` | Low Vision | high | Text that clips or controls that overlap only after applying the WCAG 1.4.12 reference overrides (line height 1.5, paragraph spacing 2em, letter spacing 0.12em, word spacing 0.16em), with before/after bounding boxes | People who need wider spacing lose the content entirely | One Chromium run; JavaScript reacting to layout changes is not modeled |
| `reflow_horizontal_scroll` | Low Vision | high when 400% overflow includes content loss / medium review-only otherwise | The document is wider than the zoomed viewport at 200% or 400% zoom-equivalent widths, above a 24 px and 5% viewport tolerance | Zoomed readers may need horizontal scrolling (WCAG 1.4.10 Reflow, reference 320 CSS px) | Bare document overflow is review evidence; high severity requires clipped content or overlapping interactive controls. Intentional scroll regions such as data tables are allowed by WCAG and need manual review |
| `reflow_clipped_content` | Low Vision | high | Text or controls whose bounding box sits beyond every reachable area at a zoom level | Clipped content disappears entirely for zoomed readers | Bounding boxes from one run; decorative cut-offs need manual confirmation |
| `reflow_overlap` | Low Vision | medium | Interactive elements whose bounding boxes collide at a zoom level | An overlapped control can be hidden or impossible to activate | Cannot judge visual intent; intentional stacking such as badges can be fine |
| `zoom_horizontal_overflow` | Low Vision | medium/high | (Legacy, no longer emitted) narrow-viewport overflow approximation | Kept so reports from older versions stay documented | Replaced by `reflow_horizontal_scroll` |
| `zoom_fixed_width_content` | Low Vision | medium | (Legacy, no longer emitted) wide or fixed-width rendered elements | Kept so reports from older versions stay documented | Replaced by the `reflow_*` checks |
| `focus_indicator_missing` | Low Vision | high | Focus stops whose focused and unfocused computed styles are identical, checked across outline, border, box-shadow, background, text decoration, transform, filter, `::before`/`::after` pseudo-elements, and the parent element | Keyboard users with low vision can lose track of focus | One Chromium run; canvas-drawn or animation-only indicators can still be missed. Falls back to the old single-snapshot heuristic (needs_review) when the comparison is unavailable |

Low-vision limitations:

- Rendered contrast checks sample visible text and computed colors; they do
  not replace design review. When the background stack cannot be resolved
  (images, gradients, transparency), the finding is downgraded to a
  `contrast_unresolved_background` needs_review observation.
- Zoom checks lay the page out at the CSS widths browser zoom produces
  (640 px at 200%, 320 px at 400% from a 1280 px base, matching the WCAG
  1.4.10 reference); they run in one Chromium engine and do not prove full
  reflow compliance. Content inside intentional horizontal-scroll regions
  (tables, `pre`/`code`, figures, containers with `overflow-x: auto|scroll`)
  is excluded, document-level overflow attributed entirely to such regions is
  not reported, and small overflow below 24 px or 5% of the viewport is
  ignored as noise.
- Focus indicator detection compares focused and unfocused computed styles;
  canvas-drawn or animation-only indicators may still be missed.
- Target size and focus-obscured measurements come from one run at default
  zoom; WCAG 2.5.8 exceptions beyond inline links and spacing need human
  judgment. Focus-obscured findings require at least 80% sampled coverage;
  lighter partial overlap is ignored.
- Text-spacing checks apply the WCAG 1.4.12 reference overrides once and
  compare before/after; only regressions caused by the overrides count.

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

- Full screen-reader simulation (browser mode reads Chromium's computed
  accessibility tree, which real screen readers may interpret differently)
- Free-form keyboard interaction beyond Tab traversal. Task execution can
  press arrow keys, Escape, Space, Home, End, and Enter through declared
  `press_key` steps, but there is no automatic widget-pattern exploration
- Hover/focus-triggered content behavior (WCAG 1.4.13)
- Character-key shortcut detection (WCAG 2.1.4)
- Before/after accessibility-tree state verification for custom widgets
  (stale `aria-expanded`/`aria-checked`, WCAG 4.1.2 state changes) and
  status message exposure (WCAG 4.1.3) beyond task-expected text
- Authenticated portals and login-protected pages, including accessible
  authentication checks (WCAG 3.3.8) against real login systems
- PDFs and other documents
- Mobile app accessibility
- Full WCAG certification: A11yway results are hints for human reviewers,
  not conformance claims

The full per-criterion status, including criteria covered only by the
optional axe-core scan and criteria that are manual-only, lives in
[WCAG_2_2_COVERAGE.md](WCAG_2_2_COVERAGE.md).

If a page passes every current check, that only means these specific checks
found nothing. Manual review is still required.

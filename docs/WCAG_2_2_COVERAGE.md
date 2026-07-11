# A11yway WCAG 2.2 Coverage

This matrix maps every WCAG 2.2 Success Criterion to the A11yway
rules that produce related evidence. It is generated from
`a11yway/core/wcag_coverage.py` (regenerate with
`python -m a11yway.main --wcag-coverage-markdown docs/WCAG_2_2_COVERAGE.md`).

**WCAG evidence coverage is not the same as WCAG conformance coverage.**
A criterion marked `direct` is
only checked within the narrow scope its rules document. Every audit
still requires manual review, and many criteria can only be tested
by a human.

Extended modules such as screen-reader transcripts, mobile emulation,
document inspection, media review, workflows, forms, cognitive review,
multilingual review, components, and passive security add evidence and
report sections. They do not change this generated WCAG coverage count
unless their rules are explicitly mapped in `wcag_coverage.py`.

## Summary

- Total WCAG 2.2 Success Criteria: 86
- Direct native coverage: 1
- Partial native coverage: 21
- Supporting evidence only: 23
- Covered only through the optional axe-core scan: 0
- Manual review only: 41
- Unsupported: 0

Each criterion is counted once at its strongest native coverage
level, even when several rules map to it.

## Coverage levels

- `direct`: a rule deterministically observes the specific failure,
  within its documented scope.
- `partial`: a rule observes a meaningful slice of the criterion.
- `supporting_evidence`: rules produce evidence a reviewer can use,
  but do not test the criterion themselves.
- `manual_only`: no A11yway rule produces evidence.

## Matrix

| WCAG Success Criterion | Name | Level | Native coverage | Axe-only coverage | Coverage type | A11yway rules | Evidence mode | Limitations | Manual testing needed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1.1.1 | Non-text Content | A | partial | no | partial | `image_empty_alt_suspicious`, `missing_image_alt` | static | Cannot judge whether existing alt text is useful; decorative detection is heuristic.; Filename-based heuristic; an image named chart.png can still be decorative. | Check whether the empty-alt image actually carries information a text alternative should convey.; Decide whether the image is informative and whether the alternative conveys the same information. |
| 1.2.1 | Audio-only and Video-only (Prerecorded) | A | supporting_evidence | no | supporting_evidence | `missing_audio_transcript` | static | The transcript search is a rough text heuristic; a transcript may exist on a linked page. | Check whether a transcript is available and easy to find. |
| 1.2.2 | Captions (Prerecorded) | A | partial | no | partial | `missing_video_captions` | static | Only sees <track> elements; player-level, platform, or burned-in captions are invisible. | Play the video and check for captions from the player or platform. |
| 1.2.3 | Audio Description or Media Alternative (Prerecorded) | A | none | no | manual_only | none | manual | No automated A11yway evidence for this Success Criterion. | Manual WCAG testing is required. |
| 1.2.4 | Captions (Live) | AA | none | no | manual_only | none | manual | No automated A11yway evidence for this Success Criterion. | Manual WCAG testing is required. |
| 1.2.5 | Audio Description (Prerecorded) | AA | none | no | manual_only | none | manual | No automated A11yway evidence for this Success Criterion. | Manual WCAG testing is required. |
| 1.2.6 | Sign Language (Prerecorded) | AAA | none | no | manual_only | none | manual | No automated A11yway evidence for this Success Criterion. | Manual WCAG testing is required. |
| 1.2.7 | Extended Audio Description (Prerecorded) | AAA | none | no | manual_only | none | manual | No automated A11yway evidence for this Success Criterion. | Manual WCAG testing is required. |
| 1.2.8 | Media Alternative (Prerecorded) | AAA | none | no | manual_only | none | manual | No automated A11yway evidence for this Success Criterion. | Manual WCAG testing is required. |
| 1.2.9 | Audio-only (Live) | AAA | none | no | manual_only | none | manual | No automated A11yway evidence for this Success Criterion. | Manual WCAG testing is required. |
| 1.3.1 | Info and Relationships | A | partial | no | partial | `fake_heading`, `missing_form_label`, `missing_h1`, `multiple_h1`, `radio_group_missing_fieldset`, `skipped_heading_level`, `table_missing_headers`, `visual_required_not_programmatic` | static | A table can be a layout table; the check skips role=presentation and single-row/column tables but cannot always tell intent.; Detects * or 'required' in an associated label without required/aria-required on the control.; Inline-style heuristic (large bold text in div/span); many false positives are possible in decorated content, so this is review evidence only.; Multiple h1 elements are valid HTML and often intentional; this is review evidence only.; Only checks fieldset/legend and role=radiogroup with an accessible name; other grouping idioms need review.; Only detects missing label association, not other relationship failures.; Skipped levels are not automatically WCAG failures; independent regions and embedded components can legitimately restart levels.; WCAG does not require an h1; this is structural review evidence. | Check whether a visually implied label exists that is not programmatically connected.; Confirm the field is actually mandatory and expose that state programmatically.; Confirm the group question is announced when a screen reader reaches each radio button.; Decide whether the table presents data; if so, header cells must be programmatically associated.; Judge whether multiple h1 headings make the main topic unclear when navigating by headings.; Judge whether the page structure is understandable without a main heading.; Judge whether the styled text functions as a section heading; if so, use a real heading element.; Read the heading outline and judge whether relationships are conveyed. |
| 1.3.2 | Meaningful Sequence | A | supporting_evidence | no | supporting_evidence | `meaningful_sequence_reorder` | static | Detects inline CSS order/grid placement that can desynchronize visual and DOM order, but cannot determine intended meaning. | Compare DOM order, visual order, and keyboard/focus order in the rendered page. |
| 1.3.3 | Sensory Characteristics | A | supporting_evidence | no | supporting_evidence | `sensory_instruction` | static | Keyword pattern heuristic; the surrounding text may also give non-sensory identification. | Read the instruction in context and check whether it also identifies the target by name or label. |
| 1.3.4 | Orientation | AA | partial | no | partial | `orientation_restriction` | static | Requires strong static restriction evidence such as rotate messaging, orientation-lock code, or orientation-specific hidden content. | Test the page in portrait and landscape and confirm content/functionality is restricted without an essential reason. |
| 1.3.5 | Identify Input Purpose | AA | partial | no | partial | `missing_autocomplete` | static | Conservative token map for common personal-data fields; custom or ambiguous fields are skipped, and search/one-time-code fields are excluded. | Confirm the field collects information about the user and add the matching autocomplete token. |
| 1.3.6 | Identify Purpose | AAA | none | no | manual_only | none | manual | No automated A11yway evidence for this Success Criterion. | Manual WCAG testing is required. |
| 1.4.1 | Use of Color | A | supporting_evidence | no | supporting_evidence | `color_only_indicator` | static | Looks for status/selection classes or inline color cues while excluding common non-color alternatives; final computed presentation is not measured. | Confirm color is the only way the information is conveyed. |
| 1.4.2 | Audio Control | A | partial | no | partial | `autoplay_audio_no_control` | static | Detects native autoplay audio without controls; duration and custom controls require rendered-page review. | Confirm the audio starts automatically, lasts more than about three seconds, and lacks pause/stop or volume controls. |
| 1.4.3 | Contrast (Minimum) | AA | partial | no | partial | `contrast_unresolved_background`, `low_contrast_text` | low_vision | Computed-color sampling; gradients, images, and overlays force a needs_review confidence instead.; The background stack includes an image, gradient, or transparency, so the ratio cannot be computed reliably. | Measure contrast against the actual rendered background (eyedropper or contrast tool).; Verify the sampled colors match what users see, then measure contrast precisely. |
| 1.4.4 | Resize Text | AA | supporting_evidence | no | supporting_evidence | `reflow_clipped_content` | low_vision | Viewport-based emulation approximates but does not equal text-only scaling to 200%. | Test with browser text-size settings at 200%. |
| 1.4.5 | Images of Text | AA | supporting_evidence | no | supporting_evidence | `image_of_text` | static | Uses SVG text or image filename evidence; it does not perform OCR or judge exceptions such as logos. | Inspect whether the graphic contains text that should be real text, or whether an exception applies. |
| 1.4.6 | Contrast (Enhanced) | AAA | none | no | manual_only | none | manual | No automated A11yway evidence for this Success Criterion. | Manual WCAG testing is required. |
| 1.4.7 | Low or No Background Audio | AAA | none | no | manual_only | none | manual | No automated A11yway evidence for this Success Criterion. | Manual WCAG testing is required. |
| 1.4.8 | Visual Presentation | AAA | none | no | manual_only | none | manual | No automated A11yway evidence for this Success Criterion. | Manual WCAG testing is required. |
| 1.4.9 | Images of Text (No Exception) | AAA | none | no | manual_only | none | manual | No automated A11yway evidence for this Success Criterion. | Manual WCAG testing is required. |
| 1.4.10 | Reflow | AA | partial | no | partial | `reflow_clipped_content`, `reflow_horizontal_scroll`, `reflow_overlap`, `zoom_fixed_width_content`, `zoom_horizontal_overflow` | low_vision | Bounding boxes from one run; animation and lazy layout can shift results.; Bounding-box intersection cannot judge visual intent; intentional stacking can be fine.; Legacy check kept for old reports; replaced by reflow_horizontal_scroll.; Legacy check kept for old reports; replaced by the reflow_* checks.; Zoom is emulated through equivalent viewport widths in one Chromium run; intentional scroll regions (data tables, maps) are allowed by WCAG. | Confirm the clipped element holds real content.; Confirm the overflow is not an allowed two-dimensional content region.; Confirm the overlap visually at high zoom.; Re-audit with a current A11yway version. |
| 1.4.11 | Non-text Contrast | AA | none | no | manual_only | none | manual | No automated A11yway evidence for this Success Criterion. | Manual WCAG testing is required. |
| 1.4.12 | Text Spacing | AA | partial | no | partial | `text_spacing_content_loss` | low_vision | Applies the WCAG reference text-spacing overrides and compares clipping/overlap before and after; loss caused by JavaScript reacting to resize is not modeled. | Apply a text-spacing bookmarklet and confirm the content or control is genuinely lost. |
| 1.4.13 | Content on Hover or Focus | AA | supporting_evidence | no | supporting_evidence | `hover_focus_content` | static | Static event/CSS evidence cannot verify dismissible, hoverable, or persistent behavior. | Interact with the component by keyboard and pointer to test dismissibility, hoverability, persistence, and obstruction. |
| 2.1.1 | Keyboard | A | partial | no | partial | `browser_focus_not_moving`, `browser_no_focusable_elements`, `task_control_not_keyboard_reachable`, `task_step_blocked` | browser_interaction, task_execution | Counts common focusable selectors in one Chromium run.; Headless Tab behavior can differ from a desktop browser session.; Proves one scripted path failed under keyboard-only interaction, not that every path fails.; The Tab search has a fixed press budget and may miss controls on very long pages. | Press Tab in a visible browser and confirm focus never enters the page.; Repeat the step manually with a keyboard.; Tab through the page manually and confirm the control is unreachable.; Try the page with a real keyboard. |
| 2.1.2 | No Keyboard Trap | A | partial | no | partial | `browser_repeated_focus`, `keyboard_trap` | browser_interaction | Observed Tab-only behavior; a documented escape mechanism (Escape, arrow keys) would not be seen.; Repeated focus suggests but does not prove a trap. | Confirm by hand whether standard keys escape the widget.; Confirm the loop by hand and check for documented escape mechanisms. |
| 2.1.3 | Keyboard (No Exception) | AAA | none | no | manual_only | none | manual | No automated A11yway evidence for this Success Criterion. | Manual WCAG testing is required. |
| 2.1.4 | Character Key Shortcuts | A | supporting_evidence | no | supporting_evidence | `single_character_shortcut` | static | Script heuristic for unmodified single-character key listeners; minified code and typing-field exceptions require manual testing. | Verify whether the shortcut triggers without modifiers and whether it can be disabled, remapped, or scoped away from text entry. |
| 2.2.1 | Timing Adjustable | A | supporting_evidence | no | supporting_evidence | `timing_adjustable_missing` | static | Detects meta refresh, timeout scripts, and countdown language, but not all timing exceptions or custom adjustment controls. | Confirm the time limit, whether users can extend/disable/adjust it, and whether an exception applies. |
| 2.2.2 | Pause, Stop, Hide | A | supporting_evidence | no | supporting_evidence | `moving_content_no_pause` | static | Detects common auto-moving/update patterns and visible pause/stop/hide controls; duration and process exceptions require review. | Confirm movement lasts more than five seconds and no pause, stop, hide, or update-frequency control exists. |
| 2.2.3 | No Timing | AAA | none | no | manual_only | none | manual | No automated A11yway evidence for this Success Criterion. | Manual WCAG testing is required. |
| 2.2.4 | Interruptions | AAA | none | no | manual_only | none | manual | No automated A11yway evidence for this Success Criterion. | Manual WCAG testing is required. |
| 2.2.5 | Re-authenticating | AAA | none | no | manual_only | none | manual | No automated A11yway evidence for this Success Criterion. | Manual WCAG testing is required. |
| 2.2.6 | Timeouts | AAA | none | no | manual_only | none | manual | No automated A11yway evidence for this Success Criterion. | Manual WCAG testing is required. |
| 2.3.1 | Three Flashes or Below Threshold | A | supporting_evidence | no | supporting_evidence | `possible_flashing_content` | static | CSS keyframe/duration evidence suggests rapid flashing but does not measure luminance area or precise flash thresholds. | Use a specialized flashing-threshold tool or visual review to confirm risk. |
| 2.3.2 | Three Flashes | AAA | none | no | manual_only | none | manual | No automated A11yway evidence for this Success Criterion. | Manual WCAG testing is required. |
| 2.3.3 | Animation from Interactions | AAA | supporting_evidence | no | supporting_evidence | `interaction_motion_no_reduced_motion` | static | Detects interaction-triggered CSS motion without prefers-reduced-motion evidence; it cannot judge whether motion is essential. | Trigger the interaction and confirm non-essential motion can be disabled or respects reduced-motion preferences. |
| 2.4.1 | Bypass Blocks | A | partial | no | partial | `no_bypass_mechanism` | static | Fires only for pages with a substantial repeated navigation block and no skip link, main landmark, or heading-based structure; other bypass mechanisms may exist. | Check whether keyboard users can reach the main content without tabbing through all repeated blocks. |
| 2.4.2 | Page Titled | A | partial | no | partial | `missing_page_title` | static | Titles set by JavaScript are only visible in browser mode. | Confirm the rendered page has no usable title. |
| 2.4.3 | Focus Order | A | supporting_evidence | no | supporting_evidence | `browser_focus_on_hidden_element`, `focus_lost`, `task_control_not_keyboard_reachable` | browser_interaction, task_execution | One headless run; focus handling can differ with browser UI present.; Reachability failure often indicates focus-order problems too.; Visibility is estimated from size and CSS; skip links that appear on focus are a valid pattern. | Check whether the element becomes visible when focused.; Reproduce by hand in a visible browser.; Review the Tab order around the unreachable control. |
| 2.4.4 | Link Purpose (In Context) | A | partial | no | partial | `generic_link_text`, `missing_link_name` | static | Generic visible text can still be acceptable when programmatic context (aria-labelledby, list context) disambiguates it.; Only detects empty names, not misleading ones. | Confirm the link announces nothing useful in a screen reader.; Listen to the link in a links list; judge whether its purpose is clear in context. |
| 2.4.5 | Multiple Ways | AA | none | no | manual_only | none | manual | No automated A11yway evidence for this Success Criterion. | Manual WCAG testing is required. |
| 2.4.6 | Headings and Labels | AA | supporting_evidence | no | supporting_evidence | `missing_h1` | static | Absence of an h1 is not itself a 2.4.6 failure. | Judge whether existing headings describe their sections. |
| 2.4.7 | Focus Visible | AA | partial | no | partial | `browser_focus_on_hidden_element`, `focus_indicator_missing` | browser_interaction, low_vision | An invisible focused element usually has no visible indicator, but the pattern needs human judgment.; Compares focused and unfocused computed styles (outline, box-shadow, border, background, text-decoration, transform, pseudo-elements, parent styles) in one Chromium run; animated or canvas-drawn indicators can still be missed. | Tab through the page and look for any visible focus indication.; Tab to the element and look for any visible focus location. |
| 2.4.8 | Location | AAA | none | no | manual_only | none | manual | No automated A11yway evidence for this Success Criterion. | Manual WCAG testing is required. |
| 2.4.9 | Link Purpose (Link Only) | AAA | none | no | manual_only | none | manual | No automated A11yway evidence for this Success Criterion. | Manual WCAG testing is required. |
| 2.4.10 | Section Headings | AAA | none | no | manual_only | none | manual | No automated A11yway evidence for this Success Criterion. | Manual WCAG testing is required. |
| 2.4.11 | Focus Not Obscured (Minimum) | AA | partial | no | partial | `focus_obscured` | low_vision | Bounding-box and hit-test sampling against sticky/fixed overlays in one run; overlays that appear only after user actions are not seen. | Tab to the control and confirm whether it is visible behind sticky headers, footers, banners, or widgets. |
| 2.4.12 | Focus Not Obscured (Enhanced) | AAA | none | no | manual_only | none | manual | No automated A11yway evidence for this Success Criterion. | Manual WCAG testing is required. |
| 2.4.13 | Focus Appearance | AAA | none | no | manual_only | none | manual | No automated A11yway evidence for this Success Criterion. | Manual WCAG testing is required. |
| 2.5.1 | Pointer Gestures | A | supporting_evidence | no | supporting_evidence | `pointer_gesture_no_alternative` | static | Event-name heuristic for swipe, pinch, path, or pointer-move interactions; visible alternatives are inferred from control text. | Confirm the gesture is required and whether a simple pointer alternative exists. |
| 2.5.2 | Pointer Cancellation | A | supporting_evidence | no | supporting_evidence | `pointer_down_activation` | static | Requires down-event evidence and no obvious up/cancel handler, but cannot verify final activation behavior. | Test whether activation occurs on down, whether moving away cancels, and whether undo exists. |
| 2.5.3 | Label in Name | A | partial | no | partial | `label_in_name_mismatch` | static | Normalized substring comparison of visible text vs aria-label; icon-only and very short labels are skipped. | Say the visible label to a speech-input tool and check whether the control activates. |
| 2.5.4 | Motion Actuation | A | none | no | manual_only | none | manual | No automated A11yway evidence for this Success Criterion. | Manual WCAG testing is required. |
| 2.5.5 | Target Size (Enhanced) | AAA | supporting_evidence | no | supporting_evidence | `small_target_size` | low_vision | 2.5.5 (AAA) uses a 44px target; measurements are evidence only. | Apply the 44px AAA threshold manually if targeting AAA. |
| 2.5.6 | Concurrent Input Mechanisms | AAA | none | no | manual_only | none | manual | No automated A11yway evidence for this Success Criterion. | Manual WCAG testing is required. |
| 2.5.7 | Dragging Movements | AA | supporting_evidence | no | supporting_evidence | `dragging_no_alternative` | static | Detects draggable markup or drag/drop script names and common non-drag alternatives; cannot prove dragging is required. | Confirm the operation can be completed without dragging. |
| 2.5.8 | Target Size (Minimum) | AA | partial | no | partial | `small_target_size` | low_vision | Measured in one Chromium run at default zoom; inline text links and targets with sufficient surrounding spacing are excluded, but equivalent-control and essential exceptions need human judgment. | Check the 2.5.8 exceptions: equivalent target, inline, user-agent default, essential. |
| 3.1.1 | Language of Page | A | direct | no | direct | `missing_html_lang`, `missing_lang_indic` | static | Direct for static HTML; a lang attribute added by JavaScript would be missed in static mode.; Unicode-range script detection; languages sharing a script cannot be told apart. | Confirm the actual language and add the right lang value.; Confirm the rendered html element still has no lang attribute. |
| 3.1.2 | Language of Parts | AA | partial | no | partial | `lang_mismatch`, `missing_lang_indic`, `mixed_script_element` | static | Conservative heuristic; may flag intentional bilingual lines.; Fires only when the script itself contradicts the declaration.; Same script heuristic; transliterated text is invisible. | Confirm each language passage carries a matching lang attribute.; Confirm the element's language and correct the lang attribute.; Listen with a real screen reader to confirm the impact. |
| 3.1.3 | Unusual Words | AAA | none | no | manual_only | none | manual | No automated A11yway evidence for this Success Criterion. | Manual WCAG testing is required. |
| 3.1.4 | Abbreviations | AAA | none | no | manual_only | none | manual | No automated A11yway evidence for this Success Criterion. | Manual WCAG testing is required. |
| 3.1.5 | Reading Level | AAA | none | no | manual_only | none | manual | No automated A11yway evidence for this Success Criterion. | Manual WCAG testing is required. |
| 3.1.6 | Pronunciation | AAA | none | no | manual_only | none | manual | No automated A11yway evidence for this Success Criterion. | Manual WCAG testing is required. |
| 3.2.1 | On Focus | A | supporting_evidence | no | supporting_evidence | `focus_context_change` | static | Inline onfocus-handler evidence only; external scripts and actual browser state changes require interaction testing. | Focus the control without activating it and confirm whether navigation, submission, modal opening, or focus relocation occurs. |
| 3.2.2 | On Input | A | supporting_evidence | no | supporting_evidence | `input_context_change` | static | Inline input/change-handler evidence only; external scripts and warning mechanisms may be missed. | Change the control value with synthetic local data and confirm whether an unexpected context change occurs. |
| 3.2.3 | Consistent Navigation | AA | none | no | manual_only | none | manual | No automated A11yway evidence for this Success Criterion. | Manual WCAG testing is required. |
| 3.2.4 | Consistent Identification | AA | none | no | manual_only | none | manual | No automated A11yway evidence for this Success Criterion. | Manual WCAG testing is required. |
| 3.2.5 | Change on Request | AAA | none | no | manual_only | none | manual | No automated A11yway evidence for this Success Criterion. | Manual WCAG testing is required. |
| 3.2.6 | Consistent Help | A | none | no | manual_only | none | manual | No automated A11yway evidence for this Success Criterion. | Manual WCAG testing is required. |
| 3.3.1 | Error Identification | A | supporting_evidence | no | supporting_evidence | `error_not_identified` | static | Static error markup is inspected for aria-invalid/aria-describedby association; runtime validation may be different. | Submit local or permitted test data and confirm errors identify affected fields in text and accessibility APIs. |
| 3.3.2 | Labels or Instructions | A | partial | no | partial | `missing_form_label`, `visual_required_not_programmatic` | static | Static HTML only; labels added by JavaScript are seen only in browser mode.; The visible instruction exists; only the programmatic exposure is missing. | Check what a screen reader announces for the field's required state.; Confirm the field has no visible or programmatic label in the final rendered page. |
| 3.3.3 | Error Suggestion | AA | supporting_evidence | no | supporting_evidence | `error_suggestion_missing` | static | Checks static error text for common correction guidance words; it cannot judge all useful suggestions. | Confirm a practical correction suggestion is provided when the correction is known. |
| 3.3.4 | Error Prevention (Legal, Financial, Data) | AA | none | no | manual_only | none | manual | No automated A11yway evidence for this Success Criterion. | Manual WCAG testing is required. |
| 3.3.5 | Help | AAA | none | no | manual_only | none | manual | No automated A11yway evidence for this Success Criterion. | Manual WCAG testing is required. |
| 3.3.6 | Error Prevention (All) | AAA | none | no | manual_only | none | manual | No automated A11yway evidence for this Success Criterion. | Manual WCAG testing is required. |
| 3.3.7 | Redundant Entry | A | none | no | manual_only | none | manual | No automated A11yway evidence for this Success Criterion. | Manual WCAG testing is required. |
| 3.3.8 | Accessible Authentication (Minimum) | AA | none | no | manual_only | none | manual | No automated A11yway evidence for this Success Criterion. | Manual WCAG testing is required. |
| 3.3.9 | Accessible Authentication (Enhanced) | AAA | none | no | manual_only | none | manual | No automated A11yway evidence for this Success Criterion. | Manual WCAG testing is required. |
| 4.1.2 | Name, Role, Value | A | partial | no | partial | `browser_focused_control_missing_name`, `missing_button_name`, `missing_form_label`, `missing_link_name`, `unnamed_focus_stop` | accessibility_tree, browser_interaction, static | A missing label usually means a missing accessible name, but the browser may compute one from other sources.; Chromium's computed tree in one run; real screen readers apply their own rules.; Heuristic name estimate; only used when accessibility tree data is unavailable.; Static heuristic on source HTML.; Static heuristic; icon fonts and JavaScript-injected names are invisible statically. | Confirm the computed accessible name is empty in the rendered page.; Confirm with NVDA, JAWS, or VoiceOver what is actually announced.; Inspect the computed accessible name in browser dev tools. |
| 4.1.3 | Status Messages | AA | supporting_evidence | no | supporting_evidence | `task_expected_content_missing` | task_execution | Compares normalized visible text only; the status may exist but use different wording. | Check whether the outcome of the action is communicated at all, and whether it is exposed to assistive technology. |

## Manual verification guidance

For every criterion with native or axe coverage, the related
rules carry per-mapping manual_check guidance available through
`python -m a11yway.main --rule <issue_type>` and in report
issue entries. Criteria marked manual_only need a human test
plan; the W3C's *Understanding WCAG 2.2* documents describe
procedures for each.

## Axe-core note

The optional `--axe` scan maps to WCAG through axe-core's own
rule tags. Axe coverage of a criterion is itself partial;
'covered by axe-core' means axe has at least one automated rule
related to the criterion, not that the criterion is fully tested.

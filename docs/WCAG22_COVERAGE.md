# A11yway WCAG 2.2 A/AA Coverage Inventory

This document is generated from `a11yway/data/wcag22_coverage.json`.

This figure is not WCAG conformance, certification, scoring, or a legal claim.

## Summary

- Total WCAG 2.2 Level A and AA Success Criteria: 55
- Automated: 1
- Partially automated: 45
- Manual only: 4
- Unsupported: 5
- Automated or partially automated rule coverage: 83.6%

## Coverage Statuses

- `automated`: deterministic A11yway rule evidence for a narrow criterion slice with fixtures and actionable output.
- `partially_automated`: A11yway or axe-core evidence helps evaluate the criterion but does not fully decide it.
- `manual_only`: the criterion fundamentally needs human judgment or a permitted workflow.
- `unsupported`: A11yway does not currently implement criterion-specific evidence.

## Matrix

| Criterion | Short name | Level | Status | Rules | Engines | Evidence | Human review required | Limitations |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1.1.1 | Non-text Content | A | partially_automated | `image_empty_alt_suspicious`, `missing_image_alt` | static | source markup and parsed element evidence | yes | Cannot judge whether existing alt text is useful; decorative detection is heuristic., Filename-based heuristic; an image named chart.png can still be decorative. |
| 1.2.1 | Audio-only and Video-only (Prerecorded) | A | partially_automated | `missing_audio_transcript` | static | source markup and parsed element evidence | yes | The transcript search is a rough text heuristic; a transcript may exist on a linked page. |
| 1.2.2 | Captions (Prerecorded) | A | partially_automated | `missing_video_captions` | static | source markup and parsed element evidence | yes | Only sees <track> elements; player-level, platform, or burned-in captions are invisible. |
| 1.2.3 | Audio Description or Media Alternative (Prerecorded) | A | manual_only | none | none | none | yes | No implemented A11yway rule currently produces criterion-specific evidence. |
| 1.2.4 | Captions (Live) | AA | unsupported | none | none | none | yes | No implemented A11yway rule currently produces criterion-specific evidence. |
| 1.2.5 | Audio Description (Prerecorded) | AA | unsupported | none | none | none | yes | No implemented A11yway rule currently produces criterion-specific evidence. |
| 1.3.1 | Info and Relationships | A | partially_automated | `fake_heading`, `missing_form_label`, `missing_h1`, `multiple_h1`, `radio_group_missing_fieldset`, `skipped_heading_level`, `table_missing_headers`, `visual_required_not_programmatic` | static | source markup and parsed element evidence | yes | A table can be a layout table; the check skips role=presentation and single-row/column tables but cannot always tell intent., Detects * or 'required' in an associated label without required/aria-required on the control., Inline-style heuristic (large bold text in div/span); many false positives are possible in decorated content, so this is review evidence only., Multiple h1 elements are valid HTML and often intentional; this is review evidence only., Only checks fieldset/legend and role=radiogroup with an accessible name; other grouping idioms need review., Only detects missing label association, not other relationship failures., Skipped levels are not automatically WCAG failures; independent regions and embedded components can legitimately restart levels., WCAG does not require an h1; this is structural review evidence. |
| 1.3.2 | Meaningful Sequence | A | partially_automated | `meaningful_sequence_reorder` | static | source markup and parsed element evidence | yes | Detects inline CSS order/grid placement that can desynchronize visual and DOM order, but cannot determine intended meaning. |
| 1.3.3 | Sensory Characteristics | A | partially_automated | `sensory_instruction` | static | source markup and parsed element evidence | yes | Keyword pattern heuristic; the surrounding text may also give non-sensory identification. |
| 1.3.4 | Orientation | AA | partially_automated | `orientation_restriction` | static | source markup and parsed element evidence | yes | Requires strong static restriction evidence such as rotate messaging, orientation-lock code, or orientation-specific hidden content. |
| 1.3.5 | Identify Input Purpose | AA | partially_automated | `autocomplete_unsupported_control`, `contradictory_autocomplete`, `invalid_autocomplete_token`, `missing_autocomplete` | static | source markup and parsed element evidence | yes | Compares inferred purpose with the token; ambiguous labels and localized forms can require review., Conservative token map for common personal-data fields; custom or ambiguous fields are skipped, and search/one-time-code fields are excluded., Flags autocomplete metadata on controls that normally do not collect reusable personal data., Validates known autocomplete detail tokens but cannot prove the field purpose. |
| 1.4.1 | Use of Color | A | partially_automated | `color_only_indicator` | static | source markup and parsed element evidence | yes | Looks for status/selection classes or inline color cues while excluding common non-color alternatives; final computed presentation is not measured. |
| 1.4.2 | Audio Control | A | partially_automated | `autoplay_audio_no_control` | static | source markup and parsed element evidence | yes | Detects native autoplay audio without controls; duration and custom controls require rendered-page review. |
| 1.4.3 | Contrast (Minimum) | AA | partially_automated | `contrast_unresolved_background`, `low_contrast_text` | low_vision | rendered geometry and computed style evidence | yes | Computed-color sampling; gradients, images, and overlays force a needs_review confidence instead., The background stack includes an image, gradient, or transparency, so the ratio cannot be computed reliably. |
| 1.4.4 | Resize Text | AA | partially_automated | `reflow_clipped_content` | low_vision | rendered geometry and computed style evidence | yes | Viewport-based emulation approximates but does not equal text-only scaling to 200%. |
| 1.4.5 | Images of Text | AA | partially_automated | `image_of_text` | static | source markup and parsed element evidence | yes | Uses SVG text or image filename evidence; it does not perform OCR or judge exceptions such as logos. |
| 1.4.10 | Reflow | AA | partially_automated | `reflow_clipped_content`, `reflow_horizontal_scroll`, `reflow_overlap`, `zoom_fixed_width_content`, `zoom_horizontal_overflow` | low_vision | rendered geometry and computed style evidence | yes | Bounding boxes from one run; animation and lazy layout can shift results., Bounding-box intersection cannot judge visual intent; intentional stacking can be fine., Legacy check kept for old reports; replaced by reflow_horizontal_scroll., Legacy check kept for old reports; replaced by the reflow_* checks., Zoom is emulated through equivalent viewport widths in one Chromium run; intentional scroll regions (data tables, maps) are allowed by WCAG. |
| 1.4.11 | Non-text Contrast | AA | manual_only | none | none | none | yes | No implemented A11yway rule currently produces criterion-specific evidence. |
| 1.4.12 | Text Spacing | AA | partially_automated | `text_spacing_content_loss` | low_vision | rendered geometry and computed style evidence | yes | Applies the WCAG reference text-spacing overrides and compares clipping/overlap before and after; loss caused by JavaScript reacting to resize is not modeled. |
| 1.4.13 | Content on Hover or Focus | AA | partially_automated | `hover_focus_content` | static | source markup and parsed element evidence | yes | Static event/CSS evidence cannot verify dismissible, hoverable, or persistent behavior. |
| 2.1.1 | Keyboard | A | partially_automated | `browser_focus_not_moving`, `browser_no_focusable_elements`, `task_control_not_keyboard_reachable`, `task_step_blocked` | browser_interaction, task_execution | keyboard traversal and browser interaction evidence, safe keyboard workflow evidence | yes | Counts common focusable selectors in one Chromium run., Headless Tab behavior can differ from a desktop browser session., Proves one scripted path failed under keyboard-only interaction, not that every path fails., The Tab search has a fixed press budget and may miss controls on very long pages. |
| 2.1.2 | No Keyboard Trap | A | partially_automated | `browser_repeated_focus`, `keyboard_trap` | browser_interaction | keyboard traversal and browser interaction evidence | yes | Observed Tab-only behavior; a documented escape mechanism (Escape, arrow keys) would not be seen., Repeated focus suggests but does not prove a trap. |
| 2.1.4 | Character Key Shortcuts | A | partially_automated | `single_character_shortcut` | static | source markup and parsed element evidence | yes | Script heuristic for unmodified single-character key listeners; minified code and typing-field exceptions require manual testing. |
| 2.2.1 | Timing Adjustable | A | partially_automated | `timing_adjustable_missing` | static | source markup and parsed element evidence | yes | Detects meta refresh, timeout scripts, and countdown language, but not all timing exceptions or custom adjustment controls. |
| 2.2.2 | Pause, Stop, Hide | A | partially_automated | `moving_content_no_pause` | static | source markup and parsed element evidence | yes | Detects common auto-moving/update patterns and visible pause/stop/hide controls; duration and process exceptions require review. |
| 2.3.1 | Three Flashes or Below Threshold | A | partially_automated | `possible_flashing_content` | static | source markup and parsed element evidence | yes | CSS keyframe/duration evidence suggests rapid flashing but does not measure luminance area or precise flash thresholds. |
| 2.4.1 | Bypass Blocks | A | partially_automated | `no_bypass_mechanism` | static | source markup and parsed element evidence | yes | Fires only for pages with a substantial repeated navigation block and no skip link, main landmark, or heading-based structure; other bypass mechanisms may exist. |
| 2.4.2 | Page Titled | A | partially_automated | `missing_page_title` | static | source markup and parsed element evidence | yes | Titles set by JavaScript are only visible in browser mode. |
| 2.4.3 | Focus Order | A | partially_automated | `browser_focus_on_hidden_element`, `focus_lost`, `task_control_not_keyboard_reachable` | browser_interaction, task_execution | keyboard traversal and browser interaction evidence, safe keyboard workflow evidence | yes | One headless run; focus handling can differ with browser UI present., Reachability failure often indicates focus-order problems too., Visibility is estimated from size and CSS; skip links that appear on focus are a valid pattern. |
| 2.4.4 | Link Purpose (In Context) | A | partially_automated | `generic_link_text`, `missing_link_name` | static | source markup and parsed element evidence | yes | Generic visible text can still be acceptable when programmatic context (aria-labelledby, list context) disambiguates it., Only detects empty names, not misleading ones. |
| 2.4.5 | Multiple Ways | AA | unsupported | none | none | none | yes | No implemented A11yway rule currently produces criterion-specific evidence. |
| 2.4.6 | Headings and Labels | AA | partially_automated | `missing_h1` | static | source markup and parsed element evidence | yes | Absence of an h1 is not itself a 2.4.6 failure. |
| 2.4.7 | Focus Visible | AA | partially_automated | `browser_focus_on_hidden_element`, `focus_indicator_missing` | browser_interaction, low_vision | keyboard traversal and browser interaction evidence, rendered geometry and computed style evidence | yes | An invisible focused element usually has no visible indicator, but the pattern needs human judgment., Compares focused and unfocused computed styles (outline, box-shadow, border, background, text-decoration, transform, pseudo-elements, parent styles) in one Chromium run; animated or canvas-drawn indicators can still be missed. |
| 2.4.11 | Focus Not Obscured (Minimum) | AA | partially_automated | `focus_obscured` | low_vision | rendered geometry and computed style evidence | yes | Bounding-box and hit-test sampling against sticky/fixed overlays in one run; overlays that appear only after user actions are not seen. |
| 2.5.1 | Pointer Gestures | A | partially_automated | `pointer_gesture_no_alternative` | static | source markup and parsed element evidence | yes | Event-name heuristic for swipe, pinch, path, or pointer-move interactions; visible alternatives are inferred from control text. |
| 2.5.2 | Pointer Cancellation | A | partially_automated | `pointer_down_activation` | static | source markup and parsed element evidence | yes | Requires down-event evidence and no obvious up/cancel handler, but cannot verify final activation behavior. |
| 2.5.3 | Label in Name | A | partially_automated | `label_in_name_mismatch` | static | source markup and parsed element evidence | yes | Normalized substring comparison of visible text vs aria-label; icon-only and very short labels are skipped. |
| 2.5.4 | Motion Actuation | A | manual_only | none | none | none | yes | No implemented A11yway rule currently produces criterion-specific evidence. |
| 2.5.7 | Dragging Movements | AA | partially_automated | `dragging_no_alternative` | static | source markup and parsed element evidence | yes | Detects draggable markup or drag/drop script names and common non-drag alternatives; cannot prove dragging is required. |
| 2.5.8 | Target Size (Minimum) | AA | partially_automated | `small_target_size` | low_vision | rendered geometry and computed style evidence | yes | Measured in one Chromium run at default zoom; inline text links and targets with sufficient surrounding spacing are excluded, but equivalent-control and essential exceptions need human judgment. |
| 3.1.1 | Language of Page | A | automated | `missing_html_lang`, `missing_lang_indic` | static | source markup and parsed element evidence | no | Direct for static HTML; a lang attribute added by JavaScript would be missed in static mode., Unicode-range script detection; languages sharing a script cannot be told apart. |
| 3.1.2 | Language of Parts | AA | partially_automated | `lang_mismatch`, `missing_lang_indic`, `mixed_script_element` | static | source markup and parsed element evidence | yes | Conservative heuristic; may flag intentional bilingual lines., Fires only when the script itself contradicts the declaration., Same script heuristic; transliterated text is invisible. |
| 3.2.1 | On Focus | A | partially_automated | `focus_context_change` | static | source markup and parsed element evidence | yes | Inline onfocus-handler evidence only; external scripts and actual browser state changes require interaction testing. |
| 3.2.2 | On Input | A | partially_automated | `input_context_change` | static | source markup and parsed element evidence | yes | Inline input/change-handler evidence only; external scripts and warning mechanisms may be missed. |
| 3.2.3 | Consistent Navigation | AA | unsupported | none | none | none | yes | No implemented A11yway rule currently produces criterion-specific evidence. |
| 3.2.4 | Consistent Identification | AA | unsupported | none | none | none | yes | No implemented A11yway rule currently produces criterion-specific evidence. |
| 3.2.6 | Consistent Help | A | manual_only | none | none | none | yes | No implemented A11yway rule currently produces criterion-specific evidence. |
| 3.3.1 | Error Identification | A | partially_automated | `error_not_identified` | static | source markup and parsed element evidence | yes | Static error markup is inspected for aria-invalid/aria-describedby association; runtime validation may be different. |
| 3.3.2 | Labels or Instructions | A | partially_automated | `missing_form_label`, `visual_required_not_programmatic` | static | source markup and parsed element evidence | yes | Static HTML only; labels added by JavaScript are seen only in browser mode., The visible instruction exists; only the programmatic exposure is missing. |
| 3.3.3 | Error Suggestion | AA | partially_automated | `error_suggestion_missing` | static | source markup and parsed element evidence | yes | Checks static error text for common correction guidance words; it cannot judge all useful suggestions. |
| 3.3.4 | Error Prevention (Legal, Financial, Data) | AA | partially_automated | `error_prevention_missing` | static | source markup and parsed element evidence | yes | Keyword heuristic for high-consequence public forms; it does not submit forms or inspect later workflow steps. |
| 3.3.7 | Redundant Entry | A | partially_automated | `redundant_entry_repeated_field` | static | source markup and parsed element evidence | yes | Single-page repeated-field inference only; full redundant-entry testing needs a controlled workflow. |
| 3.3.8 | Accessible Authentication (Minimum) | AA | partially_automated | `accessible_authentication_barrier` | static | source markup and parsed element evidence | yes | Public-page heuristic for paste blocking and CAPTCHA-like challenge text; authentication is never attempted. |
| 4.1.2 | Name, Role, Value | A | partially_automated | `browser_focused_control_missing_name`, `missing_button_name`, `missing_form_label`, `missing_link_name`, `unnamed_focus_stop` | accessibility_tree, browser_interaction, static | computed accessibility-tree evidence, keyboard traversal and browser interaction evidence, source markup and parsed element evidence | yes | A missing label usually means a missing accessible name, but the browser may compute one from other sources., Chromium's computed tree in one run; real screen readers apply their own rules., Heuristic name estimate; only used when accessibility tree data is unavailable., Static heuristic on source HTML., Static heuristic; icon fonts and JavaScript-injected names are invisible statically. |
| 4.1.3 | Status Messages | AA | partially_automated | `status_message_not_live`, `task_expected_content_missing` | static, task_execution | safe keyboard workflow evidence, source markup and parsed element evidence | yes | Compares normalized visible text only; the status may exist but use different wording., Static status-like content only; dynamic before/after accessibility-tree behavior is not reproduced. |

## Rules by Criterion

- 1.1.1 Non-text Content: `image_empty_alt_suspicious`, `missing_image_alt`
- 1.2.1 Audio-only and Video-only (Prerecorded): `missing_audio_transcript`
- 1.2.2 Captions (Prerecorded): `missing_video_captions`
- 1.2.3 Audio Description or Media Alternative (Prerecorded): none
- 1.2.4 Captions (Live): none
- 1.2.5 Audio Description (Prerecorded): none
- 1.3.1 Info and Relationships: `fake_heading`, `missing_form_label`, `missing_h1`, `multiple_h1`, `radio_group_missing_fieldset`, `skipped_heading_level`, `table_missing_headers`, `visual_required_not_programmatic`
- 1.3.2 Meaningful Sequence: `meaningful_sequence_reorder`
- 1.3.3 Sensory Characteristics: `sensory_instruction`
- 1.3.4 Orientation: `orientation_restriction`
- 1.3.5 Identify Input Purpose: `autocomplete_unsupported_control`, `contradictory_autocomplete`, `invalid_autocomplete_token`, `missing_autocomplete`
- 1.4.1 Use of Color: `color_only_indicator`
- 1.4.2 Audio Control: `autoplay_audio_no_control`
- 1.4.3 Contrast (Minimum): `contrast_unresolved_background`, `low_contrast_text`
- 1.4.4 Resize Text: `reflow_clipped_content`
- 1.4.5 Images of Text: `image_of_text`
- 1.4.10 Reflow: `reflow_clipped_content`, `reflow_horizontal_scroll`, `reflow_overlap`, `zoom_fixed_width_content`, `zoom_horizontal_overflow`
- 1.4.11 Non-text Contrast: none
- 1.4.12 Text Spacing: `text_spacing_content_loss`
- 1.4.13 Content on Hover or Focus: `hover_focus_content`
- 2.1.1 Keyboard: `browser_focus_not_moving`, `browser_no_focusable_elements`, `task_control_not_keyboard_reachable`, `task_step_blocked`
- 2.1.2 No Keyboard Trap: `browser_repeated_focus`, `keyboard_trap`
- 2.1.4 Character Key Shortcuts: `single_character_shortcut`
- 2.2.1 Timing Adjustable: `timing_adjustable_missing`
- 2.2.2 Pause, Stop, Hide: `moving_content_no_pause`
- 2.3.1 Three Flashes or Below Threshold: `possible_flashing_content`
- 2.4.1 Bypass Blocks: `no_bypass_mechanism`
- 2.4.2 Page Titled: `missing_page_title`
- 2.4.3 Focus Order: `browser_focus_on_hidden_element`, `focus_lost`, `task_control_not_keyboard_reachable`
- 2.4.4 Link Purpose (In Context): `generic_link_text`, `missing_link_name`
- 2.4.5 Multiple Ways: none
- 2.4.6 Headings and Labels: `missing_h1`
- 2.4.7 Focus Visible: `browser_focus_on_hidden_element`, `focus_indicator_missing`
- 2.4.11 Focus Not Obscured (Minimum): `focus_obscured`
- 2.5.1 Pointer Gestures: `pointer_gesture_no_alternative`
- 2.5.2 Pointer Cancellation: `pointer_down_activation`
- 2.5.3 Label in Name: `label_in_name_mismatch`
- 2.5.4 Motion Actuation: none
- 2.5.7 Dragging Movements: `dragging_no_alternative`
- 2.5.8 Target Size (Minimum): `small_target_size`
- 3.1.1 Language of Page: `missing_html_lang`, `missing_lang_indic`
- 3.1.2 Language of Parts: `lang_mismatch`, `missing_lang_indic`, `mixed_script_element`
- 3.2.1 On Focus: `focus_context_change`
- 3.2.2 On Input: `input_context_change`
- 3.2.3 Consistent Navigation: none
- 3.2.4 Consistent Identification: none
- 3.2.6 Consistent Help: none
- 3.3.1 Error Identification: `error_not_identified`
- 3.3.2 Labels or Instructions: `missing_form_label`, `visual_required_not_programmatic`
- 3.3.3 Error Suggestion: `error_suggestion_missing`
- 3.3.4 Error Prevention (Legal, Financial, Data): `error_prevention_missing`
- 3.3.7 Redundant Entry: `redundant_entry_repeated_field`
- 3.3.8 Accessible Authentication (Minimum): `accessible_authentication_barrier`
- 4.1.2 Name, Role, Value: `browser_focused_control_missing_name`, `missing_button_name`, `missing_form_label`, `missing_link_name`, `unnamed_focus_stop`
- 4.1.3 Status Messages: `status_message_not_live`, `task_expected_content_missing`

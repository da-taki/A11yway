# Rules

Rules describe evidence A11yway can collect. They do not prove full WCAG conformance.

Each finding is normalized through `a11yway/core/rules.py` and mapped to WCAG evidence through `a11yway/data/wcag22_coverage.json`. The generated matrix is `docs/WCAG22_COVERAGE.md`.

## Confidence

- `confirmed` or `strong`: stronger deterministic evidence.
- `likely`: useful evidence that still needs review.
- `needs_review`: a review prompt, not a confirmed violation.
- `informational`: context for the reviewer.

## Current Rule Groups

### Authentication

- `accessible_authentication_barrier`: Authentication flow may require a cognitive function test without an accessible alternative.

### Content

- `sensory_instruction`: Instruction may rely on sensory characteristics only.

### Dynamic Feedback

- `status_message_not_live`: Status message may not be exposed programmatically.

### Forms

- `autocomplete_unsupported_control`: Autocomplete is set on an unsupported control.
- `contradictory_autocomplete`: Autocomplete token contradicts the field purpose.
- `error_not_identified`: Error message may not identify the affected field.
- `error_prevention_missing`: High-consequence form may lack visible review or reversal steps.
- `error_suggestion_missing`: Error message may lack a correction suggestion.
- `invalid_autocomplete_token`: Autocomplete token is invalid.
- `missing_autocomplete`: Common personal-data field is missing an autocomplete token.
- `missing_form_label`: Form control missing accessible label.
- `radio_group_missing_fieldset`: Radio group is not grouped with fieldset/legend.
- `redundant_entry_repeated_field`: Workflow may ask for the same information more than once.
- `visual_required_not_programmatic`: Required marker is visual only.

### Headings & Structure

- `fake_heading`: Styled text may act as a heading without heading markup.
- `missing_h1`: Page missing an h1 heading.
- `multiple_h1`: Page has multiple h1 headings.
- `skipped_heading_level`: Heading level is skipped.

### Images

- `image_empty_alt_suspicious`: Empty alt on an image that looks informative.
- `image_of_text`: Graphic appears to contain text.
- `missing_image_alt`: Image missing useful alt text.

### Interaction

- `focus_context_change`: Focus may trigger a context change.
- `hover_focus_content`: Hover or focus may reveal additional content.
- `input_context_change`: Changing a control may trigger a context change.

### Interactive Elements

- `generic_link_text`: Link text is too generic.
- `label_in_name_mismatch`: Visible label is missing from the accessible name.
- `missing_button_name`: Button missing accessible name.
- `missing_link_name`: Link missing accessible name.

### Keyboard Interaction

- `browser_focus_not_moving`: Keyboard focus does not move into the page.
- `browser_focus_on_hidden_element`: Keyboard focus landed on a hidden element.
- `browser_focused_control_missing_name`: Focused control has no accessible name.
- `browser_no_focusable_elements`: No keyboard focusable elements found.
- `browser_repeated_focus`: Keyboard focus repeats on the same element.
- `focus_lost`: Keyboard focus left the page content.
- `keyboard_trap`: Keyboard focus is trapped in a loop.
- `single_character_shortcut`: Single-character keyboard shortcut may be active.
- `unnamed_focus_stop`: Focus stop announces no accessible name.

### Language

- `lang_mismatch`: Declared lang contradicts the text's script.
- `missing_lang_indic`: Indic-script text lacks a matching lang attribute.
- `mixed_script_element`: Latin and Indic scripts mix without a lang boundary.

### Low Vision

- `color_only_indicator`: Color may be the only indicator.
- `contrast_unresolved_background`: Text contrast could not be resolved reliably.
- `focus_indicator_missing`: Focused element may not show a visible focus indicator.
- `focus_obscured`: Focused control is covered by overlaying content.
- `low_contrast_text`: Rendered text may have low contrast.
- `reflow_clipped_content`: Content is clipped outside the zoomed viewport.
- `reflow_horizontal_scroll`: Page requires horizontal scrolling under zoom.
- `reflow_overlap`: Interactive elements overlap under zoom.
- `small_target_size`: Interactive target is smaller than 24x24 CSS pixels.
- `text_spacing_content_loss`: Content breaks under WCAG text-spacing overrides.
- `zoom_fixed_width_content`: Fixed or wide content may prevent reflow.
- `zoom_horizontal_overflow`: Page has horizontal overflow under zoom/reflow stress.

### Media

- `autoplay_audio_no_control`: Autoplaying audio may lack independent controls.
- `missing_audio_transcript`: Audio missing a transcript.
- `missing_video_captions`: Video missing captions.

### Motion

- `interaction_motion_no_reduced_motion`: Interaction-triggered motion lacks reduced-motion evidence.
- `moving_content_no_pause`: Auto-moving content may lack pause controls.
- `possible_flashing_content`: Animation may flash rapidly.

### Page Metadata

- `missing_html_lang`: HTML document missing a language.
- `missing_page_title`: Page missing a title.

### Pointer Interaction

- `dragging_no_alternative`: Function may require dragging.
- `pointer_down_activation`: Control may activate on pointer down.
- `pointer_gesture_no_alternative`: Function may require a path or multipoint gesture.

### Responsive Layout

- `orientation_restriction`: Page may restrict use to one orientation.

### Structure

- `meaningful_sequence_reorder`: CSS may reorder content away from DOM order.
- `no_bypass_mechanism`: No apparent way to bypass repeated navigation.
- `table_missing_headers`: Data table has no header cells.

### Task Execution

- `task_control_not_keyboard_reachable`: Task control is not reachable with the keyboard.
- `task_expected_content_missing`: Expected task content is missing.
- `task_step_blocked`: Task step could not be completed with the keyboard.

### Timing

- `timing_adjustable_missing`: Timed behavior may not be adjustable.

Use `python -m a11yway.main --rule ISSUE_TYPE` for detailed rule metadata from the registry.

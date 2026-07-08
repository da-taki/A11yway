"""Map issue types to practical accessibility fixes."""

from __future__ import annotations


class FixSuggester:
    """Suggests plain-language fixes for common issue types."""

    def __init__(self) -> None:
        self.fix_map = {
            "missing_label": "Add a visible label and connect it to the form field.",
            "missing_form_label": (
                "Add a visible <label> connected with for/id. Use aria-label only "
                "when a visible label is not possible. Later, associate helper text "
                "and error messages programmatically."
            ),
            "low_contrast": "Increase text and control contrast so content is easier to read.",
            "missing_transcript": "Add a transcript near the audio or video lesson.",
            "captions_transcripts": "Provide synchronized captions and a full text transcript.",
            "plain_language_review": "Simplify instructions and use short, direct sentences.",
            "keyboard_form_completion": "Ensure the full form can be completed with only the keyboard.",
            "missing_button_name": "Add clear button text or an aria-label that describes the button action.",
            "missing_link_name": "Add descriptive link text that explains the link destination or action.",
            "generic_link_text": (
                'Use descriptive link text like "Download scholarship guidelines" '
                'instead of "click here."'
            ),
            "missing_image_alt": "Add alt text that describes the image purpose, or mark decorative images as presentation.",
            "missing_h1": "Add one clear h1 that matches the page purpose.",
            "skipped_heading_level": "Do not skip heading levels; move from h1 to h2 before h3.",
            "multiple_h1": "Use one main h1 for the page purpose, then organize sections with h2 and lower headings.",
            "missing_page_title": "Add a short, descriptive page title.",
            "missing_html_lang": 'Add lang="en" or the correct document language to the html element.',
            "missing_video_captions": "Add captions or subtitles for education video content.",
            "missing_audio_transcript": "Add a transcript near audio lessons or instructions.",
        }

    def suggest_fix(self, issue_type: str) -> str:
        """Return a practical fix for an issue type."""
        return self.fix_map.get(
            issue_type,
            "Review this barrier manually and provide a clear accessible alternative.",
        )

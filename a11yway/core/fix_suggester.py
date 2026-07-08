"""Map issue types to practical accessibility fixes."""

from __future__ import annotations


class FixSuggester:
    """Suggests plain-language fixes for common issue types."""

    def __init__(self) -> None:
        self.fix_map = {
            "missing_label": "Add a visible label and connect it to the form field.",
            "low_contrast": "Increase text and control contrast so content is easier to read.",
            "missing_transcript": "Add a transcript near the audio or video lesson.",
            "captions_transcripts": "Provide synchronized captions and a full text transcript.",
            "plain_language_review": "Simplify instructions and use short, direct sentences.",
            "keyboard_form_completion": "Ensure the full form can be completed with only the keyboard.",
        }

    def suggest_fix(self, issue_type: str) -> str:
        """Return a practical fix for an issue type."""
        return self.fix_map.get(
            issue_type,
            "Review this barrier manually and provide a clear accessible alternative.",
        )

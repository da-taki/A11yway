from pathlib import Path

from a11yway.core.comment_scan import format_comment_scan, scan_first_party_comments


def test_first_party_source_has_no_explanatory_comments() -> None:
    result = scan_first_party_comments(Path.cwd())
    assert result["total"] == 0, format_comment_scan(Path.cwd())

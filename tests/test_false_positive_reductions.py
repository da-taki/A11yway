

from a11yway.core.page_analyzer import (
    analyze_heading_structure,
    analyze_html_forms,
    analyze_images,
    analyze_interactive_names,
)


def issue_types(issues: list) -> set[str]:
    return {issue.issue_type for issue in issues}





def test_plain_empty_alt_is_respected_as_decorative() -> None:

    assert analyze_images('<img src="divider.png" alt="">') == []


def test_empty_alt_with_presentation_role_passes() -> None:
    assert analyze_images('<img src="x.png" alt="" role="presentation">') == []


def test_empty_alt_inside_named_link_is_not_flagged() -> None:

    html = '<a href="/home" aria-label="Home"><img src="logo.png" alt=""></a>'
    assert analyze_images(html) == []


def test_empty_alt_next_to_link_text_is_not_flagged() -> None:
    html = '<a href="/home"><img src="logo.png" alt="">Home</a>'
    assert analyze_images(html) == []


def test_empty_alt_as_only_content_of_link_is_flagged() -> None:
    html = '<a href="/home"><img src="logo.png" alt=""></a>'
    issues = analyze_images(html)
    assert issue_types(issues) == {"missing_image_alt"}
    assert issues[0].severity == "high"


def test_empty_alt_with_informative_filename_is_review_only() -> None:
    issues = analyze_images('<img src="chart-results.png" alt="">')
    assert issue_types(issues) == {"image_empty_alt_suspicious"}
    assert issues[0].severity == "low"


def test_missing_alt_on_spacer_is_downgraded() -> None:
    issues = analyze_images('<img src="spacer.gif">')
    assert len(issues) == 1
    assert issues[0].severity == "low"
    assert issues[0].confidence == "needs_review"


def test_missing_alt_on_content_image_still_flagged() -> None:
    issues = analyze_images('<img src="campus-photo.jpg">')
    assert issue_types(issues) == {"missing_image_alt"}
    assert issues[0].severity == "medium"


def test_hidden_image_is_ignored() -> None:
    assert analyze_images('<div hidden><img src="photo.jpg"></div>') == []





def test_hidden_attribute_control_is_ignored() -> None:
    assert analyze_html_forms('<form><input type="text" name="ghost" hidden></form>') == []


def test_display_none_control_is_ignored() -> None:
    html = '<form><input type="text" name="ghost" style="display: none"></form>'
    assert analyze_html_forms(html) == []


def test_aria_hidden_ancestor_hides_control() -> None:
    html = '<div aria-hidden="true"><input type="text" name="ghost"></div>'
    assert analyze_html_forms(html) == []


def test_visible_unlabeled_control_is_still_flagged() -> None:
    issues = analyze_html_forms('<form><input type="text" name="real"></form>')
    assert issue_types(issues) == {"missing_form_label"}


def test_placeholder_only_is_still_flagged_with_note() -> None:

    issues = analyze_html_forms('<input type="text" name="q2" placeholder="Your name">')
    assert issue_types(issues) == {"missing_form_label"}
    assert issues[0].evidence.get("placeholder_only") is True
    assert "placeholder" in issues[0].evidence["reason"]





def test_generic_text_with_specific_aria_label_passes() -> None:
    html = '<a href="/guide" aria-label="Download scholarship guidelines">Learn more</a>'
    assert "generic_link_text" not in issue_types(analyze_interactive_names(html))


def test_generic_text_with_aria_labelledby_passes() -> None:
    html = (
        '<h3 id="grants">Grant deadlines</h3>'
        '<a href="/grants" aria-labelledby="grants">Read more</a>'
    )
    assert "generic_link_text" not in issue_types(analyze_interactive_names(html))


def test_generic_aria_label_is_still_flagged() -> None:

    html = '<a href="/x" aria-label="read more">something specific</a>'
    assert "generic_link_text" in issue_types(analyze_interactive_names(html))


def test_plain_generic_link_is_still_flagged() -> None:
    html = '<a href="/x">click here</a>'
    assert "generic_link_text" in issue_types(analyze_interactive_names(html))


def test_hidden_link_is_ignored() -> None:
    html = '<div style="display:none"><a href="/x"></a></div>'
    assert analyze_interactive_names(html) == []





def test_multiple_h1_is_informational() -> None:
    html = "<h1>One</h1><h1>Two</h1>"
    issues = [
        issue
        for issue in analyze_heading_structure(html)
        if issue.issue_type == "multiple_h1"
    ]
    assert len(issues) == 1
    assert issues[0].severity == "low"
    assert "review evidence" in issues[0].evidence["reason"]


def test_heading_skip_within_one_flow_is_flagged() -> None:
    html = "<h1>Main</h1><h3>Detail</h3>"
    assert "skipped_heading_level" in issue_types(analyze_heading_structure(html))


def test_heading_restart_inside_article_is_not_a_skip() -> None:

    html = (
        "<h1>Feed</h1><h2>Today</h2>"
        "<article><h4>Embedded card title</h4></article>"
    )
    assert "skipped_heading_level" not in issue_types(analyze_heading_structure(html))


def test_heading_restart_inside_labeled_region_is_not_a_skip() -> None:
    html = (
        "<h1>Page</h1>"
        '<div role="region" aria-label="Related links"><h4>See also</h4></div>'
    )
    assert "skipped_heading_level" not in issue_types(analyze_heading_structure(html))


def test_skip_inside_same_article_is_still_flagged() -> None:

    html = "<article><h2>Story</h2><h5>Fine print</h5></article>"
    assert "skipped_heading_level" in issue_types(analyze_heading_structure(html))

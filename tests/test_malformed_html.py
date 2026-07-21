







from a11yway.core.page_analyzer import analyze_html_static


def issue_types(html: str) -> list[str]:

    return [issue.issue_type for issue in analyze_html_static(html)]


def test_unclosed_label_is_closed_by_container_end_tag() -> None:

    html = (
        '<div><label>Name<input id="a"></div>'
        '<input id="b" type="text">'
    )

    issues = analyze_html_static(html)
    unlabeled = [
        issue for issue in issues if issue.issue_type == "missing_form_label"
    ]

    assert len(unlabeled) == 1
    assert unlabeled[0].evidence["id"] == "b"


def test_sibling_unclosed_labels_each_wrap_their_own_control() -> None:

    html = (
        '<label>Name <input id="a">'
        '<label>Email <input id="b">'
    )

    assert "missing_form_label" not in issue_types(html)


def test_script_text_is_not_a_button_name() -> None:

    html = "<button><script>doThing()</script></button>"

    assert "missing_button_name" in issue_types(html)


def test_style_text_is_not_a_link_name() -> None:

    html = '<a href="/x"><style>.a { color: red; }</style></a>'

    assert "missing_link_name" in issue_types(html)


def test_script_text_does_not_satisfy_audio_transcript_check() -> None:

    html = '<audio src="x.mp3"></audio><script>var transcript = 1;</script>'

    assert "missing_audio_transcript" in issue_types(html)


def test_visible_transcript_text_still_satisfies_audio_check() -> None:

    html = '<audio src="x.mp3"></audio><p>Read the transcript below.</p>'

    assert "missing_audio_transcript" not in issue_types(html)


def test_new_anchor_implicitly_closes_unclosed_anchor() -> None:

    html = '<a href="/one">click here<a href="/two">Two page</a>'

    issues = [
        issue
        for issue in analyze_html_static(html)
        if issue.issue_type == "generic_link_text"
    ]

    assert len(issues) == 1
    assert issues[0].evidence["href"] == "/one"


def test_stray_end_tags_do_not_hide_findings() -> None:

    html = '</div></p></span><input id="x" type="text">'

    assert "missing_form_label" in issue_types(html)


def test_unclosed_title_still_counts_as_page_title() -> None:

    html = '<html lang="en"><head><title>Scholarship Portal'

    assert "missing_page_title" not in issue_types(html)


def test_unquoted_and_uppercase_attributes_parse() -> None:

    labeled = '<LABEL FOR=email>Email</LABEL><INPUT ID=email TYPE=text>'
    unlabeled = "<INPUT ID=phone TYPE=text>"

    assert "missing_form_label" not in issue_types(labeled)
    assert "missing_form_label" in issue_types(unlabeled)


def test_paragraph_soup_keeps_heading_checks_working() -> None:

    html = "<p>one<p>two<p>three<h1>Title</h1><h3>Sub</h3>"
    types = issue_types(html)

    assert "skipped_heading_level" in types
    assert "missing_h1" not in types


def test_severely_malformed_html_degrades_instead_of_crashing() -> None:

    html = (
        "<!DOCTYPE mangled <html><<div>< a href=>"
        '<input id="x" type="text">'
        "<![bogus[data]]><b><i></b></i><table><td><tr>"
    )

    issues = analyze_html_static(html)

    assert isinstance(issues, list)
    assert "missing_form_label" in [issue.issue_type for issue in issues]


def test_empty_and_whitespace_sources_return_page_level_findings() -> None:

    for html in ["", "   \n\t  "]:
        types = issue_types(html)
        assert "missing_page_title" in types
        assert "missing_html_lang" in types

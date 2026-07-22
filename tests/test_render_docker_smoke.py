from __future__ import annotations

import pytest

from scripts.render_docker_smoke import _assert_landing_form


VALID_FORM = """
<!doctype html>
<html>
  <body>
    <form id="audit" method="post" action="/audit">
      <label for="url">Audit a URL</label>
      <input id="url" name="url" type="url" required>
      <label>
        <input name="permission" type="checkbox" required>
        I have permission.
      </label>
      <button type="submit">Run audit</button>
    </form>
  </body>
</html>
"""


def test_landing_form_structure_passes() -> None:
    _assert_landing_form(VALID_FORM)


def test_landing_form_does_not_depend_on_submit_text() -> None:
    _assert_landing_form(VALID_FORM.replace("Run audit", "Start review"))


@pytest.mark.parametrize(
    ("html", "message"),
    [
        (VALID_FORM.replace('name="url"', 'name="target"'), "URL input"),
        (VALID_FORM.replace('name="permission"', 'name="confirm"'), "permission checkbox"),
        (VALID_FORM.replace('<button type="submit">Run audit</button>', ""), "submit control"),
        ("<html><body><p>No form here.</p></body></html>", "audit form"),
        ("TemplateSyntaxError: broken template", "template error"),
    ],
)
def test_landing_form_structure_failures(html: str, message: str) -> None:
    with pytest.raises(AssertionError, match=message):
        _assert_landing_form(html)

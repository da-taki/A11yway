from __future__ import annotations

import json
import subprocess
import sys
import tarfile
import zipfile
from pathlib import Path
import tomllib

import pytest

import a11yway
from a11yway.core.extended_results import EXTENDED_RESULT_SCHEMA_VERSION
from a11yway.core.report_builder import REPORT_SCHEMA_VERSION, build_json_report
from a11yway.main import _apply_all_accessibility_modules, parse_args


ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session")
def built_release_dist(tmp_path_factory) -> Path:
    out_dir = tmp_path_factory.mktemp("release-dist")
    subprocess.run(
        [
            sys.executable,
            "-m",
            "build",
            "--no-isolation",
            "--sdist",
            "--wheel",
            "--outdir",
            str(out_dir),
        ],
        cwd=ROOT,
        check=True,
    )
    return out_dir


def _pyproject() -> dict:
    return tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))


def _requirements_browser() -> str:
    return (ROOT / "requirements-browser.txt").read_text(encoding="utf-8")


def _dockerfile() -> str:
    return (ROOT / "Dockerfile").read_text(encoding="utf-8")


def _dockerignore() -> str:
    return (ROOT / ".dockerignore").read_text(encoding="utf-8")


def test_single_version_source_and_cli_version() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "a11yway.main", "--version"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )

    assert a11yway.__version__ == "0.8.0b1"
    assert completed.stdout.strip() == f"a11yway {a11yway.__version__}"


def test_package_metadata_uses_dynamic_version_and_console_script() -> None:
    data = _pyproject()

    assert data["project"]["name"] == "a11yway"
    assert data["project"]["dynamic"] == ["version"]
    assert data["tool"]["setuptools"]["dynamic"]["version"]["attr"] == "a11yway.__version__"
    assert data["project"]["scripts"]["a11yway"] == "a11yway.main:main"


def test_optional_dependency_groups_are_represented() -> None:
    extras = _pyproject()["project"]["optional-dependencies"]

    for group in ("browser", "documents", "media", "ai", "web", "development", "all"):
        assert group in extras
    assert "playwright==1.61.0" in extras["browser"]
    assert "pypdf" in extras["documents"]
    assert "mutagen" in extras["media"]
    assert "groq" in extras["ai"]
    assert "Flask" in extras["web"]
    assert {
        "build",
        "coverage",
        "pytest",
        "pytest-cov",
        "setuptools>=69",
        "wheel",
    }.issubset(extras["development"])
    assert not any("ffmpeg" in item.lower() for deps in extras.values() for item in deps)


def test_schema_versions_are_consistent_in_reports() -> None:
    report = build_json_report("fixture.html", [])

    assert report["report_schema_version"] == REPORT_SCHEMA_VERSION
    assert report["extended_result_schema_version"] == EXTENDED_RESULT_SCHEMA_VERSION
    assert report["version"] == a11yway.__version__
    json.dumps(report)


def test_required_release_documents_exist() -> None:
    for path in [
        "CHANGELOG.md",
        "docs/RELEASE_CHECKLIST.md",
        "docs/PRODUCTION_READINESS_REPORT.md",
        "docs/REPORT_SCHEMA.md",
    ]:
        assert (ROOT / path).exists(), path


def test_ci_workflow_contains_release_checks_without_native_adapter_requirements() -> None:
    workflow = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")

    assert "ubuntu-latest" in workflow
    assert "windows-latest" in workflow
    assert 'python -m pip install -e ".[development,browser,documents,media,web]"' in workflow
    assert 'python -c "import flask; import a11yway.web_app"' in workflow
    assert "python -m playwright install --with-deps chromium" in workflow
    assert "python -m pip check" in workflow
    assert "python -m build" in workflow
    assert "scripts/verify_wheel_install.py" in workflow
    assert "Render Docker smoke" in workflow
    assert "docker build -t a11yway-render-smoke ." in workflow
    assert "python scripts/render_docker_smoke.py" in workflow
    assert "NVDA" not in workflow
    assert "JAWS" not in workflow


def test_browser_dependency_is_pinned_for_docker_and_extras() -> None:
    requirements = _requirements_browser()
    extras = _pyproject()["project"]["optional-dependencies"]

    assert "playwright==1.61.0" in requirements
    assert "playwright==1.61.0" in extras["browser"]
    assert "playwright==1.61.0" in extras["all"]


def test_render_dockerfile_uses_python_312_and_matching_playwright_install() -> None:
    dockerfile = _dockerfile()

    assert "FROM python:3.12-bookworm" in dockerfile
    assert "mcr.microsoft.com/playwright" not in dockerfile
    assert "python -m pip install --no-cache-dir -r requirements-web.txt" in dockerfile
    assert "python -m playwright install --with-deps chromium" in dockerfile
    assert 'gunicorn a11yway.web_app:app --bind 0.0.0.0:${PORT:-10000}' in dockerfile


def test_render_docker_context_excludes_secrets_and_generated_reports() -> None:
    dockerignore = _dockerignore()

    assert ".env" in dockerignore
    assert ".env.*" in dockerignore
    assert "!.env.example" in dockerignore
    assert "reports/" in dockerignore
    assert ".git" in dockerignore


def test_all_accessibility_modules_still_excludes_passive_security() -> None:
    args = parse_args(["examples/sample_form.html", "--all-accessibility-modules"])

    _apply_all_accessibility_modules(args)

    assert args.forms
    assert args.mobile
    assert args.screen_reader
    assert not args.passive_security


def test_release_build_outputs_have_expected_names_and_package_data(built_release_dist: Path) -> None:
    wheel = next(built_release_dist.glob("a11yway-0.8.0b1-py3-none-any.whl"))
    sdist = next(built_release_dist.glob("a11yway-0.8.0b1.tar.gz"))

    with zipfile.ZipFile(wheel) as archive:
        names = set(archive.namelist())
    assert "a11yway/workflow_packs/scholarships.json" in names
    assert "a11yway/templates/web_demo/home.html" in names

    with tarfile.open(sdist) as archive:
        sdist_names = set(archive.getnames())
    assert "a11yway-0.8.0b1/pyproject.toml" in sdist_names
    assert "a11yway-0.8.0b1/README.md" in sdist_names
    assert not any(name.endswith("/.env") or name.endswith("/debug.log") for name in sdist_names)


def test_wheel_imports_from_installed_environment_outside_source_tree(built_release_dist: Path) -> None:
    wheel = next(built_release_dist.glob("a11yway-0.8.0b1-py3-none-any.whl"))

    completed = subprocess.run(
        [sys.executable, "scripts/verify_wheel_install.py", str(wheel)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )

    assert "console_version: a11yway 0.8.0b1" in completed.stdout
    assert "package_import: 0.8.0b1" in completed.stdout
    assert "fixture_audit: A11yway static HTML accessibility audit" in completed.stdout

"""Verify an A11yway wheel from a clean virtual environment."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def _run(command: list[str], *, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        text=True,
        capture_output=True,
        check=True,
    )


def _venv_python(venv: Path) -> Path:
    if sys.platform == "win32":
        return venv / "Scripts" / "python.exe"
    return venv / "bin" / "python"


def _venv_script(venv: Path, name: str) -> Path:
    if sys.platform == "win32":
        return venv / "Scripts" / f"{name}.exe"
    return venv / "bin" / name


def verify_wheel(wheel: Path, *, keep_env: bool = False) -> dict[str, str]:
    """Install a wheel in a temporary venv and run release smoke checks."""
    if not wheel.exists():
        raise FileNotFoundError(wheel)

    temp_root = Path(tempfile.mkdtemp(prefix="a11yway-wheel-smoke-"))
    venv = temp_root / "venv"
    work = temp_root / "work"
    work.mkdir()
    sample = work / "sample.html"
    sample.write_text(
        "<html lang='en'><head><title>Smoke</title></head><body><h1>Smoke</h1></body></html>",
        encoding="utf-8",
    )

    results: dict[str, str] = {"temp_root": str(temp_root)}
    try:
        _run([sys.executable, "-m", "venv", str(venv)])
        python = _venv_python(venv)
        a11yway = _venv_script(venv, "a11yway")
        _run([str(python), "-m", "pip", "install", str(wheel)])
        checks = {
            "console_help": [str(a11yway), "--help"],
            "console_version": [str(a11yway), "--version"],
            "console_capabilities": [str(a11yway), "--capabilities"],
            "console_wcag_coverage": [str(a11yway), "--wcag-coverage"],
            "package_import": [
                str(python),
                "-c",
                "import a11yway; print(a11yway.__version__)",
            ],
            "fixture_audit": [str(a11yway), str(sample)],
        }
        for name, command in checks.items():
            completed = _run(command, cwd=work)
            results[name] = completed.stdout.strip().splitlines()[0] if completed.stdout.strip() else "ok"
        return results
    finally:
        if keep_env:
            print(f"Kept smoke environment: {temp_root}")
        else:
            shutil.rmtree(temp_root, ignore_errors=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("wheel", type=Path)
    parser.add_argument("--keep-env", action="store_true")
    args = parser.parse_args(argv)
    results = verify_wheel(args.wheel, keep_env=args.keep_env)
    for name, value in results.items():
        if name == "temp_root" and not args.keep_env:
            continue
        print(f"{name}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


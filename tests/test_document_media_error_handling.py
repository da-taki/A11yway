from __future__ import annotations

import sys
import types

import pytest

from a11yway.core.document_audit import analyze_document
from a11yway.core.media_audit import analyze_media_file


@pytest.mark.parametrize("suffix", [".pdf", ".docx", ".pptx"])
def test_malformed_documents_report_parse_failure(tmp_path, suffix: str) -> None:
    path = tmp_path / f"broken{suffix}"
    path.write_bytes(b"not a valid document")

    issues, result = analyze_document(str(path))

    assert result["status"] == "failed"
    assert issues[0].issue_type == "document_parse_failed"
    assert issues[0].confidence == "informational"
    assert issues[0].evidence["context"]["error_type"]


def test_unsupported_document_format_reports_without_crashing(tmp_path) -> None:
    path = tmp_path / "notes.txt"
    path.write_text("hello", encoding="utf-8")

    issues, result = analyze_document(str(path))

    assert result["status"] == "unsupported"
    assert issues[0].issue_type == "document_format_unsupported"


def test_media_metadata_reader_exception_reports_failure(tmp_path, monkeypatch) -> None:
    path = tmp_path / "clip.mp3"
    path.write_bytes(b"not really media")

    fake_mutagen = types.SimpleNamespace(File=lambda _source: (_ for _ in ()).throw(ValueError("bad media")))
    monkeypatch.setitem(sys.modules, "mutagen", fake_mutagen)

    issues, result = analyze_media_file(str(path))

    assert result["status"] == "failed"
    assert issues[0].issue_type == "media_metadata_unreadable"
    assert issues[0].confidence == "informational"
    assert issues[0].evidence["context"]["error_type"] == "ValueError"


def test_media_metadata_unavailable_when_library_missing(tmp_path, monkeypatch) -> None:
    path = tmp_path / "clip.mp3"
    path.write_bytes(b"")
    monkeypatch.setitem(sys.modules, "mutagen", None)

    issues, result = analyze_media_file(str(path))

    assert issues == []
    assert result["status"] == "unavailable"
    assert result["capability"]["library"] == "mutagen"


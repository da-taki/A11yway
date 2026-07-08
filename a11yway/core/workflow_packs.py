"""Load deterministic workflow pack templates."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PACKS_DIR = Path(__file__).resolve().parent.parent / "workflow_packs"


def _load_json_file(path: Path) -> dict[str, Any] | None:
    """Return a workflow pack dictionary, or None when it cannot be loaded."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None

    if not isinstance(data, dict):
        return None
    if not isinstance(data.get("pack_id"), str):
        return None
    if not isinstance(data.get("workflows"), list):
        return None
    return data


def list_workflow_packs() -> list[dict[str, Any]]:
    """List all loadable workflow packs."""
    try:
        pack_paths = sorted(PACKS_DIR.glob("*.json"))
    except OSError:
        return []

    packs: list[dict[str, Any]] = []
    for path in pack_paths:
        pack = _load_json_file(path)
        if pack is not None:
            packs.append(pack)
    return packs


def load_workflow_pack(pack_id: str) -> dict[str, Any] | None:
    """Load one workflow pack by id."""
    if not pack_id or any(part in pack_id for part in ("/", "\\", "..")):
        return None

    path = PACKS_DIR / f"{pack_id}.json"
    pack = _load_json_file(path)
    if pack is None:
        return None
    if pack.get("pack_id") != pack_id:
        return None
    return pack


def list_workflows(pack_id: str) -> list[dict[str, Any]]:
    """Return workflow templates for a pack, or an empty list."""
    pack = load_workflow_pack(pack_id)
    if pack is None:
        return []
    workflows = pack.get("workflows", [])
    return [workflow for workflow in workflows if isinstance(workflow, dict)]


def suggest_workflows_from_pack(pack_id: str) -> list[dict[str, Any]]:
    """Return deterministic workflow templates for reviewer task planning."""
    return list_workflows(pack_id)

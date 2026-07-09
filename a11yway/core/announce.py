"""Announce transcript support from Chromium's accessibility tree.

Browser mode already traces where keyboard focus goes. This module asks
Chromium's own accessibility tree, over the Chrome DevTools Protocol (CDP),
what a screen reader would be told at each focus stop: the computed role,
the computed accessible name, and relevant states such as disabled,
required, invalid, checked, and expanded.

This is deterministic browser evidence, not a screen reader simulation.
Real screen readers (NVDA, JAWS, VoiceOver) apply their own rules on top of
the browser tree and can announce things differently. Every capture is
wrapped so a CDP failure degrades to "announcement unavailable" instead of
crashing an audit or inventing a finding. This module never imports
Playwright, so it is always safe to import in static mode.
"""

from __future__ import annotations

from typing import Any


ANNOUNCE_CHECK_NAME = "accessibility_tree_announce"

ANNOUNCE_LIMITATIONS = [
    "The announce transcript comes from Chromium's computed accessibility tree in one browser run.",
    "Real screen readers (NVDA, JAWS, VoiceOver) apply their own rules and can announce things differently.",
]

# AX state properties worth announcing, in the order screen readers
# commonly say them.
_STATE_PROPERTIES = ["disabled", "required", "invalid", "checked", "expanded"]


def open_announce_session(page) -> Any | None:
    """Open a CDP session for accessibility tree lookups, or None on failure."""
    try:
        session = page.context.new_cdp_session(page)
    except Exception:  # noqa: BLE001 - announce data is optional evidence
        return None
    for command in ("DOM.enable", "Accessibility.enable"):
        try:
            session.send(command)
        except Exception:  # noqa: BLE001 - getPartialAXTree can work without enable
            pass
    return session


def _state_words(state: str, value) -> list[str]:
    """Translate one AX property into the words a transcript should show."""
    if state == "checked":
        if value in (True, "true"):
            return ["checked"]
        if value == "mixed":
            return ["partially checked"]
        if value in (False, "false"):
            return ["not checked"]
        return []
    if state == "expanded":
        if value in (True, "true"):
            return ["expanded"]
        if value in (False, "false"):
            return ["collapsed"]
        return []
    if state == "invalid":
        if value in (False, "false", None, ""):
            return []
        return ["invalid"]
    # disabled and required are plain booleans.
    if value in (True, "true"):
        return [state]
    return []


def announcement_from_ax_node(node: dict) -> dict:
    """Map a raw CDP AX node onto the announce fields reports use."""
    role = ((node.get("role") or {}).get("value") or "").strip()
    name = ((node.get("name") or {}).get("value") or "").strip()
    properties = {
        prop.get("name"): (prop.get("value") or {}).get("value")
        for prop in node.get("properties", [])
    }
    states: list[str] = []
    for state in _STATE_PROPERTIES:
        if state in properties:
            states.extend(_state_words(state, properties[state]))
    return {
        "role": role,
        "name": name,
        "states": states,
        "ignored": bool(node.get("ignored")),
    }


def capture_focused_announcement(session) -> dict | None:
    """Return computed role, name, and states for the focused element.

    Resolves the specific focused node (activeElement -> backendNodeId ->
    partial AX tree) instead of diffing full-tree snapshots. Returns None
    whenever the node cannot be resolved, so callers report "announcement
    unavailable" instead of guessing.
    """
    if session is None:
        return None
    object_id = None
    try:
        evaluated = session.send(
            "Runtime.evaluate", {"expression": "document.activeElement"}
        )
        object_id = evaluated.get("result", {}).get("objectId")
        if not object_id:
            return None
        described = session.send("DOM.describeNode", {"objectId": object_id})
        backend_node_id = described.get("node", {}).get("backendNodeId")
        if not backend_node_id:
            return None
        tree = session.send(
            "Accessibility.getPartialAXTree",
            {"backendNodeId": backend_node_id, "fetchRelatives": False},
        )
        nodes = tree.get("nodes", [])
        if not nodes:
            return None
        node = next(
            (n for n in nodes if n.get("backendDOMNodeId") == backend_node_id),
            nodes[0],
        )
        return announcement_from_ax_node(node)
    except Exception:  # noqa: BLE001 - announce data must never break an audit
        return None
    finally:
        if object_id:
            try:
                session.send("Runtime.releaseObject", {"objectId": object_id})
            except Exception:  # noqa: BLE001 - cleanup only
                pass


def format_announcement(announce: dict | None) -> str:
    """Render one focus stop the way the transcript prints it.

    Examples: 'button, (no accessible name)' or 'edit, "Full name", required'.
    """
    if not announce:
        return "(announcement unavailable)"
    parts = [announce.get("role") or "(no role)"]
    name = (announce.get("name") or "").strip()
    parts.append(f'"{name}"' if name else "(no accessible name)")
    parts.extend(announce.get("states", []))
    return ", ".join(parts)


def is_unnamed_announcement(announce: dict | None) -> bool:
    """Return whether captured announce data shows an empty accessible name.

    Unavailable data (None) is not evidence of a missing name, so it never
    produces a finding.
    """
    if not announce:
        return False
    return not (announce.get("name") or "").strip()


def build_announce_transcript(focus_trace: list[dict]) -> list[dict]:
    """Build numbered announce transcript entries from an enriched trace."""
    transcript: list[dict] = []
    for entry in focus_trace:
        announce = entry.get("announce")
        transcript.append(
            {
                "step": entry.get("step"),
                "announcement": entry.get("announcement")
                or format_announcement(announce),
                "role": (announce or {}).get("role"),
                "name": (announce or {}).get("name"),
                "states": (announce or {}).get("states", []),
                "available": announce is not None,
                "unnamed": is_unnamed_announcement(announce),
            }
        )
    return transcript


def trace_has_announce_data(focus_trace: list[dict]) -> bool:
    """Return whether any trace entry carries captured announce data."""
    return any(entry.get("announce") is not None for entry in focus_trace)

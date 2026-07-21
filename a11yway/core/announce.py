















from __future__ import annotations

from typing import Any


ANNOUNCE_CHECK_NAME = "accessibility_tree_announce"

ANNOUNCE_LIMITATIONS = [
    "The announce transcript comes from Chromium's computed accessibility tree in one browser run.",
    "Real screen readers (NVDA, JAWS, VoiceOver) apply their own rules and can announce things differently.",
]



_STATE_PROPERTIES = ["disabled", "required", "invalid", "checked", "expanded"]


def open_announce_session(page) -> Any | None:

    try:
        session = page.context.new_cdp_session(page)
    except Exception:
        return None
    for command in ("DOM.enable", "Accessibility.enable"):
        try:
            session.send(command)
        except Exception:
            pass
    return session


def _state_words(state: str, value) -> list[str]:

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

    if value in (True, "true"):
        return [state]
    return []


def announcement_from_ax_node(node: dict) -> dict:

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
    except Exception:
        return None
    finally:
        if object_id:
            try:
                session.send("Runtime.releaseObject", {"objectId": object_id})
            except Exception:
                pass


def format_announcement(announce: dict | None) -> str:




    if not announce:
        return "(announcement unavailable)"
    parts = [announce.get("role") or "(no role)"]
    name = (announce.get("name") or "").strip()
    parts.append(f'"{name}"' if name else "(no accessible name)")
    parts.extend(announce.get("states", []))
    return ", ".join(parts)


def is_unnamed_announcement(announce: dict | None) -> bool:





    if not announce:
        return False
    return not (announce.get("name") or "").strip()


def build_announce_transcript(focus_trace: list[dict]) -> list[dict]:

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

    return any(entry.get("announce") is not None for entry in focus_trace)

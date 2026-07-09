"""Generate visual proof artifacts from browser focus traces."""

from __future__ import annotations

from html import escape
from pathlib import Path
from typing import Any


VISUAL_PROOF_LIMITATIONS = [
    "Focus overlay shows observed Tab stops in this browser run.",
    "It does not represent every assistive technology experience.",
]


def _clean_path(path: str | Path) -> str:
    """Return a stable report path string."""
    return Path(path).as_posix()


def _legend_transcript_lines(focus_points: list[dict[str, Any]]) -> list[str]:
    """Render the announce transcript inside the overlay legend.

    Returns no lines when no focus point carries announce data, so overlays
    from runs without accessibility tree access stay unchanged.
    """
    announced = [point for point in focus_points if point.get("announcement")]
    if not announced:
        return []
    lines = [
        "<h3>Announce Transcript</h3>",
        '<p class="muted">Computed by Chromium\'s accessibility tree for each numbered focus stop. '
        "Real screen readers (NVDA, JAWS, VoiceOver) can announce things differently.</p>",
        "<ol>",
    ]
    for point in focus_points:
        announcement = point.get("announcement") or "(announcement unavailable)"
        lines.append(f"<li>{escape(str(announcement))}</li>")
    lines.append("</ol>")
    return lines


def build_focus_overlay_html(
    screenshot_path: str | Path,
    focus_points: list[dict[str, Any]],
    source: str = "",
    viewport: dict[str, Any] | None = None,
) -> str:
    """Build an HTML focus-path overlay using CSS over a screenshot."""
    screenshot_name = Path(screenshot_path).name
    viewport_text = ""
    if viewport:
        width = viewport.get("width")
        height = viewport.get("height")
        if width and height:
            viewport_text = f"Viewport observed: {width} x {height} CSS pixels."

    lines = [
        "<!doctype html>",
        '<html lang="en">',
        "<head>",
        '<meta charset="utf-8">',
        "<title>A11yway Focus Path Overlay</title>",
        "<style>",
        "body { margin: 0; font-family: system-ui, sans-serif; color: #172033; background: #f5f7fb; }",
        "header { padding: 1rem 1.25rem; background: #ffffff; border-bottom: 1px solid #d8deea; }",
        "main { padding: 1rem; }",
        ".frame { position: relative; display: inline-block; background: #ffffff; box-shadow: 0 2px 16px rgba(23, 32, 51, 0.16); }",
        ".frame img { display: block; max-width: none; }",
        ".marker { position: absolute; min-width: 1.6rem; height: 1.6rem; padding: 0 0.35rem; border-radius: 999px; border: 3px solid #ffffff; background: #b42318; color: #ffffff; font-weight: 700; font-size: 0.85rem; line-height: 1.6rem; text-align: center; box-shadow: 0 0 0 3px rgba(180, 35, 24, 0.45); transform: translate(-50%, -50%); }",
        ".box { position: absolute; border: 3px solid #b42318; background: rgba(180, 35, 24, 0.08); pointer-events: none; }",
        ".legend { max-width: 54rem; margin: 0 0 1rem; padding: 0.8rem 1rem; background: #ffffff; border: 1px solid #d8deea; }",
        ".muted { color: #526071; }",
        "</style>",
        "</head>",
        "<body>",
        "<header>",
        "<h1>A11yway Focus Path Overlay</h1>",
        f"<p>Source: {escape(source)}</p>" if source else "",
        "</header>",
        "<main>",
        '<section class="legend" aria-labelledby="legend-title">',
        '<h2 id="legend-title">Legend</h2>',
        "<p>Marker numbers show the Tab order observed by A11yway during this browser run. "
        "Hover a marker to see its announced role and name.</p>",
        '<p class="muted">This is a browser observation, not a full screen-reader simulation or accessibility certification.</p>',
        f'<p class="muted">{escape(viewport_text)}</p>' if viewport_text else "",
        *_legend_transcript_lines(focus_points),
        "</section>",
        '<div class="frame">',
        f'<img src="{escape(screenshot_name)}" alt="Full-page screenshot used for focus path overlay">',
    ]

    for point in focus_points:
        step = point.get("step", "")
        x = point.get("x")
        y = point.get("y")
        width = point.get("width")
        height = point.get("height")
        if x is None or y is None:
            continue

        label_parts = [
            f"Step {step}",
            str(point.get("announcement") or ""),
            str(point.get("tag") or ""),
            str(point.get("accessible_name_guess") or ""),
            str(point.get("id") or point.get("name") or ""),
        ]
        label = " | ".join(part for part in label_parts if part)

        if width and height:
            lines.append(
                '<div class="box" style="left: {left}px; top: {top}px; width: {width}px; height: {height}px;"></div>'.format(
                    left=float(x),
                    top=float(y),
                    width=float(width),
                    height=float(height),
                )
            )
            marker_x = float(x) + (float(width) / 2)
            marker_y = float(y) + (float(height) / 2)
        else:
            marker_x = float(x)
            marker_y = float(y)

        lines.append(
            '<div class="marker" style="left: {x}px; top: {y}px;" title="{label}" aria-label="{label}">{step}</div>'.format(
                x=marker_x,
                y=marker_y,
                label=escape(label, quote=True),
                step=escape(str(step)),
            )
        )

    lines.extend(["</div>", "</main>", "</body>", "</html>"])
    return "\n".join(line for line in lines if line != "")


def save_focus_overlay_html(
    screenshot_path: str | Path,
    focus_points: list[dict[str, Any]],
    output_path: str | Path,
    source: str = "",
    viewport: dict[str, Any] | None = None,
) -> None:
    """Write a focus path overlay HTML file."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        build_focus_overlay_html(
            screenshot_path,
            focus_points,
            source=source,
            viewport=viewport,
        ),
        encoding="utf-8",
    )


def build_visual_proof_metadata(
    screenshot_path: str | Path,
    focus_overlay_path: str | Path,
    focus_points: list[dict[str, Any]],
    viewport: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return report-safe visual proof metadata without image bytes."""
    return {
        "enabled": True,
        "screenshot_path": _clean_path(screenshot_path),
        "focus_overlay_path": _clean_path(focus_overlay_path),
        "focus_points": focus_points,
        "focus_points_count": len(focus_points),
        "viewport": viewport or {},
        "limitations": list(VISUAL_PROOF_LIMITATIONS),
    }

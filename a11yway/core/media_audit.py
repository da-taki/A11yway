

from __future__ import annotations

from pathlib import Path

from a11yway.core.extended_results import DETERMINISTIC, HEURISTIC, extended_issue, module_result
from a11yway.core.html_module_utils import attr, parse_elements, selector_for, visible_text
from a11yway.models.issue import AccessibilityIssue


MEDIA_LIMITATIONS = [
    "Media checks inspect HTML and metadata evidence; they do not decode audio tracks by default.",
    "Missing audio description is not inferred from video presence alone.",
    "Muted decorative background video is review evidence, not an automatic caption failure.",
]

MEDIA_EXTENSIONS = {".mp3", ".wav", ".m4a", ".aac", ".ogg", ".mp4", ".mov", ".webm", ".m4v"}


def analyze_media(html: str, source: str) -> tuple[list[AccessibilityIssue], dict]:
    issues: list[AccessibilityIssue] = []
    elements = parse_elements(html)
    tracks_by_parent = {}
    for track in [e for e in elements if e["tag"] == "track"]:
        kind = attr(track, "kind").lower() or "subtitles"
        tracks_by_parent.setdefault(kind, []).append(track)
        if kind in {"captions", "subtitles"} and not attr(track, "srclang"):
            issues.append(
                extended_issue(
                    module="media",
                    check_id="caption_language",
                    title="Caption track is missing language metadata",
                    issue_type="media_caption_language_missing",
                    severity="medium",
                    source=source,
                    selector=selector_for(track),
                    observed="Track element has no srclang attribute.",
                    expected="Caption and subtitle tracks should identify their language.",
                    manual="Verify the captions are meaningful and use the declared language.",
                    evidence_type=HEURISTIC,
                    snippet=track.get("snippet", ""),
                )
            )
    has_transcript_link = any("transcript" in visible_text(e).lower() or "transcript" in attr(e, "href").lower() for e in elements if e["tag"] == "a")
    for media in [e for e in elements if e["tag"] in {"audio", "video"}]:
        tag = media["tag"]
        attrs = media.get("attrs", {})
        controls = "controls" in attrs
        autoplay = "autoplay" in attrs
        muted = "muted" in attrs or attr(media, "aria-hidden").lower() == "true"
        loop = "loop" in attrs
        if autoplay and not controls and not muted:
            issues.append(
                extended_issue(
                    module="media",
                    check_id="autoplay_control",
                    title="Media may start automatically without user control",
                    issue_type="media_autoplay_without_control",
                    severity="high",
                    source=source,
                    selector=selector_for(media),
                    observed=f"{tag} has autoplay without controls or muted state.",
                    expected="Provide controls and avoid automatic audio, or ensure autoplay media is muted/decorative.",
                    manual="Load the page and verify whether meaningful audio/video starts for more than three seconds.",
                    evidence_type=HEURISTIC,
                    snippet=media.get("snippet", ""),
                )
            )
        if tag == "video" and not tracks_by_parent.get("captions") and not muted:
            issues.append(
                extended_issue(
                    module="media",
                    check_id="captions_track",
                    title="Video has no caption track in markup",
                    issue_type="media_caption_track_missing",
                    severity="medium",
                    source=source,
                    selector=selector_for(media),
                    observed="Video is not clearly decorative/muted and no caption track was found.",
                    expected="Provide captions when video contains meaningful audio.",
                    manual="Confirm whether the video has meaningful speech or audio before treating this as a failure.",
                    evidence_type=HEURISTIC,
                    snippet=media.get("snippet", ""),
                )
            )
        if tag in {"audio", "video"} and not has_transcript_link and not muted:
            issues.append(
                extended_issue(
                    module="media",
                    check_id="transcript_relationship",
                    title="Media has no nearby transcript relationship",
                    issue_type="media_transcript_not_found",
                    severity="low",
                    source=source,
                    selector=selector_for(media),
                    observed="No link or text mentioning a transcript was found in the page.",
                    expected="Provide a meaningful transcript relationship for media with meaningful audio.",
                    manual="Verify whether a transcript exists elsewhere and is clearly associated with this media.",
                    evidence_type=HEURISTIC,
                    snippet=media.get("snippet", ""),
                )
            )
        if autoplay and loop and muted and not controls:
            issues.append(
                extended_issue(
                    module="media",
                    check_id="decorative_background_video",
                    title="Muted looping background video should be confirmed decorative",
                    issue_type="media_decorative_background_review",
                    severity="low",
                    source=source,
                    selector=selector_for(media),
                    observed="Muted autoplay looping video without controls appears background/decorative.",
                    expected="Ensure decorative video is hidden from assistive tech or has an accessible alternative if meaningful.",
                    manual="Confirm the video does not convey essential information.",
                    evidence_type=HEURISTIC,
                    confidence="needs_review",
                    snippet=media.get("snippet", ""),
                )
            )
    for image in [e for e in elements if e["tag"] == "img"]:
        src = attr(image, "src").lower()
        if src.endswith(".gif"):
            issues.append(
                extended_issue(
                    module="media",
                    check_id="animated_gif_review",
                    title="Animated GIF should be reviewed separately from video",
                    issue_type="media_animated_gif_review",
                    severity="low",
                    source=source,
                    selector=selector_for(image),
                    observed="Image source appears to be a GIF.",
                    expected="Review animation, pause/stop support, flashing risk, and alternative text.",
                    manual="Confirm whether the GIF is animated and whether users can pause or avoid it.",
                    evidence_type=HEURISTIC,
                    snippet=image.get("snippet", ""),
                )
            )
    return issues, module_result("media", "html_media_accessibility", issues, limitations=MEDIA_LIMITATIONS).to_json()


def analyze_media_file(source: str) -> tuple[list[AccessibilityIssue], dict]:

    issues: list[AccessibilityIssue] = []
    path = Path(source)
    if path.suffix.lower() not in MEDIA_EXTENSIONS:
        issue = extended_issue(
            module="media",
            check_id="media_file_format",
            title="Media file format is not supported",
            issue_type="media_file_format_unsupported",
            severity="low",
            source=source,
            observed=path.suffix or "(no extension)",
            expected="Use a common audio/video file or inspect embedded HTML media.",
            manual="Verify the media in a player with captions/transcripts/audio-description controls.",
            evidence_type=HEURISTIC,
            confidence="informational",
        )
        return [issue], module_result("media", "local_media_metadata", [issue], status="unsupported", limitations=MEDIA_LIMITATIONS).to_json()
    try:
        import mutagen
    except ImportError:
        return issues, module_result(
            "media",
            "local_media_metadata",
            issues,
            status="unavailable",
            limitations=[
                "Local media metadata checks require the optional mutagen package or an external media inspector.",
                *MEDIA_LIMITATIONS,
            ],
            capability={"status": "unavailable", "library": "mutagen"},
        ).to_json()
    try:
        media = mutagen.File(source)
    except Exception as error:
        issue = extended_issue(
            module="media",
            check_id="media_metadata_read_error",
            title="Media metadata reader failed",
            issue_type="media_metadata_unreadable",
            severity="low",
            source=source,
            observed=str(error),
            expected="Use a valid media file or inspect it with a dedicated media accessibility workflow.",
            manual="Open the media in a player and verify captions, transcripts, controls, and audio-description needs.",
            evidence_type=HEURISTIC,
            confidence="informational",
            context={"error_type": type(error).__name__},
        )
        return [issue], module_result(
            "media",
            "local_media_metadata",
            [issue],
            status="failed",
            limitations=MEDIA_LIMITATIONS,
        ).to_json()
    artifacts = {"path": source, "file_type": path.suffix.lower(), "metadata_available": media is not None}
    if media is None:
        issues.append(
            extended_issue(
                module="media",
                check_id="media_metadata_unreadable",
                title="Media metadata could not be read",
                issue_type="media_metadata_unreadable",
                severity="low",
                source=source,
                observed="mutagen returned no metadata object.",
                expected="Use a supported media file or inspect manually.",
                manual="Open the media in a player and verify captions, transcripts, controls, and audio-description needs.",
                evidence_type=HEURISTIC,
            )
        )
    else:
        info = getattr(media, "info", None)
        duration = getattr(info, "length", None)
        artifacts["duration_seconds"] = duration
        if duration and duration > 3:
            issues.append(
                extended_issue(
                    module="media",
                    check_id="media_alternative_review",
                    title="Local media longer than three seconds needs alternatives review",
                    issue_type="media_local_alternatives_review",
                    severity="low",
                    source=source,
                    observed=f"Duration is approximately {duration:.1f} seconds.",
                    expected="Review captions, transcript, controls, and audio-description needs based on media content.",
                    manual="Do not infer missing captions or audio description from duration alone; review the actual media.",
                    evidence_type=DETERMINISTIC,
                    detection_source="mutagen",
                )
            )
    return issues, module_result("media", "local_media_metadata", issues, artifacts=artifacts, limitations=MEDIA_LIMITATIONS).to_json()

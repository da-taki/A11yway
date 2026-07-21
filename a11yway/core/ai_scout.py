






from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable


SYSTEM_PROMPT = (
    "You are AI Scout for A11yway. You help review deterministic accessibility "
    "audit summaries. Your job is to suggest possible user-facing barriers for "
    "human review. You must not claim compliance, legal risk, confirmed failures, "
    "or screen-reader behavior. Treat your output as suggest-only. Use careful "
    "language."
)

DEFAULT_MODEL = "llama-3.3-70b-versatile"
DEFAULT_MODE = "suggest_only"
MAX_AI_SCOUT_FINDINGS = 25
ALLOWED_CONFIDENCE = {"AI-only", "AI plus deterministic support", "unclear"}
AI_SCOUT_LIMITATIONS = [
    "AI Scout findings are suggestions and need human review.",
    "AI Scout output is not a confirmed accessibility finding.",
    "AI Scout does not determine legal compliance, WCAG compliance, or screen-reader behavior.",
]
BANNED_TERMS = [
    "confirmed",
    "violation",
    "non-compliant",
    "illegal",
    "lawsuit",
    "guaranteed",
    "WCAG compliant",
    "screen reader confirmed",
]
REPLACEMENTS = {
    "confirmed": "needs human review",
    "violation": "possible issue",
    "non-compliant": "may need review",
    "illegal": "not assessed",
    "lawsuit": "not assessed",
    "guaranteed": "suggested",
    "WCAG compliant": "not assessed for full WCAG compliance",
    "screen reader confirmed": "not assessed with a screen reader",
}


@dataclass
class AIScoutConfig:


    enabled: bool = False
    mode: str = DEFAULT_MODE
    model: str = DEFAULT_MODEL
    api_key: str = ""
    require_permission_notice: bool = True


def _truthy(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}


def _read_dotenv(path: str | Path = ".env") -> dict[str, str]:

    env_path = Path(path)
    values: dict[str, str] = {}
    if not env_path.exists():
        return values

    try:
        lines = env_path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return values

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def load_ai_scout_config(
    environ: dict[str, str] | None = None,
    dotenv_path: str | Path = ".env",
) -> AIScoutConfig:

    env = dict(environ or os.environ)
    dotenv = _read_dotenv(dotenv_path)

    def get(name: str, default: str = "") -> str:
        if name in env:
            return env[name]
        return dotenv.get(name) or default

    return AIScoutConfig(
        enabled=_truthy(get("A11YWAY_AI_SCOUT_ENABLED")),
        mode=get("A11YWAY_AI_SCOUT_MODE", DEFAULT_MODE),
        model=get("GROQ_MODEL", DEFAULT_MODEL),
        api_key=get("GROQ_API_KEY"),
        require_permission_notice=_truthy(
            get("A11YWAY_REQUIRE_PERMISSION_NOTICE", "true")
        ),
    )


def redact_secrets(value: Any, secrets: list[str] | None = None) -> Any:

    secret_values = [secret for secret in (secrets or []) if secret]
    if isinstance(value, str):
        redacted = value
        for secret in secret_values:
            redacted = redacted.replace(secret, "[REDACTED]")
        return redacted
    if isinstance(value, list):
        return [redact_secrets(item, secret_values) for item in value]
    if isinstance(value, dict):
        return {
            key: redact_secrets(item, secret_values)
            for key, item in value.items()
            if key.lower() not in {"api_key", "groq_api_key"}
        }
    return value


def _base_result(config: AIScoutConfig) -> dict:
    return {
        "enabled": bool(config.enabled),
        "mode": DEFAULT_MODE,
        "model": config.model or DEFAULT_MODEL,
        "status": "unavailable",
        "summary": "",
        "ai_suggested_observations": [],
        "outreach_notes": [],
        "limitations": list(AI_SCOUT_LIMITATIONS),
    }


def unavailable_result(reason: str, config: AIScoutConfig | None = None) -> dict:

    cfg = config or AIScoutConfig()
    result = _base_result(cfg)
    result["status"] = "unavailable" if not cfg.enabled else "failed"
    result["summary"] = f"AI Scout did not produce suggestions: {reason}"
    result["reason"] = reason
    return result


def _truncate(value: str, limit: int = 500) -> str:
    compact = " ".join(str(value or "").split())
    if len(compact) <= limit:
        return compact
    return compact[: limit - 3] + "..."


def _issue_summary(issue: dict) -> dict:
    evidence = issue.get("evidence", {})
    if not isinstance(evidence, dict):
        evidence = {"description": str(evidence)}
    return {
        "issue_type": issue.get("issue_type", ""),
        "severity": issue.get("severity", ""),
        "message": _truncate(issue.get("message", ""), 220),
        "evidence": {
            "detected_in": evidence.get("detected_in", ""),
            "reason": _truncate(evidence.get("reason", ""), 260),
            "snippet": _truncate(evidence.get("snippet", ""), 260),
            "tag": evidence.get("tag", ""),
            "id": evidence.get("id", ""),
            "name": evidence.get("name", ""),
            "text": _truncate(evidence.get("text", ""), 120),
            "step": evidence.get("step") or evidence.get("step_id", ""),
        },
    }


def _severity_rank(issue: dict) -> int:

    severity = str(issue.get("severity", "") or "").strip().lower()
    return {"high": 0, "medium": 1, "low": 2}.get(severity, 3)


def _evidence_group_rank(issue: dict) -> int:






    evidence = issue.get("evidence", {})
    if not isinstance(evidence, dict):
        return 4

    detected_in = str(evidence.get("detected_in", "") or "").strip().lower()
    issue_type = str(issue.get("issue_type", "") or "").strip().lower()
    agent_name = str(issue.get("agent_name", "") or "").strip().lower()

    if detected_in == "axe_core" or issue_type.startswith("axe_"):
        return 0
    if (
        detected_in == "browser_interaction"
        or "accessibility_tree" in detected_in
        or "announce" in issue_type
        or "keyboard" in agent_name
    ):
        return 1
    if detected_in == "browser_dom":
        return 2
    if detected_in == "low_vision" or "low vision" in agent_name:
        return 3
    return 4


def select_ai_scout_findings(
    issues: list[dict],
    limit: int = MAX_AI_SCOUT_FINDINGS,
) -> list[dict]:

    indexed = list(enumerate(issues or []))
    indexed.sort(
        key=lambda item: (
            _evidence_group_rank(item[1]),
            _severity_rank(item[1]),
            item[0],
        )
    )
    return [issue for _index, issue in indexed[:limit]]


def build_ai_scout_payload(
    report: dict,
    target_name: str = "",
    workflow_tested: str = "",
    outreach_tone: str = "",
    workflow_pack: str = "",
) -> dict:

    issues = select_ai_scout_findings(report.get("issues", []))
    browser = report.get("browser") or {}
    focus_trace = browser.get("focus_trace", [])[:12]
    low_vision = report.get("low_vision") or {}
    visual = report.get("visual_proof") or {}
    execution = report.get("task_execution") or {}
    source = report.get("source", {})

    return {
        "target_name": target_name,
        "url_tested": source.get("input") or report.get("source_file", ""),
        "final_url": source.get("final_url", ""),
        "workflow_tested": workflow_tested,
        "workflow_pack": workflow_pack,
        "outreach_tone": outreach_tone,
        "task_result": {
            "completed": execution.get("completed"),
            "blocked_at_step": execution.get("blocked_at_step"),
            "steps_passed": execution.get("steps_passed"),
            "steps_total": execution.get("steps_total"),
        },
        "deterministic_summary": report.get("summary", {}),
        "deterministic_findings": [_issue_summary(issue) for issue in issues],
        "focus_path_summary": [
            {
                "step": entry.get("step"),
                "tag": entry.get("tag"),
                "accessible_name_guess": _truncate(
                    entry.get("accessible_name_guess", ""), 120
                ),
                "text": _truncate(entry.get("text", ""), 120),
                "href": _truncate(entry.get("href", ""), 160),
            }
            for entry in focus_trace
        ],
        "screenshot_paths": {
            "screenshot": visual.get("screenshot_path", ""),
            "focus_overlay": visual.get("focus_overlay_path", ""),
        },
        "low_vision_findings": {
            "success": low_vision.get("success"),
            "contrast_sample_count": low_vision.get("contrast_sample_count"),
            "zoom_reflow": low_vision.get("zoom_reflow", {}),
            "focus_visibility": low_vision.get("focus_visibility", {}),
        },
        "report_metadata": {
            "tool": report.get("tool", "A11yway"),
            "version": report.get("version", ""),
            "limitations": report.get("limitations", []),
        },
    }


def _user_prompt(payload: dict) -> str:
    schema = {
        "enabled": True,
        "mode": "suggest_only",
        "model": "model name",
        "status": "ok",
        "summary": "short careful summary",
        "ai_suggested_observations": [
            {
                "observation": "possible barrier wording",
                "why_it_may_matter": "careful user impact wording",
                "related_deterministic_evidence": "deterministic support or none",
                "human_review_needed": True,
                "confidence": "AI-only",
            }
        ],
        "outreach_notes": ["respectful email note"],
        "limitations": list(AI_SCOUT_LIMITATIONS),
    }
    return (
        "Review this deterministic A11yway audit summary and return only valid JSON. "
        "Use suggest-only language. Do not use banned claims such as confirmed, "
        "violation, non-compliant, illegal, lawsuit, guaranteed, WCAG compliant, "
        "or screen reader confirmed. Use only these confidence labels: AI-only, "
        "AI plus deterministic support, unclear.\n\n"
        f"Required JSON shape:\n{json.dumps(schema, indent=2)}\n\n"
        f"Audit summary:\n{json.dumps(payload, indent=2)}"
    )


def _extract_message_content(response: Any) -> str:
    try:
        return response.choices[0].message.content
    except (AttributeError, IndexError, TypeError):
        return ""


def _extract_json_object(text: str) -> dict:
    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        pass

    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("Groq response did not contain a JSON object.")
    parsed = json.loads(text[start : end + 1])
    if not isinstance(parsed, dict):
        raise ValueError("Groq response JSON was not an object.")
    return parsed


def _sanitize_text(value: str) -> str:
    sanitized = value
    for term in BANNED_TERMS:
        replacement = REPLACEMENTS[term]
        sanitized = re.sub(
            re.escape(term),
            replacement,
            sanitized,
            flags=re.IGNORECASE,
        )
    return sanitized


def _sanitize_output(value: Any) -> Any:
    if isinstance(value, str):
        return _sanitize_text(value)
    if isinstance(value, list):
        return [_sanitize_output(item) for item in value]
    if isinstance(value, dict):
        return {key: _sanitize_output(item) for key, item in value.items()}
    return value


def normalize_ai_scout_output(parsed: dict, config: AIScoutConfig) -> dict:

    safe = _sanitize_output(parsed)
    result = _base_result(config)
    result["enabled"] = True
    result["status"] = "ok"
    result["summary"] = str(safe.get("summary") or "")
    result["outreach_notes"] = [
        str(note) for note in safe.get("outreach_notes", []) if str(note).strip()
    ][:5]

    observations = []
    for item in safe.get("ai_suggested_observations", []):
        if not isinstance(item, dict):
            continue
        confidence = str(item.get("confidence") or "unclear")
        if confidence not in ALLOWED_CONFIDENCE:
            confidence = "unclear"
        observations.append(
            {
                "observation": str(item.get("observation") or ""),
                "why_it_may_matter": str(item.get("why_it_may_matter") or ""),
                "related_deterministic_evidence": str(
                    item.get("related_deterministic_evidence") or ""
                ),
                "human_review_needed": True,
                "confidence": confidence,
            }
        )
    result["ai_suggested_observations"] = observations[:8]

    limitations = safe.get("limitations", [])
    if isinstance(limitations, list):
        result["limitations"] = list(dict.fromkeys(list(AI_SCOUT_LIMITATIONS) + limitations))
    return result


def _default_client_factory(api_key: str) -> Any:
    from groq import Groq

    return Groq(api_key=api_key)


def run_ai_scout(
    report: dict,
    target_name: str = "",
    workflow_tested: str = "",
    outreach_tone: str = "",
    workflow_pack: str = "",
    config: AIScoutConfig | None = None,
    client_factory: Callable[[str], Any] | None = None,
) -> dict:

    cfg = config or load_ai_scout_config()
    if not cfg.enabled:
        return unavailable_result("AI Scout is disabled by configuration.", cfg)
    if cfg.mode != DEFAULT_MODE:
        return unavailable_result("AI Scout only supports suggest_only mode.", cfg)
    if not cfg.api_key:
        return unavailable_result("GROQ_API_KEY is not configured.", cfg)

    payload = build_ai_scout_payload(
        report,
        target_name=target_name,
        workflow_tested=workflow_tested,
        outreach_tone=outreach_tone,
        workflow_pack=workflow_pack,
    )

    try:
        factory = client_factory or _default_client_factory
        client = factory(cfg.api_key)
        response = client.chat.completions.create(
            model=cfg.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": _user_prompt(payload)},
            ],
            temperature=0.2,
            response_format={"type": "json_object"},
        )
        content = redact_secrets(_extract_message_content(response), [cfg.api_key])
        parsed = _extract_json_object(content)
        result = normalize_ai_scout_output(parsed, cfg)
    except ImportError:
        return unavailable_result(
            "The official groq Python package is not installed.", cfg
        )
    except Exception as error:
        return unavailable_result(
            redact_secrets(str(error).strip().splitlines()[0], [cfg.api_key])
            or "Groq request failed.",
            cfg,
        )

    return redact_secrets(result, [cfg.api_key])


def build_ai_scout_markdown(result: dict) -> str:

    lines = [
        "### What the AI Found",
        "",
        f"- Status: {result.get('status', '')}",
        f"- Mode: {result.get('mode', DEFAULT_MODE)}",
        f"- Model: {result.get('model', '')}",
        "",
    ]
    if result.get("status") != "ok":
        reason = result.get("reason") or result.get("summary") or "unknown reason"
        lines.extend(
            [
                (
                    "AI Scout was enabled, but no AI summary was produced because: "
                    f"{reason}. No AI findings should be inferred from this run."
                ),
                "",
            ]
        )
    else:
        if result.get("summary"):
            lines.extend([str(result["summary"]), ""])
        observations = result.get("ai_suggested_observations", [])
        if observations:
            for index, item in enumerate(observations, start=1):
                lines.extend(
                    [
                        f"{index}. AI-suggested observation: {item.get('observation', '')}",
                        f"   Related evidence, if any: {item.get('related_deterministic_evidence', '')}",
                        f"   Human review needed: {str(item.get('human_review_needed', True)).lower()}",
                        f"   Confidence: {item.get('confidence', 'unclear')}",
                        "",
                    ]
                )
        else:
            lines.extend(["AI Scout did not return specific observations.", ""])
        notes = result.get("outreach_notes", [])
        if notes:
            lines.extend(["#### Outreach Notes", ""])
            lines.extend(f"- {note}" for note in notes)
            lines.append("")

    lines.extend(["#### AI Scout Limitations", ""])
    lines.extend(f"- {limitation}" for limitation in result.get("limitations", []))
    lines.append("")
    return "\n".join(lines)


def save_ai_scout_outputs(result: dict, base_path: str | Path) -> dict[str, str]:

    base = Path(base_path)
    base.parent.mkdir(parents=True, exist_ok=True)
    json_path = base.with_name(f"{base.name}_ai_scout.json")
    markdown_path = base.with_name(f"{base.name}_ai_scout.md")
    json_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    markdown_path.write_text(build_ai_scout_markdown(result), encoding="utf-8")
    return {
        "json": json_path.as_posix(),
        "markdown": markdown_path.as_posix(),
    }

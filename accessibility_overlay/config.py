import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional


@dataclass(frozen=True)
class CueDefinition:
    event: str
    label: str
    color: str
    severity: str
    duration_ms: int


@dataclass(frozen=True)
class OverlaySettings:
    host: str
    port: int
    overlay_title: str
    transparency: float
    cue_history_size: int
    ue_log_path: Optional[str]
    ue_log_prefix: str
    ue_log_poll_interval_ms: int


@dataclass(frozen=True)
class OverlayConfig:
    settings: OverlaySettings
    cues: Dict[str, CueDefinition]


DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "cues.json"


def load_config(path: Path = DEFAULT_CONFIG_PATH) -> OverlayConfig:
    raw = json.loads(path.read_text(encoding="utf-8"))
    settings_raw = raw["settings"]
    ue_log_path = settings_raw.get("ue_log_path") or None
    settings = OverlaySettings(
        host=settings_raw.get("host", "127.0.0.1"),
        port=int(settings_raw.get("port", 9900)),
        overlay_title=settings_raw.get("overlay_title", "UE5 Accessibility Cues"),
        transparency=float(settings_raw.get("transparency", 0.88)),
        cue_history_size=int(settings_raw.get("cue_history_size", 6)),
        ue_log_path=ue_log_path,
        ue_log_prefix=settings_raw.get("ue_log_prefix", "ACCESSIBILITY_CUE"),
        ue_log_poll_interval_ms=int(settings_raw.get("ue_log_poll_interval_ms", 250)),
    )

    cues: Dict[str, CueDefinition] = {}
    for cue in raw.get("cues", []):
        definition = CueDefinition(
            event=cue["event"],
            label=cue.get("label", cue["event"]),
            color=cue.get("color", "#00E5FF"),
            severity=cue.get("severity", "info"),
            duration_ms=int(cue.get("duration_ms", 2500)),
        )
        cues[definition.event] = definition
    return OverlayConfig(settings=settings, cues=cues)


def load_event_override(raw_event: dict, config: OverlayConfig) -> CueDefinition:
    event_name = raw_event.get("event", "unknown")
    base = config.cues.get(event_name)
    if base is None:
        base = CueDefinition(
            event=event_name,
            label=event_name.replace("_", " ").title(),
            color="#FFCA28",
            severity="info",
            duration_ms=2500,
        )

    return CueDefinition(
        event=event_name,
        label=raw_event.get("label", base.label),
        color=raw_event.get("color", base.color),
        severity=raw_event.get("severity", base.severity),
        duration_ms=int(raw_event.get("duration_ms", base.duration_ms)),
    )


def summarize_cues(cues: List[CueDefinition]) -> str:
    return " | ".join(f"{cue.label} ({cue.severity})" for cue in cues)

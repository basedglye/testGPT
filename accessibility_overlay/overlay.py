import json
import socket
import threading
import time
import tkinter as tk
from datetime import datetime
from pathlib import Path
from queue import Queue
from typing import Dict, List

from accessibility_overlay.config import CueDefinition, OverlayConfig, load_event_override
from accessibility_overlay.cues import Cue


class OverlayApp:
    def __init__(self, config: OverlayConfig) -> None:
        self.config = config
        self.queue: Queue[Cue] = Queue()
        self.active_cues: List[Cue] = []
        self.root = tk.Tk()
        self.root.title(config.settings.overlay_title)
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", config.settings.transparency)
        self.root.configure(bg="#0B0F14")
        self.root.geometry("420x360+40+40")

        self.header = tk.Label(
            self.root,
            text="Accessibility Cues",
            bg="#0B0F14",
            fg="#E0E7FF",
            font=("Helvetica", 16, "bold"),
        )
        self.header.pack(fill="x", padx=12, pady=(10, 6))

        self.cue_frame = tk.Frame(self.root, bg="#0B0F14")
        self.cue_frame.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        self.footer = tk.Label(
            self.root,
            text=f"Listening on {config.settings.host}:{config.settings.port}",
            bg="#0B0F14",
            fg="#94A3B8",
            font=("Helvetica", 10),
        )
        self.footer.pack(fill="x", padx=12, pady=(0, 10))

        self._labels: List[tk.Label] = []
        self._render_cues()

    def _render_cues(self) -> None:
        for label in self._labels:
            label.destroy()
        self._labels.clear()

        if not self.active_cues:
            placeholder = tk.Label(
                self.cue_frame,
                text="No cues yet. Waiting for UE5 events...",
                bg="#0B0F14",
                fg="#64748B",
                font=("Helvetica", 12),
                anchor="w",
                justify="left",
            )
            placeholder.pack(fill="x", pady=6)
            self._labels.append(placeholder)
            return

        for cue in self.active_cues:
            label = tk.Label(
                self.cue_frame,
                text=f"{cue.label}  ·  {cue.severity.upper()}" + (f"  ·  {cue.source}" if cue.source else ""),
                bg="#111827",
                fg=cue.color,
                font=("Helvetica", 12, "bold"),
                anchor="w",
                justify="left",
                padx=10,
                pady=8,
            )
            label.pack(fill="x", pady=4)
            self._labels.append(label)

    def _drain_queue(self) -> None:
        updated = False
        while not self.queue.empty():
            cue = self.queue.get_nowait()
            self.active_cues.insert(0, cue)
            updated = True

        if updated:
            self.active_cues = self.active_cues[: self.config.settings.cue_history_size]

        now = datetime.utcnow()
        before = len(self.active_cues)
        self.active_cues = [cue for cue in self.active_cues if not cue.is_expired(now)]
        if updated or before != len(self.active_cues):
            self._render_cues()
        self.root.after(200, self._drain_queue)

    def _listen(self) -> None:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.bind((self.config.settings.host, self.config.settings.port))
            while True:
                payload, address = sock.recvfrom(8192)
                event = json.loads(payload.decode("utf-8"))
                self._enqueue_event(event, source=f"{address[0]}:{address[1]}")

    def _listen_ue_log(self, log_path: Path) -> None:
        prefix = self.config.settings.ue_log_prefix
        poll_delay = self.config.settings.ue_log_poll_interval_ms / 1000
        while True:
            if not log_path.exists():
                time.sleep(poll_delay)
                continue
            with log_path.open("r", encoding="utf-8", errors="ignore") as handle:
                handle.seek(0, 2)
                while True:
                    line = handle.readline()
                    if not line:
                        time.sleep(poll_delay)
                        continue
                    if prefix not in line:
                        continue
                    payload = line.split(prefix, 1)[1].strip()
                    try:
                        event = json.loads(payload)
                    except json.JSONDecodeError:
                        continue
                    self._enqueue_event(event, source="UE5 Log")

    def _enqueue_event(self, event: dict, source: str) -> None:
        cue_def = load_event_override(event, self.config)
        cue = Cue(
            label=cue_def.label,
            color=cue_def.color,
            severity=cue_def.severity,
            duration_ms=cue_def.duration_ms,
            created_at=datetime.utcnow(),
            source=source,
        )
        self.queue.put(cue)

    def start(self) -> None:
        listener = threading.Thread(target=self._listen, daemon=True)
        listener.start()
        if self.config.settings.ue_log_path:
            log_path = Path(self.config.settings.ue_log_path)
            log_listener = threading.Thread(
                target=self._listen_ue_log, args=(log_path,), daemon=True
            )
            log_listener.start()
        self.root.after(200, self._drain_queue)
        self.root.mainloop()


def cue_from_definition(definition: CueDefinition) -> Dict[str, str]:
    return {
        "event": definition.event,
        "label": definition.label,
        "color": definition.color,
        "severity": definition.severity,
        "duration_ms": str(definition.duration_ms),
    }

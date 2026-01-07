# UE5 External Accessibility Overlay

This repository provides a lightweight, external accessibility overlay that displays visual cues for audio/visual impaired players in Unreal Engine 5 experiences. The overlay listens for JSON events over UDP, renders them in a high-contrast UI, and expires cues automatically after a configured duration.

## Features

- **External overlay** (no UE5 plugin required) that sits on top of the game window.
- **Configurable cues** via `config/cues.json`.
- **Network-friendly** JSON over UDP so it can run on the same machine or a companion device.
- **Cue aging** to prevent clutter.

## Quick start

Use Terminal (macOS/Linux) or PowerShell (Windows). No extra dependencies are required beyond Python 3 with Tkinter (included with most standard Python installs).

```bash
python run_overlay.py
```

In a second terminal, send sample cues:

```bash
python examples/send_test_event.py
```

## Install Python 3 + Tkinter

Choose the option that matches your OS:

- **Windows**: Install Python 3 from https://www.python.org/downloads/ (Tkinter is included by default). Ensure `python` is on your PATH.
- **macOS**: Install Python 3 from https://www.python.org/downloads/ (includes Tkinter) or via Homebrew: `brew install python`.
- **Linux (Debian/Ubuntu)**:

```bash
sudo apt-get update
sudo apt-get install python3 python3-tk
```

## Cue format

The overlay expects a JSON payload with the following fields:

```json
{
  "event": "enemy_alert",
  "label": "Enemy Alert",
  "color": "#F97316",
  "severity": "warning",
  "duration_ms": 3000
}
```

- `event` is required and should match a cue in `config/cues.json`.
- Any missing fields are filled in from the config defaults.

## UE5 integration options

You can emit cues from UE5 using a simple UDP sender in Blueprints or C++:

1. **Build the JSON payload** with `event`, `label`, `severity`, `color`, `duration_ms`.
2. **Send over UDP** to `127.0.0.1:9900` (or the host/port in `config/cues.json`).
3. Trigger a cue for important audio-only information, such as:
   - footsteps nearby
   - door opening
   - enemy alert / danger
   - objective update

If you prefer to hook directly into UE5 without sockets, enable log-based cues:

1. Set `ue_log_path` in `config/cues.json` to the UE5 log file (for example, `Saved/Logs/MyGame.log`).
2. Emit a log line that starts with the prefix (default: `ACCESSIBILITY_CUE`) followed by JSON.

Example C++ snippet:

```cpp
UE_LOG(LogTemp, Log, TEXT("ACCESSIBILITY_CUE {\"event\":\"enemy_alert\",\"severity\":\"warning\"}"));
```

## Configuration

Edit `config/cues.json` to customize the overlay title, transparency, cue definitions, or log listener settings (set `ue_log_path` to enable UE5 log listening).

## Notes

- Tkinter is included with most Python distributions.
- The overlay is intentionally minimal to keep latency low and reduce CPU usage.

import json
import socket
import time


EVENTS = [
    {
        "event": "footsteps_nearby",
        "label": "Footsteps Nearby",
        "severity": "info",
        "color": "#60A5FA",
        "duration_ms": 2200,
    },
    {
        "event": "door_open",
        "label": "Door Opened",
        "severity": "info",
        "color": "#A3E635",
        "duration_ms": 2000,
    },
    {
        "event": "enemy_alert",
        "label": "Enemy Alert",
        "severity": "warning",
        "color": "#F97316",
        "duration_ms": 3000,
    },
    {
        "event": "critical_damage",
        "label": "Critical Damage",
        "severity": "critical",
        "color": "#F43F5E",
        "duration_ms": 3200,
    },
]


def main() -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        for event in EVENTS:
            sock.sendto(json.dumps(event).encode("utf-8"), ("127.0.0.1", 9900))
            time.sleep(0.75)


if __name__ == "__main__":
    main()

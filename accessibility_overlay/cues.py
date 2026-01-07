from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Cue:
    label: str
    color: str
    severity: str
    duration_ms: int
    created_at: datetime
    source: Optional[str] = None

    def is_expired(self, now: datetime) -> bool:
        return (now - self.created_at).total_seconds() * 1000 >= self.duration_ms

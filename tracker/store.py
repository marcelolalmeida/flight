from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from .models import Flight

DATA = Path(__file__).resolve().parent.parent / "data"


class Store:
    """history.jsonl = append-only price observations.
    state.json = {watch_name: {"flights": {key: price}, "best_alerted": float|None, "failures": {source: n}}}"""

    def __init__(self, data_dir: Path = DATA):
        self.dir = data_dir
        self.dir.mkdir(parents=True, exist_ok=True)
        self.history_path = self.dir / "history.jsonl"
        self.state_path = self.dir / "state.json"
        self.state: dict = (
            json.loads(self.state_path.read_text()) if self.state_path.exists() else {}
        )

    def watch_state(self, name: str) -> dict:
        return self.state.setdefault(name, {"flights": {}, "best_alerted": None, "failures": {}})

    def record(self, watch_name: str, flights: list[Flight]) -> None:
        ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
        with self.history_path.open("a") as f:
            for fl in flights:
                f.write(json.dumps({"ts": ts, "watch": watch_name, **fl.to_dict()}) + "\n")
        ws = self.watch_state(watch_name)
        for fl in flights:
            ws["flights"][fl.key] = fl.price

    def save(self) -> None:
        self.state_path.write_text(json.dumps(self.state, indent=2, sort_keys=True))

    def read_history(self) -> list[dict]:
        if not self.history_path.exists():
            return []
        return [json.loads(l) for l in self.history_path.read_text().splitlines() if l.strip()]

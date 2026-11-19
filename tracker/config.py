from __future__ import annotations

from datetime import date
from pathlib import Path

import yaml

from .models import Watch

ROOT = Path(__file__).resolve().parent.parent


def _d(v) -> date:
    return v if isinstance(v, date) else date.fromisoformat(str(v))


def load_watches(path: Path | None = None) -> list[Watch]:
    path = path or ROOT / "config.yaml"
    raw = yaml.safe_load(path.read_text()) or {}
    watches = []
    for w in raw.get("watches", []):
        watches.append(Watch(
            name=w["name"],
            origin=w["origin"].upper(),
            dest=w["dest"].upper(),
            date_from=_d(w["date_from"]),
            date_to=_d(w.get("date_to", w["date_from"])),
            airlines=[a.upper() for a in w.get("airlines", ["GOL", "LATAM"])],
            max_price=w.get("max_price"),
            drop_pct=w.get("drop_pct"),
            notify_new_flights=w.get("notify_new_flights", True),
            adults=w.get("adults", 1),
            currency=w.get("currency", "BRL"),
        ))
    return watches

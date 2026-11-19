from __future__ import annotations

from dataclasses import dataclass

from .models import Flight, Watch


@dataclass
class Alert:
    kind: str      # "new" | "drop" | "target"
    flight: Flight
    detail: str


def find_alerts(watch: Watch, flights: list[Flight], ws: dict) -> list[Alert]:
    """Compare fresh flights to last-seen state. Mutates ws['best_alerted'] for dedupe."""
    alerts: list[Alert] = []
    seen: dict[str, float] = ws.get("flights", {})
    first_run = not seen  # don't spam every flight as "new" on the first run

    for fl in flights:
        prev = seen.get(fl.key)
        if prev is None:
            if watch.notify_new_flights and not first_run:
                alerts.append(Alert("new", fl, f"New flight released at {fl.currency} {fl.price:.0f}"))
        elif watch.drop_pct and prev > 0 and (prev - fl.price) / prev * 100 >= watch.drop_pct:
            alerts.append(Alert("drop", fl, f"Dropped {prev:.0f} -> {fl.price:.0f} ({(prev - fl.price) / prev * 100:.0f}%)"))

    if watch.max_price is not None and flights:
        cheapest = min(flights, key=lambda f: f.price)
        best = ws.get("best_alerted")
        if cheapest.price <= watch.max_price and (best is None or cheapest.price < best):
            alerts.append(Alert("target", cheapest, f"At/below your target of {watch.max_price:.0f}"))
            ws["best_alerted"] = cheapest.price
        elif cheapest.price > watch.max_price:
            ws["best_alerted"] = None  # price went back up; re-arm

    return alerts

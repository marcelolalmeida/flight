from __future__ import annotations

from .config import load_watches
from .diff import find_alerts
from .notify import format_alert, send_telegram
from .store import Store

FAILURE_ALERT_AFTER = 3


def get_sources(names: list[str]):
    # GOL and LATAM block automated browsers (Akamai "Access Denied"/403), so fares
    # come from Google Flights via SearchApi.io; one query covers both airlines.
    from .sources.searchapi import SearchApiSource
    return [SearchApiSource()]


def run(dry_run: bool = False, sources_factory=get_sources, store: Store | None = None) -> int:
    store = store or Store()
    total_alerts = 0
    for watch in load_watches():
        ws = store.watch_state(watch.name)
        flights = []
        for src in sources_factory(watch.airlines):
            try:
                found = src.fetch(watch)
                ws["failures"][src.airline] = 0
                flights += found
                print(f"[{watch.name}] {src.airline}: {len(found)} flights")
            except Exception as e:  # fail soft per source
                n = ws["failures"].get(src.airline, 0) + 1
                ws["failures"][src.airline] = n
                print(f"[{watch.name}] {src.airline} FAILED ({n}x): {e}")
                if n == FAILURE_ALERT_AFTER and not dry_run:
                    send_telegram(f"⚠️ {src.airline} source has failed {n} runs in a row for '{watch.name}': {e}")
        if not flights:
            continue
        alerts = find_alerts(watch, flights, ws)
        for a in alerts:
            msg = format_alert(watch, a)
            print(msg)
            if not dry_run:
                send_telegram(msg)
        total_alerts += len(alerts)
        if not dry_run:
            store.record(watch.name, flights)
    if not dry_run:
        store.save()
    return total_alerts

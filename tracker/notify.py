from __future__ import annotations

import os

import requests

from .diff import Alert
from .models import Watch

ICONS = {"new": "🆕", "drop": "📉", "target": "🎯"}


def format_alert(watch: Watch, a: Alert) -> str:
    f = a.flight
    return (
        f"{ICONS[a.kind]} {watch.name}: {f.airline} {f.flight_no}\n"
        f"{f.origin} → {f.dest}  {f.dep.replace('T', ' ')}\n"
        f"{f.currency} {f.price:.0f} — {a.detail}"
        + (f"\nVerify: {f.url}" if f.url else "")
    )


def send_telegram(text: str) -> bool:
    token, chat = os.environ.get("TELEGRAM_BOT_TOKEN"), os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat:
        print("[notify] Telegram not configured; message was:\n" + text)
        return False
    r = requests.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        json={"chat_id": chat, "text": text},
        timeout=20,
    )
    r.raise_for_status()
    return True

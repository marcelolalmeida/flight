from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import date


@dataclass(frozen=True)
class Flight:
    airline: str          # "GOL" | "LATAM"
    flight_no: str
    origin: str
    dest: str
    dep: str              # ISO datetime, e.g. 2026-12-20T08:15
    price: float
    currency: str = "BRL"
    url: str = ""         # link to verify the fare yourself (not part of identity)

    @property
    def key(self) -> str:
        """Stable identity of a flight (price excluded)."""
        return f"{self.airline}|{self.flight_no}|{self.origin}|{self.dest}|{self.dep}"

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Watch:
    name: str
    origin: str
    dest: str
    date_from: date
    date_to: date
    airlines: list[str] = field(default_factory=lambda: ["GOL", "LATAM"])
    max_price: float | None = None       # alert when cheapest <= this
    drop_pct: float | None = None        # alert when price falls >= this % vs last run
    notify_new_flights: bool = True
    adults: int = 1
    currency: str = "BRL"

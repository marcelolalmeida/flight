from __future__ import annotations

import os
from datetime import timedelta

import requests

from ..models import Flight, Watch

# Substrings matched (case-insensitive) against the airline name Google Flights returns.
AIRLINE_MATCH = {"GOL": "gol", "LATAM": "latam"}


def parse(data: dict, watch: Watch) -> list[Flight]:
    """Turn a SearchApi.io google_flights response into Flights (pure; tested on a real response)."""
    url = data.get("search_metadata", {}).get("request_url", "")
    wanted = [AIRLINE_MATCH[a] for a in watch.airlines if a in AIRLINE_MATCH]
    out: list[Flight] = []
    for opt in data.get("best_flights", []) + data.get("other_flights", []):
        legs = opt.get("flights") or []
        price = opt.get("price")
        if not legs or price is None:
            continue
        airline = legs[0].get("airline", "")
        name = next((k for k, m in AIRLINE_MATCH.items() if m in airline.lower()), None)
        if name is None or not any(m in airline.lower() for m in wanted):
            continue
        dep = legs[0]["departure_airport"]
        out.append(Flight(
            airline=name,
            flight_no="+".join(l.get("flight_number", "?").replace(" ", "") for l in legs),
            origin=dep["id"],
            dest=legs[-1]["arrival_airport"]["id"],
            dep=f"{dep['date']}T{dep['time']}",
            price=float(price),
            currency=watch.currency,
            url=url,
        ))
    return out


class SearchApiSource:
    airline = "SEARCHAPI"

    def fetch(self, watch: Watch) -> list[Flight]:
        key = os.environ.get("SEARCHAPI_API_KEY") or os.environ.get("SERPAPI_API_KEY")
        if not key:
            raise RuntimeError("SEARCHAPI_API_KEY not set")
        flights: list[Flight] = []
        day = watch.date_from
        while day <= watch.date_to:
            r = requests.get("https://www.searchapi.io/api/v1/search", params={
                "engine": "google_flights",
                "flight_type": "one_way",
                "departure_id": watch.origin,
                "arrival_id": watch.dest,
                "outbound_date": day.isoformat(),
                "currency": watch.currency,
                "hl": "pt",
                "api_key": key,
            }, timeout=90)
            if r.status_code in (401, 403):
                raise RuntimeError(f"SearchApi rejected the API key (HTTP {r.status_code})")
            r.raise_for_status()
            data = r.json()
            if data.get("error"):
                raise RuntimeError(str(data["error"])[:200])
            flights += parse(data, watch)
            day += timedelta(days=1)
        return flights

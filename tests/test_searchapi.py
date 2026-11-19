import json
from datetime import date
from pathlib import Path

from tracker.models import Watch
from tracker.sources.searchapi import parse

FIX = Path(__file__).parent / "fixtures" / "searchapi_bps_gru.json"  # real captured response


def test_parse_real_response_filters_airlines():
    data = json.loads(FIX.read_text())
    w = Watch("t", "BPS", "GRU", date(2027, 1, 3), date(2027, 1, 3))
    fl = parse(data, w)
    # 5 options in the capture: 4 LATAM + 1 Azul (excluded)
    assert len(fl) == 4 and {f.airline for f in fl} == {"LATAM"}
    first = fl[0]
    assert (first.flight_no, first.dep, first.price) == ("LA3365", "2027-01-03T04:45", 3748.0)
    assert fl[3].flight_no == "LA3709+LA3585" and fl[3].price == 3838.0
    assert first.url.startswith("https://www.google.com/travel/flights")


def test_airline_filter_respected():
    data = json.loads(FIX.read_text())
    w = Watch("t", "BPS", "GRU", date(2027, 1, 3), date(2027, 1, 3), airlines=["GOL"])
    assert parse(data, w) == []

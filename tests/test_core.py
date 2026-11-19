from datetime import date

from tracker.diff import find_alerts
from tracker.models import Flight, Watch
from tracker.store import Store


def W(**kw):
    base = dict(name="t", origin="GRU", dest="GIG", date_from=date(2026, 12, 20), date_to=date(2026, 12, 27))
    base.update(kw)
    return Watch(**base)


def F(no="1000", price=500.0, dep="2026-12-20T08:00"):
    return Flight("GOL", no, "GRU", "GIG", dep, price)


def test_first_run_no_new_spam_but_target_fires():
    ws = {"flights": {}, "best_alerted": None, "failures": {}}
    alerts = find_alerts(W(max_price=400), [F(price=350), F("2", 600)], ws)
    assert [a.kind for a in alerts] == ["target"]


def test_new_flight_and_drop():
    ws = {"flights": {F().key: 500.0}, "best_alerted": None, "failures": {}}
    alerts = find_alerts(W(drop_pct=10), [F(price=400), F("2", 300)], ws)
    assert sorted(a.kind for a in alerts) == ["drop", "new"]


def test_target_dedupe_and_rearm():
    ws = {"flights": {F().key: 500.0}, "best_alerted": None, "failures": {}}
    w = W(max_price=400)
    assert len(find_alerts(w, [F(price=390)], ws)) == 1
    assert find_alerts(w, [F(price=390)], ws) == []        # same low, no repeat
    assert len(find_alerts(w, [F(price=380)], ws)) == 1    # new low
    find_alerts(w, [F(price=450)], ws)                      # back above -> re-arm
    assert len(find_alerts(w, [F(price=390)], ws)) == 1


def test_store_roundtrip(tmp_path):
    s = Store(tmp_path)
    s.record("t", [F(price=123)])
    s.save()
    s2 = Store(tmp_path)
    assert s2.watch_state("t")["flights"][F().key] == 123
    assert len(s2.read_history()) == 1

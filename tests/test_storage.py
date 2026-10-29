from tracker.parse import Product
from tracker.storage import PriceStore


def product(price):
    return Product("1", "Test EDP 100ml", "/test", price, 20000)


def test_first_snapshot_is_all_new(tmp_path):
    store = PriceStore(str(tmp_path / "p.db"))
    changes = store.record([product(10000)], "2026-01-01T00:00:00")
    assert [c.is_new for c in changes] == [True]


def test_unchanged_price_is_not_reported(tmp_path):
    store = PriceStore(str(tmp_path / "p.db"))
    store.record([product(10000)], "2026-01-01T00:00:00")
    assert store.record([product(10000)], "2026-01-02T00:00:00") == []


def test_price_drop_reports_delta(tmp_path):
    store = PriceStore(str(tmp_path / "p.db"))
    store.record([product(10000)], "2026-01-01T00:00:00")
    (change,) = store.record([product(8000)], "2026-01-02T00:00:00")
    assert change.previous == 10000
    assert round(change.delta_pct) == -20


def test_csv_has_latest_price_only(tmp_path):
    store = PriceStore(str(tmp_path / "p.db"))
    store.record([product(10000)], "2026-01-01T00:00:00")
    store.record([product(8000)], "2026-01-02T00:00:00")
    out = tmp_path / "p.csv"
    assert store.export_latest_csv(str(out)) == 1
    assert "8000" in out.read_text(encoding="utf-8")

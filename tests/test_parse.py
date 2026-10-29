from pathlib import Path

from tracker.parse import parse_clp, parse_listing

FIXTURE = Path(__file__).parent / "fixtures" / "listing.html"


def test_parse_clp():
    assert parse_clp("$105.900") == 105900
    assert parse_clp(" ") is None


def test_parse_listing():
    products = parse_listing(FIXTURE.read_text(encoding="utf-8"))
    assert len(products) == 4
    first = products[0]
    assert first.name.startswith("Amber Romance")
    assert first.price == 12900
    assert first.list_price == 21900
    assert first.url.startswith("/")

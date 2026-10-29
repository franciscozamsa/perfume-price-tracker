import argparse
from pathlib import Path

from .fetch import Blocked, PoliteFetcher
from .parse import parse_listing
from .storage import PriceStore

BASE_URL = "https://www.parisperfumes.cl"


def scrape(fetcher: PoliteFetcher, listing: str, max_pages: int):
    seen = {}
    for page in range(1, max_pages + 1):
        try:
            html = fetcher.get(f"/{listing}?page={page}")
        except Blocked as e:
            print(e)
            break
        found = parse_listing(html)
        if not found:
            break
        for p in found:
            seen[p.product_id] = p
    return list(seen.values())


def main(argv=None):
    ap = argparse.ArgumentParser(description="Track perfume prices from a public listing page.")
    ap.add_argument("--listing", default="ofertas", help="listing path on the site (default: ofertas)")
    ap.add_argument("--max-pages", type=int, default=3)
    ap.add_argument("--db", default="prices.db")
    ap.add_argument("--csv", default="prices.csv")
    ap.add_argument("--delay", type=float, default=2.0, help="seconds between requests")
    args = ap.parse_args(argv)

    fetcher = PoliteFetcher(BASE_URL, delay=args.delay, cache_dir=Path(".cache"))
    products = scrape(fetcher, args.listing, args.max_pages)
    store = PriceStore(args.db)
    changes = store.record(products)
    n = store.export_latest_csv(args.csv)

    print(f"{len(products)} products scraped, {len(changes)} new or changed, {n} rows in {args.csv}")
    for c in changes:
        if c.is_new:
            print(f"  NEW   {c.product.name}: ${c.product.price:,}")
        else:
            print(f"  {c.delta_pct:+.1f}%  {c.product.name}: ${c.previous:,} -> ${c.product.price:,}")


if __name__ == "__main__":
    main()

# perfume-price-tracker

Tracks perfume prices from a public retail listing, stores every snapshot in SQLite and reports what changed since the last run.

I have built scrapers before to pull retail data automatically. This is a clean public rebuild of that work, so it can be read and run by anyone: it does not contain code or data from earlier projects.

## What it does

- Scrapes a public listing page of [parisperfumes.cl](https://www.parisperfumes.cl) (default: `/ofertas`), following `?page=N`.
- Extracts product id, name, URL, current price and list price (CLP).
- Appends each run to `prices.db` and prints new products and price changes with the percentage delta.
- Exports the latest price per product to CSV. See [`sample/prices.csv`](sample/prices.csv).

## Being a good citizen

- Reads `robots.txt` first and refuses any URL it disallows.
- Minimum 2 s between requests, small page limit by default, identifiable User-Agent.
- On-disk cache (1 h) so repeated runs do not hit the site again.
- Only public listing pages. No login, no cart, no search endpoints.

Check a site's terms before pointing this at it. The site adapter is one small file (`tracker/parse.py` selectors plus `BASE_URL` in `tracker/cli.py`); adapting to another store means changing those.

## Run it

```
python -m venv .venv
.venv/Scripts/pip install -r requirements.txt     # Linux/macOS: .venv/bin/pip
.venv/Scripts/python -m tracker.cli --max-pages 2
.venv/Scripts/python -m pytest
```

First run reports every product as `NEW`. Later runs report only changes:

```
3 products scraped, 2 new or changed, 3 rows in prices.csv
  -20.0%  Example EDP 100ml: $10,000 -> $8,000
  NEW   Another EDP 50ml: $15,900
```

## Limits

- Depends on the site's current HTML. If the theme changes, the selectors in `tracker/parse.py` need updating; the offline fixture test in `tests/` will fail first.
- Listing pages only: no per-product details, stock levels or variants.
- Prices are shown to the buyer in CLP and stored as integers.

MIT license.

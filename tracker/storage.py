import csv
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from .parse import Product

SCHEMA = """
CREATE TABLE IF NOT EXISTS prices (
    product_id TEXT NOT NULL,
    name TEXT NOT NULL,
    url TEXT NOT NULL,
    price INTEGER NOT NULL,
    list_price INTEGER,
    scraped_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS prices_by_product ON prices (product_id, scraped_at);
"""


@dataclass(frozen=True)
class Change:
    product: Product
    previous: Optional[int]

    @property
    def is_new(self) -> bool:
        return self.previous is None

    @property
    def delta_pct(self) -> Optional[float]:
        if self.previous is None:
            return None
        return (self.product.price - self.previous) / self.previous * 100


class PriceStore:
    def __init__(self, path: str):
        self.db = sqlite3.connect(path)
        self.db.executescript(SCHEMA)

    def record(self, products: list[Product], scraped_at: str | None = None) -> list[Change]:
        """Store a snapshot and return the products that are new or changed price since the last one."""
        scraped_at = scraped_at or datetime.now(timezone.utc).isoformat(timespec="seconds")
        changes = []
        for p in products:
            previous = self._last_price(p.product_id)
            if previous != p.price:
                changes.append(Change(p, previous))
            self.db.execute(
                "INSERT INTO prices VALUES (?, ?, ?, ?, ?, ?)",
                (p.product_id, p.name, p.url, p.price, p.list_price, scraped_at),
            )
        self.db.commit()
        return changes

    def _last_price(self, product_id: str) -> Optional[int]:
        row = self.db.execute(
            "SELECT price FROM prices WHERE product_id = ? ORDER BY scraped_at DESC, rowid DESC LIMIT 1",
            (product_id,),
        ).fetchone()
        return row[0] if row else None

    def export_latest_csv(self, path: str) -> int:
        rows = self.db.execute(
            """
            SELECT product_id, name, url, price, list_price, scraped_at FROM prices p
            WHERE rowid = (SELECT rowid FROM prices WHERE product_id = p.product_id
                           ORDER BY scraped_at DESC, rowid DESC LIMIT 1)
            ORDER BY name
            """
        ).fetchall()
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["product_id", "name", "url", "price_clp", "list_price_clp", "scraped_at"])
            writer.writerows(rows)
        return len(rows)

import re
from dataclasses import dataclass
from typing import Optional

from bs4 import BeautifulSoup


@dataclass(frozen=True)
class Product:
    product_id: str
    name: str
    url: str
    price: int
    list_price: Optional[int]


def parse_clp(text: str) -> Optional[int]:
    digits = re.sub(r"[^\d]", "", text or "")
    return int(digits) if digits else None


def parse_listing(html: str) -> list[Product]:
    soup = BeautifulSoup(html, "html.parser")
    products = []
    for card in soup.select("article.product-block"):
        quick = card.select_one("[data-product-id][data-product-name]")
        if quick is None:
            continue
        price = parse_clp(_text(card, ".product-block__price--new"))
        if price is None:
            continue
        products.append(
            Product(
                product_id=quick["data-product-id"],
                name=quick["data-product-name"].strip(),
                url=quick.get("data-product-url", ""),
                price=price,
                list_price=parse_clp(_text(card, ".product-block__price--old")),
            )
        )
    return products


def _text(card, selector: str) -> str:
    node = card.select_one(selector)
    return node.get_text(strip=True) if node else ""

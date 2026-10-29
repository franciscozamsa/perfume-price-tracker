import hashlib
import time
from pathlib import Path
from urllib import robotparser
from urllib.parse import urljoin

import requests

USER_AGENT = "perfume-price-tracker/0.1 (+https://github.com/franciscozamsa/perfume-price-tracker)"


class Blocked(Exception):
    pass


class PoliteFetcher:
    """GET pages only if robots.txt allows it, with a minimum delay between requests and an on-disk cache."""

    def __init__(self, base_url: str, delay: float = 2.0, cache_dir: Path | None = None, cache_ttl: float = 3600):
        self.base_url = base_url
        self.delay = delay
        self.cache_dir = cache_dir
        self.cache_ttl = cache_ttl
        self._last_request = 0.0
        self._session = requests.Session()
        self._session.headers["User-Agent"] = USER_AGENT
        self._robots = robotparser.RobotFileParser()
        self._robots.parse(self._get(urljoin(base_url, "/robots.txt")).splitlines())

    def _get(self, url: str) -> str:
        wait = self.delay - (time.monotonic() - self._last_request)
        if wait > 0:
            time.sleep(wait)
        response = self._session.get(url, timeout=20)
        self._last_request = time.monotonic()
        response.raise_for_status()
        response.encoding = "utf-8"
        return response.text

    def get(self, path: str) -> str:
        url = urljoin(self.base_url, path)
        if not self._robots.can_fetch(USER_AGENT, url):
            raise Blocked(f"robots.txt disallows {url}")
        cached = self._read_cache(url)
        if cached is not None:
            return cached
        text = self._get(url)
        self._write_cache(url, text)
        return text

    def _cache_file(self, url: str) -> Path | None:
        if self.cache_dir is None:
            return None
        return self.cache_dir / (hashlib.sha1(url.encode()).hexdigest() + ".html")

    def _read_cache(self, url: str) -> str | None:
        f = self._cache_file(url)
        if f and f.exists() and time.time() - f.stat().st_mtime < self.cache_ttl:
            return f.read_text(encoding="utf-8")
        return None

    def _write_cache(self, url: str, text: str) -> None:
        f = self._cache_file(url)
        if f:
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text(text, encoding="utf-8")

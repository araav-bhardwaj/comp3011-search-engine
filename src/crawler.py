"""Web crawler for quotes.toscrape.com."""

from __future__ import annotations

import time
from collections import deque
from dataclasses import dataclass
from typing import Callable
from urllib.parse import urldefrag, urljoin, urlparse

import requests
from bs4 import BeautifulSoup


@dataclass(frozen=True)
class CrawledPage:
    url: str
    html: str


class CrawlerError(RuntimeError):
    pass


class WebCrawler:
    def __init__(
        self,
        start_url: str = "https://quotes.toscrape.com/",
        politeness_delay: float = 6.0,
        timeout: float = 10.0,
        max_pages: int | None = None,
        sleep_func: Callable[[float], None] = time.sleep,
        session: requests.Session | None = None,
    ) -> None:
        self.start_url = self._normalise_url(start_url)
        self.allowed_netloc = urlparse(self.start_url).netloc
        self.politeness_delay = politeness_delay
        self.timeout = timeout
        self.max_pages = max_pages
        self.sleep_func = sleep_func
        self.session = session or requests.Session()
        self.session.headers.update(
            {"User-Agent": "COMP3011-SearchTool/1.0 educational crawler"}
        )

    def crawl(self) -> list[CrawledPage]:
        queue: deque[str] = deque([self.start_url])
        seen: set[str] = {self.start_url}
        pages: list[CrawledPage] = []
        last_request_time: float | None = None

        while queue:
            if self.max_pages is not None and len(pages) >= self.max_pages:
                break

            url = queue.popleft()

            if last_request_time is not None:
                elapsed = time.monotonic() - last_request_time
                wait_time = max(0.0, self.politeness_delay - elapsed)
                if wait_time > 0:
                    print(f"Waiting {wait_time:.1f}s to respect politeness window...")
                    self.sleep_func(wait_time)

            print(f"Crawling page {len(pages) + 1}: {url}")

            try:
                response = self.session.get(url, timeout=self.timeout)
                last_request_time = time.monotonic()
                response.raise_for_status()
            except requests.RequestException as exc:
                print(f"Warning: failed to fetch {url}: {exc}")
                continue

            html = response.text
            pages.append(CrawledPage(url=url, html=html))

            for link in self._extract_links(url, html):
                if link not in seen:
                    seen.add(link)
                    queue.append(link)

        if not pages:
            raise CrawlerError("No pages were crawled. Check your network connection.")

        return pages

    def _extract_links(self, base_url: str, html: str) -> list[str]:
        soup = BeautifulSoup(html, "html.parser")
        links: list[str] = []

        next_link = soup.select_one("li.next a")
        if next_link and next_link.get("href"):
            absolute = self._normalise_url(urljoin(base_url, next_link["href"]))
            parsed = urlparse(absolute)

            if parsed.scheme in {"http", "https"} and parsed.netloc == self.allowed_netloc:
                links.append(absolute)

        return links

    @staticmethod
    def _normalise_url(url: str) -> str:
        clean_url, _fragment = urldefrag(url)
        parsed = urlparse(clean_url)
        if not parsed.path:
            clean_url = clean_url.rstrip("/") + "/"
        return clean_url

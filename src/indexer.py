"""Inverted index construction and persistence."""

from __future__ import annotations

import json
import math
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup

from .crawler import CrawledPage

WORD_RE = re.compile(r"[a-z0-9]+(?:'[a-z0-9]+)?", re.IGNORECASE)


@dataclass
class Posting:
    """Statistics for one term in one document."""

    frequency: int = 0
    positions: list[int] = field(default_factory=list)


@dataclass
class InvertedIndex:
    """Search index mapping words to per-page posting lists."""

    index: dict[str, dict[str, Posting]] = field(default_factory=dict)
    documents: dict[str, dict[str, Any]] = field(default_factory=dict)

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "documents": self.documents,
            "index": {
                term: {
                    url: {"frequency": posting.frequency, "positions": posting.positions}
                    for url, posting in postings.items()
                }
                for term, postings in self.index.items()
            },
        }

    @classmethod
    def from_json_dict(cls, data: dict[str, Any]) -> "InvertedIndex":
        index: dict[str, dict[str, Posting]] = {}
        for term, postings in data.get("index", {}).items():
            index[term] = {
                url: Posting(
                    frequency=int(stats.get("frequency", 0)),
                    positions=list(stats.get("positions", [])),
                )
                for url, stats in postings.items()
            }
        return cls(index=index, documents=data.get("documents", {}))


class Indexer:
    """Builds, saves, and loads an inverted index."""

    def build(self, pages: list[CrawledPage]) -> InvertedIndex:
        postings: dict[str, dict[str, Posting]] = defaultdict(dict)
        documents: dict[str, dict[str, Any]] = {}

        for page in pages:
            text = self.extract_visible_text(page.html)
            title = self.extract_title(page.html) or page.url
            tokens = self.tokenise(text)
            documents[page.url] = {"title": title, "length": len(tokens)}

            term_positions: dict[str, list[int]] = defaultdict(list)
            for position, token in enumerate(tokens):
                term_positions[token].append(position)

            for term, positions in term_positions.items():
                postings[term][page.url] = Posting(
                    frequency=len(positions), positions=positions
                )

        return InvertedIndex(index=dict(postings), documents=documents)

    @staticmethod
    def extract_visible_text(html: str) -> str:
        """Return readable text, ignoring script/style content."""
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        return soup.get_text(" ", strip=True)

    @staticmethod
    def extract_title(html: str) -> str:
        soup = BeautifulSoup(html, "html.parser")
        if soup.title and soup.title.string:
            return soup.title.string.strip()
        heading = soup.find(["h1", "h2"])
        return heading.get_text(" ", strip=True) if heading else ""

    @staticmethod
    def tokenise(text: str) -> list[str]:
        """Lowercase and split text into searchable word tokens."""
        return [match.group(0).lower() for match in WORD_RE.finditer(text)]

    @staticmethod
    def save(index: InvertedIndex, path: str | Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as file:
            json.dump(index.to_json_dict(), file, indent=2, sort_keys=True)

    @staticmethod
    def load(path: str | Path) -> InvertedIndex:
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(
                f"Index file not found: {path}. Run 'build' before 'load'."
            )
        with path.open("r", encoding="utf-8") as file:
            return InvertedIndex.from_json_dict(json.load(file))

    @staticmethod
    def document_frequencies(index: InvertedIndex) -> dict[str, int]:
        return {term: len(postings) for term, postings in index.index.items()}

    @staticmethod
    def ranked_scores(index: InvertedIndex, terms: list[str]) -> dict[str, float]:
        """Compute simple TF-IDF scores for pages matching every query term."""
        if not terms:
            return {}
        matching_urls = set(index.documents)
        for term in terms:
            matching_urls &= set(index.index.get(term, {}))

        total_docs = max(1, len(index.documents))
        scores: dict[str, float] = Counter()
        for term in terms:
            postings = index.index.get(term, {})
            if not postings:
                return {}
            idf = math.log((1 + total_docs) / (1 + len(postings))) + 1
            for url in matching_urls:
                doc_length = max(1, int(index.documents[url].get("length", 1)))
                tf = postings[url].frequency / doc_length
                scores[url] += tf * idf
        return dict(scores)

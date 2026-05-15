"""Search operations over the inverted index."""

from __future__ import annotations

from dataclasses import dataclass

from .indexer import Indexer, InvertedIndex, Posting


@dataclass(frozen=True)
class SearchResult:
    url: str
    title: str
    score: float


class SearchEngine:
    """Provides print and find commands for an already-built index."""

    def __init__(self, index: InvertedIndex | None = None) -> None:
        self.index = index

    def set_index(self, index: InvertedIndex) -> None:
        self.index = index

    def require_index(self) -> InvertedIndex:
        if self.index is None:
            raise ValueError("No index loaded. Run 'build' or 'load' first.")
        return self.index

    def print_word(self, word: str) -> dict[str, Posting]:
        index = self.require_index()
        terms = Indexer.tokenise(word)
        if len(terms) != 1:
            raise ValueError("print expects exactly one word, e.g. print nonsense")
        return index.index.get(terms[0], {})

    def find(self, query: str) -> list[SearchResult]:
        index = self.require_index()
        terms = Indexer.tokenise(query)
        if not terms:
            raise ValueError("find expects at least one search term, e.g. find good friends")

        scores = Indexer.ranked_scores(index, terms)
        results = [
            SearchResult(
                url=url,
                title=str(index.documents[url].get("title", url)),
                score=score,
            )
            for url, score in scores.items()
        ]
        return sorted(results, key=lambda item: (-item.score, item.url))

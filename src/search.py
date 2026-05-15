"""Search operations over the inverted index."""

from __future__ import annotations

import re
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

        phrase_terms = self._extract_phrase_terms(query)
        if phrase_terms:
            return self._find_phrase(index, phrase_terms)

        terms = Indexer.tokenise(query)
        if not terms:
            raise ValueError("find expects at least one search term, e.g. find good friends")

        return self._ranked_results(index, terms)

    def _ranked_results(
        self,
        index: InvertedIndex,
        terms: list[str],
        allowed_urls: set[str] | None = None,
    ) -> list[SearchResult]:
        scores = Indexer.ranked_scores(index, terms)

        if allowed_urls is not None:
            scores = {url: score for url, score in scores.items() if url in allowed_urls}

        results = [
            SearchResult(
                url=url,
                title=str(index.documents[url].get("title", url)),
                score=score,
            )
            for url, score in scores.items()
        ]
        return sorted(results, key=lambda item: (-item.score, item.url))

    def _extract_phrase_terms(self, query: str) -> list[str]:
        match = re.fullmatch(r'\s*"([^"]+)"\s*', query)
        if not match:
            return []
        terms = Indexer.tokenise(match.group(1))
        if not terms:
            raise ValueError("find expects at least one search term, e.g. find good friends")
        return terms

    def _find_phrase(self, index: InvertedIndex, terms: list[str]) -> list[SearchResult]:
        if len(terms) == 1:
            return self._ranked_results(index, terms)

        candidate_urls = set(index.documents)
        for term in terms:
            candidate_urls &= set(index.index.get(term, {}))

        phrase_urls = {
            url for url in candidate_urls if self._phrase_occurs_in_url(index, terms, url)
        }

        return self._ranked_results(index, terms, phrase_urls)

    @staticmethod
    def _phrase_occurs_in_url(index: InvertedIndex, terms: list[str], url: str) -> bool:
        first_positions = index.index[terms[0]][url].positions
        later_position_sets = [
            set(index.index[term][url].positions)
            for term in terms[1:]
        ]

        for start_position in first_positions:
            if all(
                start_position + offset + 1 in later_position_sets[offset]
                for offset in range(len(later_position_sets))
            ):
                return True

        return False

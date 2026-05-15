import pytest

from src.indexer import InvertedIndex, Posting
from src.search import SearchEngine


@pytest.fixture
def engine():
    index = InvertedIndex(
        documents={
            "page-1": {"title": "Page One", "length": 100},
            "page-2": {"title": "Page Two", "length": 100},
        },
        index={
            "good": {
                "page-1": Posting(frequency=1, positions=[1]),
                "page-2": Posting(frequency=1, positions=[5]),
            },
            "friends": {
                "page-1": Posting(frequency=1, positions=[2]),
                "page-2": Posting(frequency=1, positions=[9]),
            },
        },
    )
    return SearchEngine(index)


def test_print_word_returns_postings(engine):
    postings = engine.print_word("good")

    assert set(postings) == {"page-1", "page-2"}


def test_print_word_rejects_multiple_terms(engine):
    with pytest.raises(ValueError):
        engine.print_word("good friends")


def test_find_returns_ranked_results(engine):
    results = engine.find("good friends")

    assert results[0].url == "page-1"


def test_find_requires_terms(engine):
    with pytest.raises(ValueError):
        engine.find("")


def test_find_requires_loaded_index():
    engine = SearchEngine()

    with pytest.raises(ValueError):
        engine.find("good")


def test_phrase_search_requires_consecutive_positions(engine):
    results = engine.find('"good friends"')

    assert [result.url for result in results] == ["page-1"]


def test_phrase_search_returns_empty_when_terms_not_consecutive(engine):
    results = engine.find('"friends good"')

    assert results == []

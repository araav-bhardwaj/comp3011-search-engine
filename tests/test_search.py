import pytest

from src.crawler import CrawledPage
from src.indexer import Indexer
from src.search import SearchEngine


@pytest.fixture
def engine():
    pages = [
        CrawledPage("https://site/page1", "<title>One</title><p>good friends matter</p>"),
        CrawledPage("https://site/page2", "<title>Two</title><p>good ideas matter</p>"),
        CrawledPage("https://site/page3", "<title>Three</title><p>friends forever</p>"),
    ]
    return SearchEngine(Indexer().build(pages))


def test_find_single_word(engine):
    urls = [result.url for result in engine.find("good")]
    assert urls == ["https://site/page1", "https://site/page2"]


def test_find_multi_word_requires_all_terms(engine):
    urls = [result.url for result in engine.find("good friends")]
    assert urls == ["https://site/page1"]


def test_find_empty_query_is_rejected(engine):
    with pytest.raises(ValueError, match="at least one"):
        engine.find("!!!")


def test_print_nonexistent_word_returns_empty_dict(engine):
    assert engine.print_word("missing") == {}


def test_print_rejects_multiple_words(engine):
    with pytest.raises(ValueError, match="exactly one"):
        engine.print_word("good friends")

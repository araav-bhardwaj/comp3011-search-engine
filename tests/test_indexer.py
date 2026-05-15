from src.crawler import CrawledPage
from src.indexer import Indexer


def test_tokenise_is_case_insensitive_and_handles_apostrophes():
    assert Indexer.tokenise("Good GOOD don't!") == ["good", "good", "don't"]


def test_build_index_stores_frequency_and_positions():
    pages = [CrawledPage("https://example.com/", "<html><title>T</title><p>Good friends good</p></html>")]
    index = Indexer().build(pages)

    posting = index.index["good"]["https://example.com/"]
    assert posting.frequency == 2
    assert posting.positions == [1, 3]  # title token comes first
    assert index.documents["https://example.com/"]["title"] == "T"


def test_save_and_load_round_trip(tmp_path):
    pages = [CrawledPage("https://example.com/", "<p>alpha beta alpha</p>")]
    original = Indexer().build(pages)
    path = tmp_path / "index.json"

    Indexer.save(original, path)
    loaded = Indexer.load(path)

    assert loaded.index["alpha"]["https://example.com/"].frequency == 2
    assert loaded.documents == original.documents

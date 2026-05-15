from src.crawler import WebCrawler


class FakeResponse:
    def __init__(self, text: str, status_code: int = 200):
        self.text = text
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError("HTTP error")


class FakeSession:
    def __init__(self, pages):
        self.pages = pages
        self.headers = {}

    def get(self, url, timeout):
        return FakeResponse(self.pages[url])


def test_crawler_follows_next_pages_only_and_uses_delay():
    pages = {
        "https://quotes.toscrape.com/": """
            <li class="next"><a href="/page/2/">Next</a></li>
            <a href="https://external.example/">external</a>
            <a href="/author/Albert-Einstein">author page ignored</a>
        """,
        "https://quotes.toscrape.com/page/2/": "<p>done</p>",
    }
    delays = []
    crawler = WebCrawler(
        session=FakeSession(pages),
        politeness_delay=6.0,
        sleep_func=delays.append,
    )

    result = crawler.crawl()

    assert [page.url for page in result] == [
        "https://quotes.toscrape.com/",
        "https://quotes.toscrape.com/page/2/",
    ]
    assert round(delays[0], 1) == 6.0


def test_crawler_returns_at_least_start_page():
    pages = {"https://quotes.toscrape.com/": "<html>No next page</html>"}
    crawler = WebCrawler(session=FakeSession(pages), sleep_func=lambda _: None)

    result = crawler.crawl()

    assert len(result) == 1
    assert result[0].url == "https://quotes.toscrape.com/"

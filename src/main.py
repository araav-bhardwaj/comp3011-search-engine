"""Command-line shell for the COMP3011 search engine coursework."""

from __future__ import annotations

import argparse
import cmd
from pathlib import Path

from .crawler import WebCrawler
from .indexer import Indexer
from .search import SearchEngine

DEFAULT_INDEX_PATH = Path("data/index.json")
DEFAULT_START_URL = "https://quotes.toscrape.com/"


class SearchShell(cmd.Cmd):
    intro = "COMP3011 Search Tool. Type help or ? to list commands."
    prompt = "> "

    def __init__(self, index_path: Path, start_url: str, politeness_delay: float) -> None:
        super().__init__()
        self.index_path = index_path
        self.start_url = start_url
        self.politeness_delay = politeness_delay
        self.indexer = Indexer()
        self.engine = SearchEngine()

    def do_build(self, arg: str) -> None:
        """build: crawl the website, build the index, and save it."""
        print(f"Crawling {self.start_url} with {self.politeness_delay:.1f}s politeness delay...")
        crawler = WebCrawler(
            start_url=self.start_url,
            politeness_delay=self.politeness_delay,
        )
        pages = crawler.crawl()
        index = self.indexer.build(pages)
        self.indexer.save(index, self.index_path)
        self.engine.set_index(index)
        print(
            f"Built index for {len(index.documents)} pages and "
            f"{len(index.index)} unique words. Saved to {self.index_path}."
        )

    def do_load(self, arg: str) -> None:
        """load: load the index from disk."""
        try:
            index = self.indexer.load(self.index_path)
        except FileNotFoundError as exc:
            print(exc)
            return
        self.engine.set_index(index)
        print(
            f"Loaded index with {len(index.documents)} pages and "
            f"{len(index.index)} unique words from {self.index_path}."
        )

    def do_print(self, arg: str) -> None:
        """print WORD: print the inverted index entry for WORD."""
        try:
            postings = self.engine.print_word(arg)
        except ValueError as exc:
            print(exc)
            return

        if not postings:
            print(f"No index entry found for '{arg.strip().lower()}'.")
            return

        for url, posting in sorted(postings.items()):
            print(f"{url}")
            print(f"  frequency: {posting.frequency}")
            print(f"  positions:  {posting.positions}")

    def do_find(self, arg: str) -> None:
        """find QUERY: find pages containing every query term."""
        try:
            results = self.engine.find(arg)
        except ValueError as exc:
            print(exc)
            return

        if not results:
            print(f"No pages found for query: {arg!r}")
            return

        for rank, result in enumerate(results, start=1):
            print(f"{rank}. {result.url}")
            print(f"   title: {result.title}")
            print(f"   score: {result.score:.6f}")

    def do_exit(self, arg: str) -> bool:
        """exit: quit the search shell."""
        print("Goodbye.")
        return True

    def do_quit(self, arg: str) -> bool:
        """quit: quit the search shell."""
        return self.do_exit(arg)

    def emptyline(self) -> None:
        # Do nothing on blank lines instead of repeating the previous command.
        return None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="COMP3011 search engine tool")
    parser.add_argument("--index", type=Path, default=DEFAULT_INDEX_PATH)
    parser.add_argument("--url", default=DEFAULT_START_URL)
    parser.add_argument("--delay", type=float, default=6.0)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    SearchShell(args.index, args.url, args.delay).cmdloop()


if __name__ == "__main__":
    main()

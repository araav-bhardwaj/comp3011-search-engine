# COMP3011 Coursework 2: Search Engine Tool

A Python command-line search tool for `https://quotes.toscrape.com/`. The tool crawls the website, builds an inverted index, saves/loads the index, prints posting lists, and finds pages containing single-word or multi-word queries.

## Features

- Crawls only internal pages from the target website.
- Enforces a 6-second politeness window between HTTP requests.
- Builds a case-insensitive inverted index.
- Stores word statistics: frequency and word positions per page.
- Saves and loads the index as `data/index.json`.
- Supports required commands: `build`, `load`, `print`, and `find`.
- Handles edge cases such as empty queries, missing index files, and non-existent words.
- Includes unit tests for crawler, indexer, and search logic.
- Uses simple TF-IDF ranking to order matching results while still returning only pages containing all query terms.

## Project Structure

```text
repository-name/
├── src/
│   ├── __init__.py
│   ├── crawler.py
│   ├── indexer.py
│   ├── search.py
│   └── main.py
├── tests/
│   ├── test_crawler.py
│   ├── test_indexer.py
│   └── test_search.py
├── data/
│   └── index.json          # generated after running build
├── requirements.txt
└── README.md
```

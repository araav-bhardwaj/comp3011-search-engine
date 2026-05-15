# COMP3011 Search Engine Coursework

A Python-based mini search engine developed for the COMP3011 coursework.

The system crawls the Quotes to Scrape website, builds an inverted index, stores positional information, and supports ranked keyword and phrase searching through an interactive command-line interface.

---

# Features

## Web Crawling
- Crawls `https://quotes.toscrape.com/`
- Restricts crawling to internal quote pages only
- Implements a configurable politeness delay (default 6 seconds)
- Uses breadth-first crawling
- Handles invalid requests gracefully

## Inverted Index
- Stores:
  - term frequencies
  - positional information
  - document metadata
- Persists index to JSON

## Search Functionality

### Supported Commands
- `build`
- `load`
- `print <word>`
- `find <query>`
- `find "exact phrase"`

### Ranking
- TF-IDF style scoring
- Multi-word ranked retrieval
- Case-insensitive searching

### Phrase Search
Phrase queries use positional indexing to verify consecutive word matches.

Example:

```text
find "good friends"
```

Only documents containing the exact phrase are returned.

---

# Project Structure

```text
comp3011-search-engine/
│
├── src/
│   ├── crawler.py
│   ├── indexer.py
│   ├── search.py
│   └── main.py
│
├── tests/
│   ├── test_crawler.py
│   ├── test_indexer.py
│   ├── test_search.py
│   └── test_main.py
│
├── data/
│   └── index.json
│
├── requirements.txt
├── pyproject.toml
└── README.md
```

---

# Setup Instructions

## Create Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Running the Search Engine

## Development Mode

```bash
python -m src.main --delay 1
```

## Coursework Demonstration Mode

```bash
python -m src.main --delay 6
```

---

# Example Commands

```text
build
load
print nonsense
find good friends
find "good friends"
find xyznotreal
exit
```

---

# Testing

## Run All Tests

```bash
pytest -q
```

## Run Coverage

```bash
pytest --cov=src --cov-report=term-missing
```

Current coverage:

```text
85%
```

---

# Design Decisions

## Positional Indexing
Each indexed word stores:
- frequency
- positions within the document

This enables:
- phrase search
- proximity search extensions
- ranking improvements

## Phrase Search
Phrase searching checks whether query terms appear consecutively within the same document using positional comparisons.

## Ranking Strategy
Documents are ranked using a TF-IDF-inspired scoring method:
- higher term frequency increases relevance
- terms appearing in fewer documents receive higher weight

---

# Limitations

- Only crawls the Quotes to Scrape website
- No stemming or stop-word removal
- No wildcard search
- No boolean query operators
- No parallel crawling

---

# Future Improvements

Potential future enhancements:
- stemming
- autocomplete
- wildcard search
- boolean retrieval
- PageRank-style ranking
- snippet generation
- web interface

---

# Use of Generative AI

Generative AI tools were used during development to:
- brainstorm architecture ideas
- improve testing coverage
- refine crawler behaviour
- debug implementation issues
- improve documentation quality

All generated code was reviewed, tested, modified, and understood before inclusion.

Several AI-generated solutions required debugging and correction, including:
- crawler over-expansion into non-target pages
- fragile timing assertions in tests
- incorrect fixture usage during phrase-search testing

The final implementation and debugging decisions were performed manually.

---

# Author

Araav Bhardwaj

University of Leeds  
COMP3011 Coursework

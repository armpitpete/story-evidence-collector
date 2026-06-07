# Story Evidence Collector

Story Evidence Collector is a public-source research tool for collecting evidence about a story from allowed web pages.

It is being built step by step from a safe Scrapling parser demo.

## Current status

The current version can:

- fetch public demo pages from `quotes.toscrape.com`
- follow pagination
- extract quote text, author, tags, and source URL
- save structured JSON
- create a run report
- validate the output
- check `robots.txt` before scraping

## Safety rules

This project is for public-source research.

It is not designed to access private, restricted, paid, login-only, or blocked content. It should only fetch pages that are public and allowed, with polite delays and clear reports.

## Planned purpose

A user will enter a story or provide seed URLs.

The tool will:

- check `robots.txt`
- fetch allowed pages politely
- extract page title, text, dates, authors, links, and source URLs
- follow discovered links within safe limits
- save traceable evidence records
- produce a readable research summary

## Planned config

Future versions will support:

```json
{
  "max_pages": 50,
  "max_depth": 2,
  "same_domain_only": true,
  "respect_robots_txt": true,
  "delay_seconds": 1
}
```

## Planned outputs

```text
sources_raw.json
links_found.json
source_report.json
research_summary.md
```

## Current demo outputs

```text
quotes_all_pages_v09.json
scrape_report_v09.json
```

## Install

```powershell
pip install -r requirements.txt
```

## Run current scraper

```powershell
python .\scrape_all_quote_pages_v09.py
```

## Current version table

| Version | Status | Purpose |
|---|---:|---|
| v0.1 | Done | Parser test |
| v0.2 | Done | Scrape one page |
| v0.3 | Done | Save JSON |
| v0.4 | Done | Scrape page 1 and page 2 |
| v0.5 | Done | Follow pagination |
| v0.6 | Done | Safer cleaner scraper |
| v0.7 | Done | Run report |
| v0.8 | Done | Data validation |
| v0.9 | Done | robots.txt check |
| v1.0 | Done | Public-safe project freeze |

## Notes

The current scraper is a learning/demo scraper. The next development step is to replace the quote-demo-specific extraction with configurable seed URLs and general source records.

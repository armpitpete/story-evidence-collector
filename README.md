# Story Evidence Collector

Story Evidence Collector is a public-source research tool for collecting evidence about a story from allowed web pages.

It is being built step by step from a safe Scrapling parser demo.

## Current status

The current version can:

- read seed URLs from `seed_urls.json`
- fetch public seed pages
- extract a general source record from each seed page
- save page title, visible text excerpt, links found, robots status, and scrape status
- create a safe pending link queue from discovered links
- filter queued links into candidates and skipped links before fetching
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

## Current seed URL file

```json
{
  "seed_urls": [
    "https://quotes.toscrape.com/"
  ]
}
```

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
link_queue_filtered_v14.json
source_report_v14.json
```

## Install

```powershell
pip install -r requirements.txt
```

## Run current queue filter

```powershell
python .\filter_link_queue_v14.py
```

## Run previous source extractor and queue builder

```powershell
python .\extract_source_records_v13.py
```

## Run previous source extractor

```powershell
python .\extract_source_records_v12.py
```

## Run previous quote scraper

```powershell
python .\scrape_all_quote_pages_v11.py
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
| v1.1 | Done | Add `seed_urls.json` input |
| v1.2 | Done | Extract general source records |
| v1.3 | Done | Add safe pending link queue |
| v1.4 | Done | Filter queue before fetching |

## Notes

The current queue filter does not fetch queued links. It only separates pending links into candidates and skipped links, with clear reasons.

The next development step is to review the v1.4 filtered queue output before any controlled fetching is added.

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
- convert Nutch-style discovery output into candidate source records
- run a local Streamlit control panel for safe local pipeline steps

## Safety rules

This project is for public-source research.

It is not designed to access private, restricted, paid, login-only, or blocked content. It should only fetch pages that are public and allowed, with polite delays and clear reports.

Nutch is treated as an optional discovery layer only. Nutch may find candidate public pages. The Python evidence pipeline decides what is usable evidence.

The local interface is for local use only. It does not run a live Nutch crawl in v2.4.

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
candidate_sources_discovered_v23.json
candidate_sources_discovered_v23.md
```

## Install

```powershell
pip install -r requirements.txt
```

## Run v2.4 local interface

This opens a local Streamlit control panel.

```powershell
streamlit run .\twis_source_engine_ui_v24.py
```

The interface can:

- load known local input files
- show `targeted`, `discovery`, and `hybrid` mode labels
- run safe local scripts that exist in the repo
- preview JSON and Markdown outputs

It does not expose live Nutch crawling.

## Run v2.3 Nutch discovery converter

This does not run a live crawl. It converts an existing Nutch-style sample file into standard candidate source records.

```powershell
python .\convert_nutch_output_v23.py
```

Optional explicit paths:

```powershell
python .\convert_nutch_output_v23.py --input .\testdata\nutch_discovery_sample_v23.json --json-output .\candidate_sources_discovered_v23.json --md-output .\candidate_sources_discovered_v23.md
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
| v2.2 | Done | Add optional Nutch discovery setup |
| v2.3 | Done | Convert Nutch-style output into candidate source records |
| v2.4 | Done | Add local interface to load inputs and run safe pipeline steps |

## Notes

The current queue filter does not fetch queued links. It only separates pending links into candidates and skipped links, with clear reasons.

The v2.3 Nutch converter does not fetch pages, run Nutch, or decide whether a page is evidence. It only converts supplied discovery records into candidate source records for later processing.

The v2.4 interface is a local control panel. It is not a deployed app and does not run live crawling.

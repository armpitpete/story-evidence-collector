# Story Evidence Collector

Story Evidence Collector is a public-source research tool for collecting evidence about a story from allowed web pages.

It is being built step by step from a safe Scrapling parser demo.

## Current status

### Evidence Pack v1 docs

Start with the [Evidence Pack v1 docs index](docs/evidence-pack-v1-docs-index.md) for the current validation rules, failure-case documentation, validator usage, and related v1 documentation links.

For a compact checklist of the required Evidence Pack v1 validation rules, see the [v1 validation rules summary](docs/evidence-pack-v1-validation-rules-summary.md).

For practical validator commands and usage notes, see the [Evidence Pack v1 validation guide](docs/evidence-pack-validation-v1.md).

For concrete examples of invalid packs and expected validator errors, see the [validator failure cases](docs/evidence-pack-validator-failure-cases-v1.md).

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
- extract candidate source/search URLs from the local TWIS website sources page
- build a separate seed URL file from website source candidates
- fetch a small selected set of public seed URLs after robots.txt checks
- run a local Streamlit control panel for safe local pipeline steps

## Safety rules

This project is for public-source research.

It is not designed to access private, restricted, paid, login-only, or blocked content. It should only fetch pages that are public and allowed, with polite delays and clear reports.

Nutch is treated as an optional discovery layer only. Nutch may find candidate public pages. The Python evidence pipeline decides what is usable evidence.

The local interface is for local use only. It does not run a live Nutch crawl in v2.7.

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
website_source_candidates_v25.json
website_source_candidates_v25.md
seed_urls_from_website_candidates_v26.json
seed_urls_from_website_candidates_v26.md
sources_raw_v27.json
link_queue_v27.json
source_report_v27.json
```

## Install

```powershell
pip install -r requirements.txt
```

## Run v2.7 local interface

This opens a local Streamlit control panel.

```powershell
py -m streamlit run .\twis_source_engine_ui_v24.py
```

The interface can:

- load known local input files
- read the local TWIS website sources page
- show `targeted`, `discovery`, and `hybrid` mode labels
- run safe local scripts that exist in the repo
- fetch a small selected set of public seed URLs after robots.txt checks
- preview JSON and Markdown outputs

It does not expose live Nutch crawling or queued-link fetching.

## Run v2.7 selected seed source fetcher

This fetches seed URLs only. It checks `robots.txt` before each fetch and does not fetch queued links.

Default input:

```text
seed_urls_from_website_candidates_v26.json
```

Run:

```powershell
python .\extract_source_records_from_seed_file_v27.py
```

Default behaviour:

```text
max seeds: 5
delay seconds: 1
```

Optional explicit settings:

```powershell
python .\extract_source_records_from_seed_file_v27.py --input .\seed_urls_from_website_candidates_v26.json --max-seeds 5 --delay-seconds 1
```

Outputs:

```text
sources_raw_v27.json
link_queue_v27.json
source_report_v27.json
```

## Run v2.6 seed URL builder

This does not fetch pages and does not overwrite `seed_urls.json`. It turns website source candidates into a separate seed URL file for review.

Default input:

```text
website_source_candidates_v25.json
```

Run:

```powershell
python .\build_seed_urls_from_candidates_v26.py
```

Default behaviour includes only normal source URLs:

```text
url
```

To include RSS and secondary URLs too:

```powershell
python .\build_seed_urls_from_candidates_v26.py --roles url,rssUrl,secondaryUrl
```

Outputs:

```text
seed_urls_from_website_candidates_v26.json
seed_urls_from_website_candidates_v26.md
```

## Run v2.5 TWIS website source extractor

This does not run a live crawl. It reads the local TWIS website source map and turns each source URL, RSS URL, and secondary URL into candidate source records.

Default input:

```text
../thisweekinsmoke/src/pages/sources/index.astro
```

Run:

```powershell
python .\extract_twis_website_sources_v25.py
```

Optional explicit paths:

```powershell
python .\extract_twis_website_sources_v25.py --input ..\thisweekinsmoke\src\pages\sources\index.astro --json-output .\website_source_candidates_v25.json --md-output .\website_source_candidates_v25.md
```

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
| v2.5 | Done | Extract candidate URLs from the TWIS website sources page |
| v2.6 | Done | Build separate seed URL file from website source candidates |
| v2.7 | Done | Fetch source records from selected seed URL file |

## Notes

The current queue filter does not fetch queued links. It only separates pending links into candidates and skipped links, with clear reasons.

The v2.3 Nutch converter does not fetch pages, run Nutch, or decide whether a page is evidence. It only converts supplied discovery records into candidate source records for later processing.

The v2.5 website source extractor reads the local TWIS website source map only. It does not fetch or crawl the listed sources.

The v2.6 seed builder creates a separate seed file only. It does not overwrite `seed_urls.json`.

The v2.7 selected seed fetcher fetches seed URLs only, checks `robots.txt`, applies a default max-seed limit, and does not fetch queued links.

The v2.7 interface is a local control panel. It is not a deployed app and does not run live crawling.

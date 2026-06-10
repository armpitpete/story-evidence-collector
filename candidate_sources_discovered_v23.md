# Nutch discovery candidate report v2.3

This report lists candidate pages discovered from the supplied Nutch output sample. It does not prove that the pages are relevant evidence.

## Scope

- No live crawl was run.
- No public pages were fetched.
- No evidence judgement was made.
- These are candidate pages only.

## Files

- Input: `testdata/nutch_discovery_sample_v23.json`
- JSON output: `candidate_sources_discovered_v23.json`

## Summary

- Candidate records written: 3
- Skipped records: 3

## Candidate pages

| # | Title | URL | Source domain | Discovered from | Crawl depth | Discovery method |
|---:|---|---|---|---|---:|---|
| 1 | Example report | https://www.gov.uk/government/publications/example-report | www.gov.uk | https://www.gov.uk/government/publications | 1 | nutch |
| 2 | Example committee report | https://committees.parliament.uk/publications/example-committee-report/ | committees.parliament.uk | https://committees.parliament.uk/publications/ | 1 | nutch |
| 3 | Example value for money report | https://www.nao.org.uk/reports/example-value-for-money-report/ | www.nao.org.uk | https://www.nao.org.uk/reports/ | 2 | nutch |

## Skipped records

| Input index | Reason | URL if present |
|---:|---|---|
| 4 | missing url |  |
| 5 | invalid or unsupported url | not-a-valid-url |
| 6 | record is not an object |  |

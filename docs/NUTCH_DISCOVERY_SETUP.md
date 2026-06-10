# Nutch discovery setup

## Purpose

Apache Nutch is the optional discovery layer for this project.

Use it when the job is:

> Find candidate public pages that we did not already know about.

Do not use Nutch to replace the existing evidence collector. The existing Python pipeline remains the evidence layer: it fetches known or discovered candidate URLs, extracts usable records, labels sources, matches subjects, and creates reports.

## Modes

### Targeted mode

Use the existing Python pipeline.

Best for:

- known source URLs
- small curated source lists
- article-specific evidence checks
- subject reports from collected records

### Discovery mode

Use Nutch, or a Nutch-style adapter.

Best for:

- finding unknown candidate pages
- crawling outward from trusted seed areas
- discovering publications, reports, PDFs, committee pages, or policy pages

### Hybrid mode

Use both.

Flow:

```text
Nutch discovery
→ candidate URLs
→ Python evidence collector
→ clean source records
→ subject match report
```

## GitHub setup

This repository contains a manual GitHub Actions workflow:

```text
.github/workflows/nutch-smoke-test.yml
```

It does not run automatically. It only runs when triggered manually from GitHub Actions.

The workflow checks that:

1. Java 11 can be installed.
2. Apache Nutch 1.22 can be downloaded.
3. The release checksum can be verified.
4. `bin/nutch` starts successfully.

It does not run a public crawl.

## Why Java 11

The current Apache Nutch tutorial lists Java/JDK 11 as the runtime/development requirement for Nutch 1.x.

## Why checksum verification

Apache recommends verifying release downloads using SHA512 or PGP signatures. The smoke test verifies the SHA512 checksum before running Nutch.

## Safe use rule

Nutch should only crawl public pages that are allowed by the target site's rules and by this project's safety rules.

Do not use it for:

- login-only pages
- paid/restricted pages
- private documents
- blocked content
- anti-bot bypass
- large unbounded crawls

## First safe test

The first real discovery test should be small and bounded:

```text
one source world
one seed URL
same domain only
low page limit
short crawl depth
manual run only
```

## Candidate output shape

The discovery layer should eventually output records like this:

```json
{
  "url": "",
  "title": "",
  "source_domain": "",
  "discovered_from": "",
  "discovery_method": "nutch",
  "crawl_depth": 0,
  "date_found": ""
}
```

The Python evidence layer can then read those candidate URLs and decide what is usable.

## Stop point for v0 setup

Stop when:

- the Nutch smoke test workflow runs manually
- the workflow verifies the Nutch command starts
- no public crawl is run from GitHub Actions yet
- the next issue defines the adapter from Nutch output to this project's JSON format

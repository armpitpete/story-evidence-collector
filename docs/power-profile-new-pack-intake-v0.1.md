# Power Profile new-pack intake v0.1

This document describes the first simple intake command for creating a Power Profile Evidence Pack.

The goal is to keep the front door simple while keeping the pack structure strict underneath.

## Command

Run from the repository root:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools\new-pack.ps1
```

The command asks:

1. What are you researching?
2. What question are you trying to answer?
3. What sources or links do you already have?
4. What output do you want?
5. How sensitive is this research?

The default sensitivity is `sensitive`.

## Non-interactive example

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools\new-pack.ps1 `
  -Subject "Andy Burnham" `
  -ResearchQuestion "Does Andy Burnham's public-control image match the interests around his political operation?" `
  -KnownSource "https://members.parliament.uk/member/1427/career","https://www.theguardian.com/" `
  -WantedOutput "article","evidence table","connection chart" `
  -Sensitivity sensitive
```

## Created pack shape

The command creates a validator-compatible Evidence Pack v1 folder under:

```text
fixtures/evidence-packs/
```

It creates the current v1 files:

```text
pack.json
README.md
sources/source-records.jsonl
sources/source-authority-map.jsonl
claims/claim-records.jsonl
evidence/evidence-items.jsonl
search/search-diary.jsonl
search/negative-evidence-log.jsonl
timeline/public-record-timeline.jsonl
timeline/denial-checks.jsonl
review/human-review.jsonl
output/final-brief.md
output/evidence-summary.md
output/contradiction-brief.md
```

It also creates Power Profile starter files:

```text
manifest.json
notes.md
people.jsonl
organisations.jsonl
relationships.jsonl
chart_nodes.jsonl
chart_edges.jsonl
```

## Current compatibility note

Evidence Pack v1 currently uses `pack.json` as the validator manifest.

The simple Power Profile intake metadata is stored in `manifest.json` for now. This keeps the first intake useful without breaking the existing v1 manifest schema.

A later task can decide whether `pack_type` belongs directly in `pack.json`.

## Validation

After creating the pack, the command runs:

```powershell
python scripts\validate_evidence_pack.py <pack-folder>
```

If validation fails, the command stops with an error.

## Safety rule

Simple at the front.

Structured underneath.

Human-checkable proof trail throughout.

## Public chart rule

Every public chart edge must have a source link.

Low-confidence relationships must stay off public charts.

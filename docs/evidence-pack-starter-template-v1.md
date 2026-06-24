# Evidence Pack starter template v1

Use this as a copyable starter shape for a first Evidence Pack v1.

This is a documentation template, not a real evidence pack.

## Folder shape

Create this folder shape inside `fixtures/evidence-packs/` or inside your chosen evidence-pack storage folder:

```text
2026-06-24-example-topic/
  pack.json
  README.md
  sources/
    source-records.jsonl
    source-authority-map.jsonl
  claims/
    claim-records.jsonl
  evidence/
    evidence-items.jsonl
  search/
    search-diary.jsonl
    negative-evidence-log.jsonl
  timeline/
    public-record-timeline.jsonl
    denial-checks.jsonl
  review/
    human-review.jsonl
  output/
    final-brief.md
    evidence-summary.md
    contradiction-brief.md
```

## `pack.json` starter

Replace the example values before using this for real work.

```json
{
  "pack_id": "2026-06-24-example-topic",
  "title": "Example evidence pack",
  "status": "draft",
  "created_at": "2026-06-24T00:00:00Z",
  "updated_at": "2026-06-24T00:00:00Z",
  "research_question": "What is being checked?",
  "scope": "What is inside and outside this pack?",
  "editorial_risk": "low",
  "publishability": "not_ready",
  "human_review_required": true,
  "records": {
    "source_records": "sources/source-records.jsonl",
    "source_authority_map": "sources/source-authority-map.jsonl",
    "claim_records": "claims/claim-records.jsonl",
    "evidence_items": "evidence/evidence-items.jsonl",
    "search_diary": "search/search-diary.jsonl",
    "negative_evidence_log": "search/negative-evidence-log.jsonl",
    "public_record_timeline": "timeline/public-record-timeline.jsonl",
    "denial_checks": "timeline/denial-checks.jsonl",
    "human_review": "review/human-review.jsonl"
  },
  "outputs": {
    "final_brief": "output/final-brief.md",
    "evidence_summary": "output/evidence-summary.md",
    "contradiction_brief": "output/contradiction-brief.md"
  }
}
```

## Starter JSONL records

Each JSONL file needs one JSON object per line.

Start with one simple object per file. Expand only after the pack validates.

### `sources/source-records.jsonl`

```jsonl
{"id":"source-001","note":"Starter source record. Replace with real source details."}
```

### `sources/source-authority-map.jsonl`

```jsonl
{"id":"authority-001","source_id":"source-001","note":"Starter source authority note. Replace with source weight and role."}
```

### `claims/claim-records.jsonl`

```jsonl
{"id":"claim-001","note":"Starter claim record. Replace with the claim being checked."}
```

### `evidence/evidence-items.jsonl`

```jsonl
{"id":"evidence-001","source_id":"source-001","claim_id":"claim-001","note":"Starter evidence item. Replace with a checkable proof fragment."}
```

### `search/search-diary.jsonl`

```jsonl
{"id":"search-001","note":"Starter search diary entry. Replace with search terms, dates, and sources checked."}
```

### `search/negative-evidence-log.jsonl`

```jsonl
{"id":"negative-001","note":"Starter negative evidence entry. Replace with what was searched for but not found."}
```

### `timeline/public-record-timeline.jsonl`

```jsonl
{"id":"timeline-001","note":"Starter public record timeline entry. Replace with a dated public record event."}
```

### `timeline/denial-checks.jsonl`

```jsonl
{"id":"denial-001","note":"Starter denial check. Replace with a denial, correction, softening, or explanation check."}
```

### `review/human-review.jsonl`

```jsonl
{"id":"review-001","note":"Starter human review note. Replace with review decision, risk, or unresolved check."}
```

## Starter output files

For a first validation pass, output files can be short draft files.

### `output/final-brief.md`

```md
# Final brief

Draft placeholder. Replace after evidence review.
```

### `output/evidence-summary.md`

```md
# Evidence summary

Draft placeholder. Replace after source and evidence records are checked.
```

### `output/contradiction-brief.md`

```md
# Contradiction brief

Draft placeholder. Replace after timeline and denial checks are reviewed.
```

## Validate the starter pack

From the repository root, run:

```powershell
python scripts\validate_evidence_pack.py fixtures\evidence-packs\2026-06-24-example-topic
```

Expected result:

```text
Evidence pack validation passed.
Pack folder: fixtures\evidence-packs\2026-06-24-example-topic
```

## Good enough rule

The starter pack is good enough when it validates and every required record/output path exists.

Do not treat starter text as evidence.

Replace placeholders before using the pack for a real article, audit, contradiction check, or research brief.

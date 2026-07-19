# Collector to Evidence Pack bridge v1

## Purpose

`scripts/create_draft_evidence_pack_from_collector.py` converts a bounded collector source-record JSON file into a complete Evidence Pack v1 folder skeleton.

The bridge solves one integration problem only:

```text
collector source metadata
        ↓
draft Evidence Pack structure
        ↓
existing Evidence Pack validator
        ↓
human evidence review
```

## Safety boundary

The bridge preserves source metadata. It does not:

- generate factual claims;
- decide that a source is relevant or authoritative;
- create evidence conclusions;
- infer motives, relationships or contradictions;
- browse or fetch URLs;
- mark a pack reviewed or publishable;
- modify an existing pack unless `--overwrite` is supplied deliberately.

Every generated pack is forced to:

- `status: draft`;
- `publishability: not_ready`;
- `human_review_required: true`.

Authority maps, claims, evidence items, negative-evidence records, timelines and denial checks are created as empty JSONL files. A pending human-review record states that no public wording is authorised.

## Input

The input must be a JSON list of collector source objects. Each item must contain an absolute HTTP or HTTPS URL in `final_url` or `source_url`.

The bridge:

- removes URL fragments;
- rejects missing or malformed URLs;
- rejects duplicate URLs after fragment removal;
- preserves page title and collection time when present;
- records collector status and robots metadata as unassessed notes.

## Controlled proof fixture

The regression fixture is:

```text
fixtures/collector-runs/
  2026-06-27-west-built-cheap-china-system/
    sources_raw_v13.json
```

It contains five external source URLs already recorded in the reviewed controlled TWIS Evidence Pack of the same topic. It is an offline integration fixture, not a new collection run and not proof that the article is publication-ready.

## Run

```bash
python scripts/create_draft_evidence_pack_from_collector.py \
  --source-records fixtures/collector-runs/2026-06-27-west-built-cheap-china-system/sources_raw_v13.json \
  --output-root generated/evidence-packs \
  --pack-id 2026-06-27-west-built-cheap-china-system-collector-draft \
  --title "Draft Evidence Pack — West Built the Cheap China System" \
  --research-question "What public evidence supports or limits the article's claims about low-value parcel duties, platform use and consumer price effects?" \
  --scope "Source metadata only; no claims or publication decision." \
  --created-at 2026-06-27T16:30:00Z \
  --editorial-risk high
```

Then validate:

```bash
python scripts/validate_evidence_pack.py \
  generated/evidence-packs/2026-06-27-west-built-cheap-china-system-collector-draft
```

## Output

The generated folder contains:

```text
pack.json
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

Only source records, one search-diary record and one pending-review record contain data. The remaining research files are intentionally empty.

## Regression proof

Run:

```bash
python scripts/test_collector_to_evidence_pack.py
```

The test proves:

- five source URLs are preserved;
- two identical runs produce byte-identical packs;
- the existing Evidence Pack validator accepts both packs;
- no claims, evidence conclusions, authority ratings or contradiction findings are generated;
- draft and `not_ready` safety states remain fixed;
- duplicate and missing URLs are rejected;
- existing output is not overwritten without the explicit flag.

## Human continuation

After generation, a human may review sources and deliberately add authority, claim, evidence, timeline, contradiction and publication records using the existing Evidence Pack process. That work is outside this bridge.

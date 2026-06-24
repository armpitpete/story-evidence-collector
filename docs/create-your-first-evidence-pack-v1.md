# Create your first Evidence Pack v1

This walkthrough shows the smallest safe path for creating a valid Evidence Pack v1.

Use it before adding larger Proof Trail material.

For a copyable starter shape, use `docs/evidence-pack-starter-template-v1.md` after reading this walkthrough.

## 1. Create one pack folder

Create one folder for the topic you are collecting evidence about.

Use a clear folder name that includes the date and topic.

Example:

```text
fixtures/evidence-packs/2026-06-24-example-topic/
```

The folder name should match the `pack_id` in `pack.json`.

## 2. Add the required folder shape

Inside the pack folder, add the folders used by the v1 manifest:

```text
sources/
claims/
evidence/
search/
timeline/
review/
output/
```

Start with the full shape even if most files contain only one starter record.

This makes the pack easier to validate and expand later.

## 3. Add `pack.json`

Add a `pack.json` file inside the pack folder.

The manifest should identify the pack, describe the research question, list the record files, and list the expected output files.

For the exact required manifest shape, use:

```text
docs/evidence-pack-assembly-v1.md
schemas/evidence-pack-manifest-v1.schema.json
```

## 4. Add one JSONL file for each required record path

The current v1 manifest expects these record files:

```text
sources/source-records.jsonl
sources/source-authority-map.jsonl
claims/claim-records.jsonl
evidence/evidence-items.jsonl
search/search-diary.jsonl
search/negative-evidence-log.jsonl
timeline/public-record-timeline.jsonl
timeline/denial-checks.jsonl
review/human-review.jsonl
```

Each JSONL line must be one complete JSON object.

Start with one record per file. Do not build a large evidence pack until the first small pack validates.

## 5. Give every record a stable ID

Every JSONL record needs a non-empty string `id`.

The `id` should be stable. Do not use a temporary name that will need to change later.

Good starter examples:

```text
source-001
authority-001
claim-001
evidence-001
search-001
negative-001
timeline-001
denial-001
review-001
```

Do not duplicate IDs inside the same JSONL file.

## 6. Add the expected output files

The current v1 manifest expects these output files:

```text
output/final-brief.md
output/evidence-summary.md
output/contradiction-brief.md
```

For a first pack, these can be short draft files.

They exist to prove that the pack can point from source records through to final readable outputs.

## 7. Check before validating

Before running the validator, check that:

- `pack.json` exists.
- `pack.json` points to the record files.
- every record file exists.
- every output file exists.
- every JSONL line is valid JSON.
- every JSONL record is an object.
- every JSONL record has an `id`.
- no JSONL record IDs are duplicated inside the same file.
- record and output paths stay inside the evidence-pack folder.

## 8. Run the validator

From the repository root, validate the pack:

```powershell
python scripts\validate_evidence_pack.py fixtures\evidence-packs\2026-06-24-example-topic
```

Expected result:

```text
Evidence pack validation passed.
Pack folder: fixtures\evidence-packs\2026-06-24-example-topic
```

If the validator reports an error, fix that error before adding more material.

Do not build a large pack on top of an invalid first pack.

## 9. Expand only after the first pass

After the first pack validates, add more records gradually.

Validate again after each small change.

A good first evidence pack proves the workflow, not the full investigation.

## Related docs

- `docs/evidence-pack-starter-template-v1.md`
- `docs/evidence-pack-assembly-v1.md`
- `docs/evidence-pack-validation-v1.md`
- `docs/evidence-pack-v1-validation-rules-summary.md`
- `docs/evidence-pack-validator-failure-cases-v1.md`
- `schemas/evidence-pack-manifest-v1.schema.json`

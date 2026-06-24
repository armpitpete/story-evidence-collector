# Evidence Pack Validator Failure Cases v1

This note explains the validator failure regression cases.

The failure tests prove that the evidence pack validator rejects known bad structure.

They do not prove truth, fairness, publishability, or human review.

## Files

Failure cases are defined in:

    fixtures/invalid-evidence-packs/validator-failure-cases.json

The test runner is:

    scripts/test_evidence_pack_validator_failures.py

The test runner creates temporary invalid evidence packs from the valid example pack:

    fixtures/evidence-packs/2026-06-22-example-topic

It does this so the normal valid fixture tree stays clean.

## Run the tests

From the repository root, run:

    python scripts\test_evidence_pack_validator_failures.py

Expected result:

    PASS: missing-title
    PASS: unexpected-top-level-field
    PASS: invalid-status
    PASS: invalid-pack-id
    PASS: absolute-record-path
    PASS: bad-jsonl-line
    PASS: record-parent-traversal
    PASS: output-parent-traversal
    PASS: jsonl-record-missing-id
    PASS: jsonl-record-not-object
    PASS: jsonl-record-duplicate-id
    PASS: evidence-unknown-source-id
    PASS: evidence-unknown-claim-id
    PASS: authority-unknown-source-id
    PASS: authority-unknown-related-claim-id
    PASS: claim-unknown-supported-by
    PASS: claim-unknown-weakened-by
    All validator failure regression tests passed. Count: 17

## Failure cases

### missing-title

This removes the required `title` field from `pack.json`.

It proves the validator still rejects a manifest when a required top-level field is missing.

Expected error:

    pack.json: missing required field: title

### unexpected-top-level-field

This adds an unknown top-level field to `pack.json`.

It proves the validator still enforces `additionalProperties: false` at manifest level.

Expected error:

    pack.json: unexpected field: extra_field_that_should_fail

### invalid-status

This changes `status` to `published`.

It proves the validator still enforces the allowed workflow status values.

Allowed values are:

- `draft`
- `active`
- `in_review`
- `reviewed`
- `archived`

Expected error:

    pack.json.status: must be one of: active, archived, draft, in_review, reviewed

### invalid-pack-id

This changes `pack_id` to `Bad Pack`.

It proves the validator still enforces the readable pack ID shape.

The expected shape is:

    YYYY-MM-DD-topic-name

The ID must use lowercase letters, numbers, and hyphens.

Expected error:

    pack.json.pack_id: must match YYYY-MM-DD-topic-name using lowercase letters, numbers, and hyphens

### absolute-record-path

This changes `records.source_records` to an absolute path.

It proves the validator still rejects paths that are not relative to the pack folder.

Expected error:

    records.source_records: path must be relative, got absolute path: /tmp/source-records.jsonl

### bad-jsonl-line

This appends an invalid JSON line to a referenced `.jsonl` file.

It proves the validator still checks JSONL records line by line.

Expected error fragment:

    invalid JSONL line

### jsonl-record-missing-id

This appends a valid JSON object without an `id` field to a referenced `.jsonl` file.

It proves the validator rejects JSONL records that cannot be identified and cross-referenced.

Expected error fragment:

    JSONL record must have a non-empty string id

### jsonl-record-not-object

This appends a valid JSON array to a referenced `.jsonl` file.

It proves the validator rejects JSONL lines that parse successfully but are not object records.

Expected error fragment:

    JSONL record must be an object

### record-parent-traversal

This changes `records.source_records` to a parent-traversal path.

It proves the validator rejects record paths that try to escape the evidence pack folder.

Expected error fragment:

    path must stay inside pack folder

### output-parent-traversal

This changes `outputs.final_brief` to a parent-traversal path.

It proves the validator rejects output paths that try to escape the evidence pack folder.

Expected error fragment:

    path must stay inside pack folder

### jsonl-record-duplicate-id

This appends two valid JSON object records with the same `id` value to a referenced `.jsonl` file.

It proves the validator rejects duplicate record IDs inside the same JSONL file, because duplicate IDs make cross-references unreliable.

Expected error fragment:

    duplicate JSONL record id 'duplicate-source-id'

### evidence-unknown-source-id

This appends an evidence item with a `source_id` that does not exist in `sources/source-records.jsonl`.

It proves the validator rejects evidence records that cannot be traced back to an existing source record.

Expected error fragment:

    unknown source_id 'missing-source-id'

### evidence-unknown-claim-id

This appends an evidence item with a `claim_id` that does not exist in `claims/claim-records.jsonl`.

It proves the validator rejects evidence records that cannot be traced back to an existing claim record.

Expected error fragment:

    unknown claim_id 'missing-claim-id'

### authority-unknown-source-id

This appends a source authority map record with a `source_id` that does not exist in `sources/source-records.jsonl`.

It proves the validator rejects source authority records that cannot be traced back to an existing source record.

Expected error fragment:

    unknown source_id 'missing-source-id'

### authority-unknown-related-claim-id

This appends a source authority map record with a `related_claim_id` that does not exist in `claims/claim-records.jsonl`.

It proves the validator rejects source authority records that cannot be traced back to an existing claim record.

Expected error fragment:

    unknown related_claim_id 'missing-claim-id'

### claim-unknown-supported-by

This appends a claim record with a `supported_by` evidence ID that does not exist in `evidence/evidence-items.jsonl`.

It proves the validator rejects claim records that cannot be traced to existing supporting evidence.

Expected error fragment:

    unknown supported_by item 'missing-evidence-id'

### claim-unknown-weakened-by

This appends a claim record with a `weakened_by` evidence ID that does not exist in `evidence/evidence-items.jsonl`.

It proves the validator rejects claim records that cannot be traced to existing weakening evidence.

Expected error fragment:

    unknown weakened_by item 'missing-evidence-id'

## What these tests do not cover

These tests do not check:

- whether evidence is true.
- whether a source is authoritative.
- whether a claim is fair.
- whether an interpretation is reasonable.
- whether a pack is complete.
- whether a pack is publishable.
- whether a human has reviewed the evidence.

Those checks belong to later editorial, provenance, and review layers.

## Why the invalid packs are temporary

The repository should keep normal fixture packs valid.

The regression script copies the valid example pack into a temporary directory, applies one broken change, runs the validator, then discards the temporary files.

This keeps the valid fixture tree clean while still proving failure behaviour.

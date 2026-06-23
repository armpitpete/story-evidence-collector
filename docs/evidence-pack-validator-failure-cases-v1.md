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
    PASS: jsonl-record-missing-id
    PASS: jsonl-record-not-object
    All validator failure regression tests passed. Count: 8

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

## Planned next failure case

### duplicate-jsonl-record-id

This is not active yet.

Issue #79 should add this failure case.

The planned test should create a JSONL file where two records use the same `id` value.

It should prove the validator rejects duplicate record IDs inside the same JSONL file, because duplicate IDs make cross-references unreliable.

Expected future error should include:

- the duplicated ID
- the JSONL file path
- enough location detail to find the duplicate record

## What these tests do not cover

These tests do not check:

- whether evidence is true.
- whether a source is authoritative.
- whether a claim is fair.
- whether an interpretation is reasonable.
- whether a pack is complete.
- whether a pack is publishable.
- whether a human has reviewed the evidence.
- whether JSONL record IDs are unique inside a file. That is planned in issue #79.

Those checks belong to later editorial, provenance, and review layers.

## Why the invalid packs are temporary

The repository should keep normal fixture packs valid.

The regression script copies the valid example pack into a temporary directory, applies one broken change, runs the validator, then discards the temporary files.

This keeps the valid fixture tree clean while still proving failure behaviour.

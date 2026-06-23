# Evidence Pack Validation v1

This note explains how to validate TWIS evidence packs locally and what the GitHub Actions check does.

## What validation checks

The current validator checks structure only.

It checks:

- `pack.json` exists.
- `pack.json` is valid JSON.
- `pack.json` can be read even if a Windows tool added a UTF-8 BOM.
- required manifest fields exist.
- unexpected manifest fields are rejected.
- manifest field values have the expected basic shape.
- `pack_id` follows the v1 readable ID pattern.
- `status`, `editorial_risk`, and `publishability` use allowed values.
- `created_at` and `updated_at` look like ISO date-time strings.
- `records` is an object.
- required `records` fields exist.
- unexpected `records` fields are rejected.
- `outputs` is an object.
- required `outputs` fields exist.
- unexpected `outputs` fields are rejected.
- paths listed in `records` and `outputs` are relative.
- files listed in `records` exist.
- files listed in `outputs` exist.
- `.jsonl` files parse line by line.
- each non-empty `.jsonl` line is a JSON object.
- each `.jsonl` record has a non-empty string `id`.

It does not yet check whether JSONL record IDs are unique inside a file.

That is tracked as issue #79: duplicate JSONL ID detection.

It does not decide whether evidence is true.

It does not decide whether a claim is fair.

It does not decide whether an evidence pack is publishable.

Editorial judgement still requires human review.

## Validate one evidence pack

From the repository root, run:

    python scripts\validate_evidence_pack.py fixtures\evidence-packs\2026-06-22-example-topic

Expected result:

    Evidence pack validation passed.
    Pack folder: fixtures\evidence-packs\2026-06-22-example-topic

## Validate all fixture evidence packs

From the repository root, run:

    python scripts\validate_all_evidence_packs.py

Expected result while there is one fixture pack:

    PASS: fixtures\evidence-packs\2026-06-22-example-topic
    All evidence packs passed validation. Count: 1

## Test validator failure cases

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

The failure tests build temporary invalid packs from the valid example fixture.

They do not keep broken evidence packs under `fixtures/evidence-packs/`.

The failure cases are listed in:

    fixtures/invalid-evidence-packs/validator-failure-cases.json

The failure-case behaviour is documented in:

    docs/evidence-pack-validator-failure-cases-v1.md

## CI validation

GitHub Actions runs Evidence Pack Validation on relevant pushes and pull requests.

The workflow is:

    .github/workflows/evidence-pack-validation.yml

It runs when these paths change:

- `fixtures/evidence-packs/**`
- `fixtures/invalid-evidence-packs/**`
- `scripts/validate_evidence_pack.py`
- `scripts/validate_all_evidence_packs.py`
- `scripts/test_evidence_pack_validator_failures.py`
- `.github/workflows/evidence-pack-validation.yml`

The CI commands are:

    python scripts\validate_all_evidence_packs.py
    python scripts\test_evidence_pack_validator_failures.py

## What a passing check means

A passing check means:

- the pack folder can be found.
- the manifest can be read.
- the manifest follows the manually enforced v1 schema shape.
- required files exist.
- JSON and JSONL records are parseable.
- JSONL records are objects with non-empty string IDs.
- known invalid pack shapes are still rejected.

A passing check does not mean:

- the evidence is correct.
- the interpretation is fair.
- the article is ready.
- the pack is safe to publish.
- the proof trail has had human review.
- JSONL IDs are unique inside a file. That check is planned in issue #79.

## Current validation chain

The current evidence pack chain is:

    docs
    -> manifest schema
    -> example fixture
    -> single-pack validator
    -> all-pack validator
    -> GitHub Actions CI
    -> validation documentation
    -> schema validation inside validator
    -> failure regression tests
    -> failure-case documentation
    -> path traversal safety checks
    -> JSONL record ID checks

## Later improvements

Later versions may add:

- duplicate JSONL ID detection inside each JSONL file.
- cross-file/global record ID uniqueness if needed.
- full JSON Schema library support if stdlib-only manual validation becomes too limited.
- cross-reference checks between sources, evidence, claims, timeline entries, and review records.
- pack completeness scoring.
- archive-link checks.
- human-review gate checks.
- publishability gate checks.

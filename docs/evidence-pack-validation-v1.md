# Evidence Pack Validation v1

This note explains how to validate TWIS evidence packs locally and what the GitHub Actions check now does.

## What validation checks

The current validator checks structure only.

It checks:

- `pack.json` exists.
- `pack.json` is valid JSON.
- required manifest fields exist.
- required `records` fields exist.
- required `outputs` fields exist.
- files listed in `records` exist.
- files listed in `outputs` exist.
- `.jsonl` files parse line by line.

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

## CI validation

GitHub Actions now runs Evidence Pack Validation on relevant pushes and pull requests.

The workflow is:

    .github/workflows/evidence-pack-validation.yml

It runs when these paths change:

- `fixtures/evidence-packs/**`
- `scripts/validate_evidence_pack.py`
- `scripts/validate_all_evidence_packs.py`
- `.github/workflows/evidence-pack-validation.yml`

The CI command is:

    python scripts/validate_all_evidence_packs.py

## What a passing check means

A passing check means:

- the pack folder can be found.
- the manifest can be read.
- required files exist.
- JSON and JSONL records are parseable.

A passing check does not mean:

- the evidence is correct.
- the interpretation is fair.
- the article is ready.
- the pack is safe to publish.
- the proof trail has had human review.

## Current validation chain

The current evidence pack chain is:

    docs
    -> manifest schema
    -> example fixture
    -> single-pack validator
    -> all-pack validator
    -> GitHub Actions CI

## Later improvements

Later versions may add:

- JSON Schema validation against `schemas/evidence-pack-manifest-v1.schema.json`.
- stronger path safety checks.
- required record ID checks.
- cross-reference checks between sources, evidence, claims, timeline entries, and review records.
- pack completeness scoring.
- archive-link checks.
- human-review gate checks.
- publishability gate checks.

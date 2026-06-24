# Evidence Pack v1 Docs Index

This page lists the Evidence Pack v1 documentation in reading order.

Evidence Pack v1 is the structural foundation for the proof-trail system.

It checks whether an evidence pack has the right shape.

It does not decide whether evidence is true, fair, complete, or publishable.

## Reading order

1. `docs/evidence-pack-v1-validation-rules-summary.md`

   Start here.

   This gives the short summary of what v1 validation guarantees and what it does not guarantee.

2. `docs/evidence-pack-validation-v1.md`

   Read this when you want to run validation locally or understand the GitHub Actions check.

3. `docs/evidence-pack-validator-failure-cases-v1.md`

   Read this when you want to understand the invalid fixture cases and regression-test behaviour.

4. `fixtures/invalid-evidence-packs/validator-failure-cases.json`

   Use this as the machine-readable list of known invalid pack shapes.

## v1 boundary

Evidence Pack v1 validation is deliberately limited.

It checks structure.

It protects the project from broken or unsafe pack shapes.

It does not replace editorial judgement, source checking, archive checking, contradiction checking, legal caution, or human review.

## Current v1 status

The current v1 validator covers:

- manifest structure
- required and unexpected manifest fields
- allowed status values
- readable pack IDs
- relative path checks
- parent-traversal path rejection
- required record and output files
- JSONL parsing
- JSONL object checks
- required JSONL record IDs
- duplicate JSONL record ID rejection inside each `.jsonl` file
- regression tests for known failure cases

## Next layer

Later evidence layers can build on this foundation.

Those later layers may check provenance, source quality, archive links, claim support, contradiction evidence, quote context, and publishability.

Those are not v1 validator jobs.

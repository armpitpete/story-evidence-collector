# Evidence Pack v1 Docs Index

This page lists the Evidence Pack v1 documentation in reading order.

Evidence Pack v1 is the structural foundation for the proof-trail system.

It checks whether an evidence pack has the right shape.

It does not decide whether evidence is true, fair, complete, or publishable.

## Reading order

1. `docs/create-your-first-evidence-pack-v1.md`

   Start here when you want to create your first valid evidence pack.

   This gives the smallest safe path for making a pack folder, adding the manifest, creating JSONL records, adding expected outputs, and running the validator.

2. `docs/evidence-pack-starter-template-v1.md`

   Use this when you want a copyable starter shape for a first pack.

   This gives a starter folder shape, `pack.json`, JSONL records, output placeholders, and the validator command.

3. `fixtures/evidence-packs/2026-06-22-example-topic/`

   Use this as the working valid example pack after reading the starter template.

   This shows a complete dummy fixture that can be validated without treating the contents as real evidence.

4. `docs/evidence-pack-v1-validation-rules-summary.md`

   Read this when you want the short summary of what v1 validation guarantees and what it does not guarantee.

5. `docs/evidence-pack-validation-v1.md`

   Read this when you want to run validation locally or understand the GitHub Actions check.

6. `docs/evidence-pack-validator-failure-cases-v1.md`

   Read this when you want to understand the invalid fixture cases and regression-test behaviour.

7. `fixtures/invalid-evidence-packs/validator-failure-cases.json`

   Use this as the machine-readable list of known invalid pack shapes.

8. `docs/proof-trail-schema-v1.md`

   Read this to understand the proof provenance structure used to preserve source chains, timestamps, records, and evidence traceability.

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

---

## Evidence Pack creation checklist

- [Evidence Pack creation checklist](evidence-pack-assembly-v1.md#evidence-pack-creation-checklist) — a short human checklist for creating a valid evidence pack before validation or sharing.

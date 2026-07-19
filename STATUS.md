---
completion_authority: true
standard: Recursive Project Improvement Standard v1.0
status: AUTHORISED
authority_ref: main
---

# Story Evidence Collector — Current Status

## Current authority

- Repository: `armpitpete/story-evidence-collector`
- Governing branch: `main`
- Current baseline: `c0b6a8ee99101bfe3faf368d1d2d587b0edf3aed`.
- Reviewed private-server inventory generated `2026-07-19T19:11:01+00:00` from a clean `main` checkout at that exact commit.
- Active supporting authority: PR #145 at exact head `ced084e95c76eb6ba0049b44e88bfeceeb02e0c1`, limited to the six-file Complete MP Report v1 schema, generator, fixture, test, specification and workflow.

## Current lane

Rebuild PR #145 on the current `main` without changing its fixture-only boundary. The Complete MP Report v1 lane may define and validate deterministic report structure, but it must not claim complete evidence coverage, refresh identity data, import sources, publish a profile or alter the private archive.

## Done

- Project-control authority and CI are merged.
- The read-only server inventory implementation is merged and was executed successfully on the private server.
- The archive root and all expected private folders exist with restricted permissions.
- The SQLite evidence cache opens read-only and passes `PRAGMA quick_check` with `ok`.
- Current database coverage is one MP, 33 divisions and 33 member votes from ParlParse, covering `2003-01-07` through `2003-01-31`.
- All 33 current vote meanings remain `needs_review`.
- Raw evidence folders are empty; no validation logs or backups were found.
- The January 2003 seed contains 33 rows, but the inventory's canonical-field check reports `recorded_vote` and `target_mp` absent in all 33 source rows; this remains an explicit data-shape exception and must not be hidden.
- No audit errors were recorded, and the server repository checkout was clean on `main`.
- Stale PR #144 was closed as superseded.

## To do

- Recreate exactly the six files from PR #145 on a new branch from current `main`.
- Preserve the fixture states `fixture_unverified`, `not_ready`, `public_output_authorised: false` and mandatory human review.
- Run the Complete MP Report fixture workflow and project-control CI.
- Review the exact six-file diff and merge the rebuilt PR if validation passes.
- Close PR #145 as superseded after the replacement merges.
- Synchronise this authority after merge and select the next bounded integration lane.
- Keep the missing backups, missing validation logs, empty raw stores, January 2003 seed-shape exception and limited vote coverage visible as unresolved operational work.

## Next bounded gate

Create a current-main replacement for PR #145 containing exactly `.github/workflows/complete-mp-report-fixture-test.yml`, `docs/complete-mp-report-specification-v1.md`, `schemas/complete-mp-report-v1.schema.json`, `scripts/generate_complete_mp_report.py`, `scripts/test_complete_mp_report_generator.py` and `fixtures/complete-mp-reports/jeremy-corbyn-fixture-v1.json`; merge only after both workflows pass and the final diff remains exact.

## Stop point

Do not represent the fixture as a completed MP report, mark it publishable, research or refresh Jeremy Corbyn data, import evidence, modify the private server, repair the seed-data exception, add backups, expand collector functionality or begin another lane before the rebuilt Complete MP Report v1 contract is merged and this authority is synchronised.

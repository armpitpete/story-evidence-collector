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
- Current baseline: `01d31bb9118d1fa40280ebd7aa5f55377b9e5a34`.
- Reviewed private-server inventory generated `2026-07-19T19:11:01+00:00` remains the authority for live archive state.
- Repository release scope is a bounded public-source collection, draft Evidence Pack and deterministic report-generation toolkit. Evidence truth, political interpretation, publication approval and full historical source coverage remain human or data-availability responsibilities.

## Current lane

Reconcile repository release authority and validation. Replace stale README/version claims, correct Evidence Pack fixture/status documentation, define the v1 repository completion contract, and add one offline release-validation workflow that compiles Python and runs all deterministic core regression suites.

## Done

- Project-control authority and CI are merged.
- The read-only private-server inventory is merged, executed and reviewed.
- Evidence Pack v1 manifest, validators, six controlled fixtures and validation workflow exist.
- Proof Trail schema, writer and validator exist.
- Complete MP Report v1 deterministic schema/generator fixture contract is merged.
- The collector-to-Evidence-Pack bridge is merged as `01d31bb9118d1fa40280ebd7aa5f55377b9e5a34` and proves deterministic draft-pack generation from five repository-authoritative TWIS source records.
- Generated bridge packs remain `draft`, `not_ready`, human-review required, and contain no generated claims, evidence conclusions or authority ratings.
- Stale PRs #144 and #145 are closed as superseded.

## To do

- Rewrite `README.md` around the current bounded product rather than the historical version ladder.
- Document the current entry points: local Streamlit UI, public trace pipeline, selected-seed fetcher, collector-to-pack bridge, Evidence Pack validation, Proof Trail tools and Complete MP Report generator.
- Correct Evidence Pack current-status documentation from five to six committed controlled packs and record the collector bridge.
- Add a repository release contract defining what v1 is complete for and what it deliberately does not claim.
- Add a release-validation workflow that runs Python compilation, all-pack validation, validator failure regressions, Complete MP Report fixture tests and collector-to-pack integration tests without network access.
- Keep the private-server operational exceptions visible: empty raw stores, no backups, no validation logs, only 33 January 2003 ParlParse votes for one MP, all meanings needing review, and an unresolved server-only seed-row shape report.
- Merge only after release validation and project-control CI pass.

## Next bounded gate

Create one release-reconciliation PR changing exactly `README.md`, `.github/workflows/repository-release-validation.yml`, `docs/evidence-pack-current-status-v1.md` and `docs/repository-release-contract-v1.md`; merge only after the full offline release workflow and project-control CI pass.

## Stop point

Do not change collector behaviour, evidence schemas, report schemas, fixtures, private-server data, seed rows, backup state, publication decisions or dependency versions; do not begin server hardening or another feature lane before release reconciliation is merged and this authority is synchronised.

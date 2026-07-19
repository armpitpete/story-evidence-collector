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
- Current baseline: `75335c1351eeca6ee57175a9588c8445fe5da350`.
- Reviewed private-server inventory generated `2026-07-19T19:11:01+00:00` remains the authority for live archive state.
- Complete MP Report v1 is merged as a fixture-only deterministic report contract; it is not evidence-complete or publishable.

## Current lane

Implement the first deterministic collector-to-Evidence-Pack bridge using a committed collector-run fixture derived from the existing controlled TWIS case `2026-06-27-west-built-cheap-china-system`. The bridge may transform collected source metadata into a draft Evidence Pack skeleton. It must not generate factual claims, evidence interpretations, contradiction findings, publication approval or inferred source authority.

## Done

- Project-control authority and CI are merged.
- The read-only server inventory implementation is merged, executed and reviewed.
- The private SQLite cache passes integrity checking but currently contains only one MP and 33 January 2003 ParlParse vote records, all requiring meaning review.
- Raw evidence stores are empty; backups and validation logs are absent; the January 2003 source-row shape exception remains unresolved.
- Complete MP Report v1 schema, generator, fixture, test, specification and workflow merged through PR #151 as `75335c1351eeca6ee57175a9588c8445fe5da350`.
- Stale PRs #144 and #145 are closed as superseded.
- Evidence Pack v1 manifest, validators, fixtures and project-wide validation workflow already exist.
- The existing controlled TWIS pack `2026-06-27-west-built-cheap-china-system` supplies repository-authoritative source metadata for the first bridge fixture.

## To do

- Add a bounded collector-run fixture containing the five external public sources already recorded in the controlled TWIS pack.
- Add `scripts/create_draft_evidence_pack_from_collector.py` to convert collector source records into a complete draft-pack directory structure.
- Generate source records and a search diary only; leave authority maps, claims, evidence, timeline, denial and negative-evidence records empty.
- Generate an explicit pending human-review record and draft-only Markdown outputs.
- Force `status: draft`, `publishability: not_ready` and `human_review_required: true`.
- Reject malformed source input, missing URLs, duplicate normalised URLs, unsafe output paths and overwrite attempts unless explicitly allowed.
- Add a regression test proving deterministic output, five preserved source URLs, zero generated claims/evidence, successful Evidence Pack validation and unchanged draft safety state.
- Add a dedicated GitHub Actions workflow and a concise operator contract.
- Merge only after the new integration workflow, Evidence Pack validation and project-control CI pass.

## Next bounded gate

Create one implementation PR changing exactly `.github/workflows/collector-to-evidence-pack-test.yml`, `docs/collector-to-evidence-pack-v1.md`, `fixtures/collector-runs/2026-06-27-west-built-cheap-china-system/sources_raw_v13.json`, `scripts/create_draft_evidence_pack_from_collector.py` and `scripts/test_collector_to_evidence_pack.py`; validate deterministic draft-pack generation and merge if all checks pass.

## Stop point

Do not browse or fetch live sources, alter the existing reviewed Evidence Pack fixture, generate claims or evidence conclusions, infer source authority, mark any generated pack reviewed or publishable, modify the private server, repair the seed-data exception, add backups, package a general CLI or begin another lane before this bridge is merged and this authority is synchronised.

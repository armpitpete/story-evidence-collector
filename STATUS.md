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
- Exact starting head for this lane: `5b928de43392a9c2d230621381d13c71126ea7d8`.
- Repository Release v1 remains complete and authoritative.
- Backup-and-restore hardening remains complete, with the accepted backup and disposable restore retained on the private server.

## Current lane

January 2003 seed-row shape reconciliation.

Goal: determine and document why the generated January 2003 ParlParse batch rows use source-shape fields while the imported SQLite member-vote records contain canonical `recorded_vote` and `target_mp` fields, then make that boundary deterministic and regression-tested without changing evidence meaning.

Authorised implementation scope:

- `server_imports/build_server_evidence_cache.py`
- `server_imports/audit_server_state.py`
- `server_imports/README.md`
- `server_imports/example_config.example.json`
- `docs/january-2003-seed-row-shape-reconciliation.md`
- `scripts/test_january_2003_seed_shape.py`
- `.github/workflows/january-2003-seed-shape-test.yml`

## Done

- Repository Release v1 is complete and authoritative.
- Backup-and-restore hardening is complete.
- The first real backup and disposable restore passed.
- The accepted restored database baseline remains 33 January 2003 ParlParse divisions, 33 member votes, one member, one source and one import.
- All 33 vote meanings remain `needs_review`.
- Exact current `main` and the absence of open pull requests were verified before opening this lane.
- Initial repository tracing established that the ParlParse parser emits `recorded_side` per row while the target MP is held at batch-plan and manifest level; the SQLite schema stores row-level canonical `recorded_vote` and `target_mp` fields.

## To do

- Make the importer explicitly accept the actual generated batch shape by mapping `recorded_side` to canonical vote fields and resolving target identity from reviewed batch-manifest context when it is absent from each source row.
- Preserve the original source row unchanged in `source_trace`.
- Make the read-only audit distinguish raw source shape from canonical import readiness.
- Add deterministic regression coverage for source rows, manifest context, canonical SQLite output and failure without target identity.
- Document the classification and operator boundary.
- Run the dedicated regression workflow and existing repository release validation.
- Open and review the bounded implementation pull request, then synchronise this authority after merge.

## Next bounded gate

Merge this authority-only activation change after project-control validation, then open one controlled implementation pull request changing only the seven authorised files.

The implementation must classify the discrepancy as one of:

- a real data or importer defect;
- an alias or normalisation boundary;
- an expected source/import distinction;
- or a combination that clearly separates expected shape differences from any missing repository machinery.

## Stop point

Do not change any vote value, vote meaning, `meaning_quality`, source coverage, MP coverage, publication state or private-server evidence. Do not run a new source collection, import into the live database, rotate backups or delete the retained disposable restore. Stop only if the existing repository and retained metadata cannot determine the transformation without an evidence-content decision.

---
completion_authority: true
standard: Recursive Project Improvement Standard v1.0
status: AUTHORITATIVE
authority_ref: main
---

# Story Evidence Collector — Current Status

## Current authority

- Repository: `armpitpete/story-evidence-collector`
- Governing branch: `main`
- January 2003 seed-row shape implementation merge: `4cc7cef44ad92af1ed0f0d15f0fb9e9c063bde2b`.
- Repository Release v1 remains complete and authoritative.
- Backup-and-restore hardening remains complete, with the accepted backup and disposable restore retained on the private server.

## Current lane

No implementation lane is active.

The January 2003 seed-row shape reconciliation is complete. Further work requires a separately authorised post-release lane with a bounded goal, permitted files, validation and stop rule.

## Done

- Repository Release v1 is complete and authoritative.
- Backup-and-restore hardening is complete.
- The first real backup and disposable restore passed.
- The accepted restored database baseline remains 33 January 2003 ParlParse divisions, 33 member votes, one member, one source and one import.
- All 33 vote meanings remain `needs_review`.
- Exact pre-lane `main` was verified as `5b928de43392a9c2d230621381d13c71126ea7d8`, with no open pull requests.
- Authority activation PR #163 merged as `72ffeb3c75e0b7fd9de5ebff2b95b52703e56890`.
- Implementation PR #164 merged as `4cc7cef44ad92af1ed0f0d15f0fb9e9c063bde2b` from exact reviewed head `78c1272b72ba0edf790da8a37d2643bedd6c4f32`.
- The discrepancy is classified as an expected source/import distinction plus an alias/normalisation boundary, with a real repository defect in the previously manual and undocumented adapter boundary.
- The repository now records that the January rows file is generated local evidence, not a committed evidence-row artifact.
- The importer now accepts reviewed manifest context, maps `date` to `division_date`, maps `recorded_side` to canonical `recorded_vote` and `vote_side`, and rejects mismatched manifest identity.
- Original source rows remain unchanged in `source_trace`; no canonical fields are injected into source evidence.
- The read-only audit now separates exact raw canonical-name omissions from fields missing after approved aliases and manifest context.
- Dedicated regression proof creates a disposable SQLite database and verifies canonical values, unchanged source trace, retained `needs_review`, missing-context refusal and mismatched-manifest refusal.
- January 2003 seed shape test, Repository release validation and Project control all passed at the exact implementation head.

## To do

- No work remains in the January 2003 seed-row shape reconciliation lane.
- No live database import is required: the accepted database already contains the canonical records, and this lane changed repository machinery and authority only.
- Any future evidence review, source expansion, publication work or server operation must be opened as a separate bounded lane.

## Next bounded gate

None. Begin another lane only through an explicit authority update that names the goal, authorised files or server operations, validation and stop point.

## Stop point

Do not continue automatically into vote-meaning review, evidence expansion, publication, live re-import, backup rotation or deletion of the retained disposable restore. The repository is authoritative with no implementation lane active.

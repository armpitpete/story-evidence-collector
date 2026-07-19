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
- Completed Release v1 closure: `8e26eeb9c2a9153eb52c35e8286c0e9edf5f4e50`.
- Backup-and-restore implementation: initial merge `2a569a626fc27d0e569c8b08d2761ddee30b7214`, required structural repair `7943669c669cab9877e51a5d0ad0803bff1776a6`.
- First accepted private-server proof executed from clean `main` at `21bb060f101fa1d3fdc9f57f3b611982a7f79008` on `2026-07-19T21:16:31+00:00`.
- Release v1 remains complete and the bounded backup-and-restore hardening lane is complete.

## Current lane

Backup-and-restore hardening closure. No implementation or server-execution lane is active. Further work requires a separately authorised post-release lane with its own bounded goal, allowed files, validation and stop point.

## Done

- Repository Release v1 is complete and authoritative.
- PR #157 opened the bounded backup-and-restore hardening lane.
- PR #158 added the backup creator, verifier/restorer, regression suite, operator documentation and dedicated workflow.
- PR #160 repaired the restore shape so the top-level empty `backups/` directory and its mode are preserved while prior backup contents remain excluded.
- GitHub backup-and-restore tests, repository release validation and project-control CI passed on the repaired implementation.
- The private checkout was clean on `main` and contained the repaired implementation.
- Backup `backup-20260719T211631Z-manual-v1` was created atomically under the private archive backup store.
- The manifest recorded 22 entries: 6 files, 16 directories and 171,780 checked file bytes.
- Backup verification passed with SQLite `PRAGMA quick_check` equal to `ok`.
- Disposable restore verification passed with 6 checked files, 171,780 checked bytes and SQLite `PRAGMA quick_check` equal to `ok`.
- The restored archive retained every expected directory, including an empty top-level `backups/` directory.
- The restored database matched the reviewed live baseline: 33 divisions, 33 member votes, 1 member, 1 source, 1 import, date range `2003-01-07` through `2003-01-31`, 1 distinct target MP and 33 `needs_review` meanings.
- The restored audit recorded no errors.
- The live database SHA-256 remained exactly `c90c075c11caed36bff275057f1eaf355f477e78b8f0355fc1393c4242e1f10a` before and after the run.
- The terminal wrapper emitted a trailing here-document/paste warning only after all controlled commands and final PASS results had completed; it did not affect the backup, verification, restore, audit or immutability proof.

## To do

No work is required to complete the bounded backup-and-restore hardening lane.

The following remain separate post-release objectives and are not implied complete:

- backup scheduling, retention and deletion policy;
- encrypted or off-server backup copies;
- recovery from total server loss;
- promotion of a restored snapshot into production;
- January 2003 seed-row shape reconciliation;
- review of the existing 33 vote meanings;
- expansion of MP evidence coverage;
- evidence interpretation and publication review.

The accepted backup and disposable restore remain present. Their deletion or rotation is not part of this closure change.

## Next bounded gate

None. Begin another lane only through an explicit authority update naming one bounded objective, such as seed-row shape reconciliation, backup scheduling and retention, off-server disaster recovery, vote-meaning review, or one explicitly scoped MP evidence report.

## Stop point

Do not infer complete evidence coverage, automated production durability, off-server disaster recovery, completed MP research or publication approval from this local backup-and-disposable-restore proof. Do not continue modifying the completed hardening lane merely to create activity.
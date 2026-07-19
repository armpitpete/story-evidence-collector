---
completion_authority: true
standard: Recursive Project Improvement Standard v1.0
status: BLOCKED
authority_ref: main
---

# Story Evidence Collector — Current Status

## Current authority

- Repository: `armpitpete/story-evidence-collector`
- Governing branch: `main`
- Completed Release v1 closure: `8e26eeb9c2a9153eb52c35e8286c0e9edf5f4e50`.
- Backup-and-restore implementation merge: `2a569a626fc27d0e569c8b08d2761ddee30b7214`.
- Reviewed private-server inventory generated `2026-07-19T19:11:01+00:00` is the authority for the archive state before the first backup run.
- Release v1 remains complete; this is a separate post-release operational-hardening lane.

## Current lane

Execute the merged backup tooling once against the private archive, verify the backup in place, restore it into a new disposable directory, and compare the restored non-sensitive inventory with the live baseline. Do not restore over the live archive.

## Done

- Repository Release v1 is complete and authoritative.
- PR #157 opened this bounded post-release lane and merged as `c467ea4df8272ab270604303f2165b2b0f7185f0`.
- PR #158 added exactly the five authorised backup, verification, regression, documentation and workflow files and merged as `2a569a626fc27d0e569c8b08d2761ddee30b7214`.
- The implementation uses SQLite's online backup API and verifies source and backup databases with `PRAGMA quick_check`.
- Backup creation is atomic, excludes the backup store and SQLite sidecars, preserves modes, and writes a path/type/mode/size/SHA-256 manifest.
- Verification rejects traversal, symlinks, special files, missing or extra entries, mode/size/hash mismatch and damaged SQLite.
- Restore refuses every existing destination and validates a hidden partial restore before atomic promotion to the requested disposable path.
- Local regression testing passed on exact blobs.
- GitHub server backup-and-restore testing, repository release validation and project-control CI all passed on PR #158 exact head `6112e8eb206231b9e9761b52577f47e775207e57`.

## To do

- On the private server, confirm the repository checkout is clean and fast-forward `main` to at least `2a569a626fc27d0e569c8b08d2761ddee30b7214`.
- Choose a new explicit timestamped backup name and confirm that both the backup path and disposable restore path do not exist.
- Run `server_imports/create_server_backup.py` against `/srv/story-evidence-collector`.
- Run `server_imports/verify_restore_server_backup.py verify` against the new backup.
- Run `server_imports/verify_restore_server_backup.py restore` into a new path under `/home/storyevidence`.
- Run `server_imports/audit_server_state.py` against the disposable restore.
- Review and return a non-sensitive result containing the exact commit, backup name, manifest counts and bytes, both SQLite quick-check results, restored table counts, date range, distinct MP count and any mismatch.
- Synchronise this authority after the reviewed result and close the hardening lane only if backup and restore proof passes.

## Next bounded gate

A human with private-server access must run the controlled commands in `docs/private-server-backup-restore-v1.md` using exact merged implementation commit `2a569a626fc27d0e569c8b08d2761ddee30b7214` or a later descendant on `main`, then return the reviewed non-sensitive output.

## Stop point

Do not delete or rotate backups, delete the disposable restore, promote a restore into production, schedule backups, copy data off-server, change ownership, alter evidence records, repair the January 2003 seed shape, review vote meanings, expand coverage, import sources or begin another post-release lane until the first backup and disposable-restore result has been reviewed and recorded.

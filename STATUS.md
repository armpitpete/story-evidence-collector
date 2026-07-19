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
- Completed Release v1 closure: `8e26eeb9c2a9153eb52c35e8286c0e9edf5f4e50`.
- Release contract: `docs/repository-release-contract-v1.md`.
- Reviewed private-server inventory generated `2026-07-19T19:11:01+00:00` is the authority for the archive state before this lane.
- Release v1 remains complete; this is a separate post-release operational-hardening lane.

## Current lane

Create and prove a verified, restorable backup of the private Story Evidence Collector archive without changing evidence meaning, importing sources, expanding coverage or restoring over the live archive.

## Done

- Repository Release v1 is complete and authoritative.
- The private archive exists at `/srv/story-evidence-collector` with restricted permissions.
- The SQLite cache opens read-only and passed `PRAGMA quick_check` with `ok`.
- Current evidence remains limited to one MP, 33 January 2003 ParlParse divisions and 33 member votes, all `needs_review`.
- The reviewed inventory found no existing backups and no validation logs.

## To do

- Add a backup creator that snapshots the private archive into an atomic timestamped backup directory.
- Use SQLite's backup API for a consistent database copy rather than copying a potentially live database file directly.
- Exclude the backup store itself to prevent recursive backups.
- Generate a manifest containing relative paths, sizes and SHA-256 checksums.
- Add a verifier/restorer that validates the manifest and restores only into a new disposable target directory.
- Refuse destination overwrite, path traversal, checksum mismatch and damaged SQLite backups.
- Add deterministic temporary-directory regression tests covering backup, verification, disposable restore, source preservation, corruption detection and overwrite refusal.
- Add operator documentation and a dedicated offline GitHub Actions workflow.
- Merge the repository implementation only after project-control and backup/restore tests pass.
- Run the merged tooling once on the private server and review the resulting backup and disposable restore before closing this lane.

## Next bounded gate

Open one implementation PR from current `main` changing exactly:

- `server_imports/create_server_backup.py`;
- `server_imports/verify_restore_server_backup.py`;
- `scripts/test_server_backup_restore.py`;
- `docs/private-server-backup-restore-v1.md`;
- `.github/workflows/server-backup-restore-test.yml`.

Merge only after the exact five-file diff and both workflows pass.

## Stop point

Do not delete old files, implement retention deletion, overwrite the live archive, alter evidence records, repair the January 2003 seed shape, review vote meanings, expand MP coverage, import sources or begin another post-release lane. After repository merge, stop only for the private-server backup and disposable-restore execution result.

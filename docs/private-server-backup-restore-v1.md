# Private Server Backup and Disposable Restore v1

## Purpose

This lane creates a verified, restorable snapshot of the private Story Evidence Collector archive without changing evidence meaning or expanding source coverage.

The tooling is designed for:

- `/srv/story-evidence-collector` as the live archive;
- `/srv/story-evidence-collector/backups` as the default local backup store;
- a new disposable restore directory outside the live archive;
- execution as the `storyevidence` account.

It does not promote a restored snapshot into production.

## Files

- `server_imports/create_server_backup.py`
- `server_imports/verify_restore_server_backup.py`
- `scripts/test_server_backup_restore.py`
- `.github/workflows/server-backup-restore-test.yml`

## Safety properties

The backup creator:

- reads the source archive without editing or deleting it;
- excludes the backup store itself, preventing recursive backups;
- rejects source symlinks and special files;
- detects non-database files that change while being copied;
- uses SQLite's online backup API for `db/mp_evidence_cache.sqlite`;
- checks the source and backup databases with `PRAGMA quick_check`;
- excludes SQLite `-wal`, `-shm`, and `-journal` sidecars;
- normalises the backed-up database to delete-journal mode;
- preserves file and directory modes;
- writes a manifest containing every relative path, type, mode, file size, and SHA-256;
- builds in a hidden partial directory and renames only after successful completion;
- never removes older backups.

The verifier/restorer:

- rejects missing or malformed manifests;
- rejects absolute paths and `..` traversal;
- rejects duplicate paths, symlinks, special files, missing files, and extra files;
- checks types, modes, sizes, and SHA-256 values;
- runs SQLite `PRAGMA quick_check` after verification;
- refuses to restore into any existing destination;
- restores first into a hidden partial directory;
- validates the complete restored snapshot before atomically renaming it;
- never writes to the live archive unless an operator incorrectly selects a new, nonexistent path there. Do not do that.

## Backup layout

A backup is a directory such as:

```text
/srv/story-evidence-collector/backups/
└── backup-20260719T210000Z-manual-v1/
    ├── manifest.json
    └── archive/
        ├── db/
        │   └── mp_evidence_cache.sqlite
        ├── raw/
        ├── reports/
        └── logs/
```

`manifest.json` is the integrity authority for the snapshot.

## Automated regression test

Run from the repository root:

```bash
python3 -m py_compile \
  server_imports/create_server_backup.py \
  server_imports/verify_restore_server_backup.py \
  scripts/test_server_backup_restore.py

python3 scripts/test_server_backup_restore.py
```

The regression suite proves:

- source content is unchanged;
- a backup is created and verifies;
- SQLite data survives a disposable restore;
- file and directory modes survive;
- the backup store and SQLite sidecars are excluded;
- checksum corruption is detected;
- manifest path traversal is rejected;
- a damaged SQLite file is rejected even if its manifest hash is maliciously updated;
- an existing restore destination is never overwritten;
- source symlinks are rejected.

## First controlled private-server run

### 1. Update the checkout safely

```bash
sudo -iu storyevidence
cd /home/storyevidence/story-evidence-collector

git status --short --branch
git fetch origin main
git pull --ff-only origin main
git rev-parse HEAD
```

Stop if the working tree is not clean. Do not reset or discard local work.

### 2. Choose an explicit backup name

```bash
BACKUP_NAME="backup-$(date -u +%Y%m%dT%H%M%SZ)-manual-v1"
BACKUP_DIR="/srv/story-evidence-collector/backups/$BACKUP_NAME"
RESTORE_ROOT="/home/storyevidence/restore-check-$BACKUP_NAME"

printf '%s\n' "$BACKUP_NAME" "$BACKUP_DIR" "$RESTORE_ROOT"
```

Confirm that neither `$BACKUP_DIR` nor `$RESTORE_ROOT` exists.

### 3. Create the backup

```bash
python3 server_imports/create_server_backup.py \
  --archive-root /srv/story-evidence-collector \
  --backup-name "$BACKUP_NAME"
```

Expected final lines:

```text
Backup created successfully.
Backup directory: /srv/story-evidence-collector/backups/<backup-name>
Manifest: /srv/story-evidence-collector/backups/<backup-name>/manifest.json
```

### 4. Verify the backup in place

```bash
python3 server_imports/verify_restore_server_backup.py \
  verify "$BACKUP_DIR"
```

Expected result:

```text
Backup verification passed.
```

The JSON report must show:

- at least one checked file;
- `database_quick_check` equal to `ok`;
- the expected backup directory and name.

### 5. Restore into a disposable target

```bash
python3 server_imports/verify_restore_server_backup.py \
  restore "$BACKUP_DIR" "$RESTORE_ROOT"
```

Expected result:

```text
Backup restore passed.
```

The command must refuse to run if `$RESTORE_ROOT` already exists.

### 6. Audit the disposable restore

```bash
python3 server_imports/audit_server_state.py \
  --archive-root "$RESTORE_ROOT" \
  --repo-root /home/storyevidence/story-evidence-collector
```

Compare the non-sensitive result with the reviewed live inventory:

- SQLite quick check remains `ok`;
- table and row counts match;
- source-system counts match;
- earliest and latest division dates match;
- distinct target-MP count matches;
- raw, report, and log file counts are plausible;
- no audit errors appear.

## Review evidence to return

Return only a reviewed, non-sensitive summary containing:

- exact repository commit;
- backup directory name;
- manifest file count and total checked bytes;
- backup SQLite quick-check result;
- disposable restore SQLite quick-check result;
- restored table and row counts;
- restored date range and distinct MP count;
- confirmation that the live archive remained unchanged;
- any errors or mismatches.

Do not share raw evidence, credentials, private keys, or unexpected private paths.

## Deliberate limitations

This v1 lane does not:

- delete or rotate backups;
- copy backups off the server;
- encrypt backups;
- schedule automated backups;
- promote a restored snapshot into the live archive;
- change ownership during restore;
- prove disaster recovery from total server loss.

Those require separate post-release authority. The current lane proves local snapshot integrity and disposable restoration only.

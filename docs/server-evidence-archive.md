# Webmin Server Evidence Archive Plan

## Purpose

This document locks the server storage model for the MP evidence pipeline.

The project needs two separate places for two separate jobs:

- GitHub stores the machinery.
- The Webmin server stores the evidence.

GitHub should hold code, schemas, small fixtures, documentation, and controlled reports. The Webmin server should hold raw source material, normalised databases, large generated indexes, import logs, backups, and evidence snapshots.

## Current server facts

| Item | Value |
|---|---|
| Archive root | `/srv/story-evidence-collector/` |
| Project user | `storyevidence` |
| Starting free space | about 180 GB |
| Public web folder | not used |
| Archive visibility | private by default |

The archive must stay outside public website directories such as `public_html`.

## Core rule

```text
GitHub stores the machinery.
The Webmin server stores the evidence.
```

A second working rule is:

```text
Raw archive = proof.
Normalised database = usable evidence.
Reports = readable output.
```

## Required folder layout

```text
/srv/story-evidence-collector/
  raw/
    commons-votes/
    members/
    parlparse/
    hansard/
    interests/
    committees/
  db/
    mp_evidence_cache.sqlite
  reports/
    coverage/
    mp/
    divisions/
  logs/
    imports/
    validation/
  backups/
```

## Folder rules

### `raw/`

Use `raw/` for downloaded or copied source material. Raw files are the evidence receipts.

Examples:

- Commons Votes API JSON responses
- Parliament Members API JSON responses
- ParlParse XML files
- saved source metadata
- downloaded source manifests
- compressed raw source snapshots

Raw files should not be edited by hand. If a source file needs cleaning, write a normalised copy into the database or a derived output folder instead.

### `db/`

Use `db/` for local/server databases.

Expected first database:

```text
/srv/story-evidence-collector/db/mp_evidence_cache.sqlite
```

The database should contain normalised records, not untraceable summaries. Every normalised row should keep enough source fields to link back to the raw archive.

### `reports/`

Use `reports/` for readable generated outputs.

Examples:

- MP vote index reports
- coverage reports
- missing-period reports
- duplicate-key reports
- source-quality reports
- review-needed reports

Reports may later be copied selectively to GitHub if they are small and safe, but raw evidence should not be copied to GitHub by default.

### `logs/`

Use `logs/` for import and validation logs.

Logs should answer:

- what command ran
- when it ran
- what source was used
- how many files were read
- how many rows were created
- how many rows failed validation
- whether network access was used
- where output was written

### `backups/`

Use `backups/` for compressed snapshots of important project evidence and the SQLite database.

Backups should be named clearly and should not overwrite the previous backup unless a separate rotation rule exists.

## What stays out of GitHub

Do not commit these to GitHub:

```text
/srv/story-evidence-collector/raw/
/srv/story-evidence-collector/db/*.sqlite
/srv/story-evidence-collector/db/*.sqlite-wal
/srv/story-evidence-collector/db/*.sqlite-shm
/srv/story-evidence-collector/backups/
.env
*.pem
*.key
id_ed25519
id_ed25519.pub if it identifies a private deployment workflow
```

GitHub should not contain:

- server passwords
- Webmin passwords
- private SSH keys
- API secrets
- private `.env` files
- bulk raw evidence archives
- large SQLite database files
- generated caches that can be rebuilt

## Public/private separation

The evidence archive is private by default.

Do not store evidence archive files inside:

```text
public_html
www
htdocs
```

A report should become public only after a deliberate export step.

Use this model:

```text
private archive -> reviewed report -> selected public export
```

Never expose the raw archive accidentally.

## Naming rules for raw source files

Raw source files should use stable names that preserve source, date, and scope.

Suggested pattern:

```text
<source-system>/<scope>/<date-or-range>__<source-id>.<ext>
```

Examples:

```text
raw/commons-votes/divisions/2026-06-17__division-1234.json
raw/members/member/2026-06-17__member-185.json
raw/parlparse/2003/01/2003-01-15__division-source.xml
```

If a source does not have a clear date, include the download date and source identifier.

## Source metadata rule

Every import should preserve:

- source system
- source URL or source path
- source identifier
- download or capture time
- parser version
- import run ID
- checksum when useful
- whether the file was fetched live or read from cache

## Compression rules

Raw evidence can be compressed after import when it is no longer actively being inspected.

Preferred archive format:

```text
.tar.zst
```

Acceptable alternatives:

```text
.zip
.tar.gz
```

Do not compress active SQLite database files while they are in use. For database backups, stop writes first or use the SQLite backup command.

## Storage thresholds

Starting free space was about 180 GB. Use these thresholds:

| Free space left | Meaning | Action |
|---:|---|---|
| 100 GB+ | safe | continue normal work |
| 60-100 GB | watch | check raw cache growth |
| 40-60 GB | warning | compress old raw batches and review backups |
| 20-40 GB | stop bulk imports | make a cleanup or expansion plan |
| under 20 GB | hard stop | do not run new imports |

No bulk import should start if free space is under 40 GB.

## Backup rules

Back up these first:

- `db/mp_evidence_cache.sqlite`
- import manifests
- coverage reports
- merge reports
- source manifests

Suggested backup name:

```text
backups/story-evidence-collector__YYYY-MM-DD__manual-snapshot.tar.zst
```

Backups should include a short manifest explaining what is inside the archive.

## Import-log rules

Every importer should write a log under:

```text
logs/imports/
```

Suggested log file pattern:

```text
logs/imports/YYYY-MM-DD__<import-name>__<run-id>.log
```

Each log should include:

- import name
- start time
- end time
- source system
- input path
- output path
- row count
- error count
- warning count
- network access used: yes/no
- Git commit or script version if available

## Evidence traceability rules

Every normalised vote row should be traceable back to raw evidence.

At minimum, keep:

- `source_system`
- `source_path` or `source_url`
- `source_id`
- `import_run_id`
- `parser_version`
- `source_capture_date`

Historic rows should keep conservative quality flags such as:

```text
meaning_quality: needs_review
```

Do not infer political meaning from a raw historic row unless the motion meaning has been separately reviewed.

## Current project boundary

The current MP pipeline has:

- Commons Votes API available-source records from 2016 onward
- one ready ParlParse batch: `parlparse_2003_01`
- no valid full-career claim yet
- unresolved 1983-2001 source gap

The server archive plan does not change that coverage. It only creates a safer place to store evidence.

## Next implementation issue

After this documentation issue, the next server-side implementation issue should be:

```text
MP v2.5 — Build server evidence cache importer
```

That issue should create a controlled importer that can:

- write raw source files under `/srv/story-evidence-collector/raw/`
- write or update `/srv/story-evidence-collector/db/mp_evidence_cache.sqlite`
- write import logs under `/srv/story-evidence-collector/logs/imports/`
- generate coverage reports under `/srv/story-evidence-collector/reports/coverage/`
- refuse to run if available disk space is below the agreed threshold

## Hard limits

- Do not put raw evidence files in GitHub.
- Do not put SQLite database files in GitHub.
- Do not put server secrets in GitHub.
- Do not store the archive under `public_html`.
- Do not make raw evidence public by default.
- Do not start bulk downloads before the importer and logging rules exist.

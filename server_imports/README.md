# Server Evidence Cache Importer

## Purpose

This folder contains the first controlled server-side importer machinery for the MP evidence pipeline.

It follows the project rule:

```text
GitHub stores the machinery.
The Webmin server stores the evidence.
```

The files in this folder are code, schema, documentation, and example configuration only. They must not include raw evidence files, SQLite databases, server secrets, private keys, or downloaded source archives.

## Server archive root

The importer is designed for this private server path:

```text
/srv/story-evidence-collector/
```

Expected server layout:

```text
/srv/story-evidence-collector/
  raw/
  db/
  reports/
    review-queues/
  logs/
    imports/
    validation/
  backups/
```

## Files

```text
server_imports/README.md
server_imports/mp_evidence_cache_schema.sql
server_imports/build_server_evidence_cache.py
server_imports/build_january_2003_vote_review_queue.py
server_imports/january_2003_vote_review_queue_schema.json
server_imports/example_config.example.json
```

## What the first importer does

The first version is deliberately cautious. It can:

- check that the archive root exists
- check that the requested paths stay inside the archive root
- check the current user
- check write access to `logs/imports/`
- check available disk space before writing
- create or validate the SQLite schema path
- write an import log
- run in dry-run mode by default

It does not fetch data from the web.

It does not run bulk downloads.

It does not put raw evidence or database files into GitHub.

## Dry-run first

Run as the project-only server user:

```bash
sudo -iu storyevidence
cd /path/to/story-evidence-collector
python3 server_imports/build_server_evidence_cache.py --config server_imports/example_config.example.json
```

Dry-run is the default. It should report checks and write a log if `logs/imports/` is writable.

## Apply mode

Apply mode may initialise the SQLite database schema in the server archive:

```bash
python3 server_imports/build_server_evidence_cache.py \
  --config server_imports/example_config.example.json \
  --apply \
  --init-db
```

Use apply mode only after dry-run passes.

## Safety boundaries

The importer must refuse to write outside:

```text
/srv/story-evidence-collector/
```

It must not require root. It should run as:

```text
storyevidence
```

It should stop if free disk space is below the configured threshold.

Default minimum free space:

```text
40 GB
```

## GitHub boundary

Do not commit these to GitHub:

```text
*.sqlite
*.sqlite-wal
*.sqlite-shm
/srv/story-evidence-collector/raw/
/srv/story-evidence-collector/backups/
/srv/story-evidence-collector/reports/review-queues/
.env
*.pem
*.key
id_ed25519
```

## Next step after this issue

After the importer skeleton is merged, the next safe step is to test it on the server as `storyevidence` and confirm that it can create the SQLite schema and write an import log without touching public web folders.

## Controlled seed import

The importer can check or import one small local seed rows file. Source-shaped batch rows may be paired with their reviewed batch manifest.

Dry-run seed check:

```bash
python3 server_imports/build_server_evidence_cache.py \
  --config server_imports/example_config.example.json \
  --seed-id parlparse_2003_01 \
  --seed-rows /path/to/local/parlparse_2003_01_rows.json \
  --seed-manifest /path/to/local/parlparse_2003_01_manifest.json
```

Apply seed import:

```bash
python3 server_imports/build_server_evidence_cache.py \
  --config server_imports/example_config.example.json \
  --seed-id parlparse_2003_01 \
  --seed-rows /path/to/local/parlparse_2003_01_rows.json \
  --seed-manifest /path/to/local/parlparse_2003_01_manifest.json \
  --apply
```

### January 2003 shape boundary

The generated ParlParse row artifact is a source-shaped batch:

- `date` is normalised to SQLite `division_date`;
- `recorded_side` is normalised to SQLite `recorded_vote` and `vote_side`;
- `target_mp` and `target_member_id` may be supplied once by the reviewed batch manifest rather than repeated in every source row;
- the original row is retained unchanged in `source_trace`;
- ParlParse `meaning_quality` remains `needs_review`.

The rows file is generated locally and is not a committed evidence artifact. The repository commits the parser, batch plan, manifest fixture, importer machinery and tests.

Seed import rules:

- dry-run is still the default;
- `--apply` is required before database rows are written;
- the rows and manifest files must already exist locally;
- the manifest batch identity must match the selected seed ID;
- no web fetch or bulk import is performed;
- skipped rows are counted and reported;
- database files, logs, generated rows, raw evidence and server output must not be committed.

## January 2003 vote-review queue

The queue builder reads the accepted SQLite cache without modifying it and creates deterministic private JSON and Markdown packets:

```bash
python3 server_imports/build_january_2003_vote_review_queue.py \
  --config server_imports/example_config.example.json
```

The example configuration selects January 2003, expects 33 rows and writes beneath:

```text
/srv/story-evidence-collector/reports/review-queues/january-2003/
```

Queue rules:

- SQLite is opened with `mode=ro` and `PRAGMA query_only`;
- all matched rows must belong to one target MP unless one is selected explicitly;
- all records must retain `meaning_quality: needs_review`;
- source trace, source URL, source XML URL and evidence status are copied without reinterpretation;
- reviewer-decision fields are blank;
- technical states are limited to recorded Aye, recorded No and not recorded;
- incomplete, contradictory or source-ambiguous rows stop generation;
- existing output is not replaced unless `--overwrite` is supplied;
- the real 33-row packet remains on the private server and must not be committed.

See `docs/january-2003-vote-review-protocol.md` for the evidence standard, later human-review decisions and stop rule.

Run the disposable regression proof:

```bash
python3 scripts/test_january_2003_vote_review_queue.py
```

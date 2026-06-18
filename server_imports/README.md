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
.env
*.pem
*.key
id_ed25519
```

## Next step after this issue

After the importer skeleton is merged, the next safe step is to test it on the server as `storyevidence` and confirm that it can create the SQLite schema and write an import log without touching public web folders.

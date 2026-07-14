# Read-only server inventory

## Purpose

`server_imports/audit_server_state.py` reports the live state of the private Story Evidence Collector archive without modifying it.

It checks:

- archive folders, ownership and permissions
- free disk space
- raw-evidence area file counts and stored size
- SQLite file metadata and SHA-256
- SQLite `PRAGMA quick_check`
- database tables, columns and row counts
- source-system counts
- vote-date coverage
- `meaning_quality` counts
- January 2003 seed-row existence, checksum and validation summary
- recent import logs, validation logs and backups
- repository branch, commit and working-tree status

It does not:

- use the network
- fetch or import evidence
- write to SQLite
- change permissions
- pull repository changes
- print raw evidence contents
- delete, move or rename files

## Run from the server checkout

Run as the project user:

```bash
sudo -iu storyevidence
cd /home/storyevidence/story-evidence-collector
python3 server_imports/audit_server_state.py
```

The report is printed as Markdown to the terminal.

For JSON:

```bash
python3 server_imports/audit_server_state.py --format json
```

## Save a report deliberately

The script itself does not create files. Shell redirection may be used when a reviewed report file is wanted:

```bash
python3 server_imports/audit_server_state.py \
  > /home/storyevidence/SERVER_EVIDENCE_INVENTORY.md
```

Keep the report outside public web folders. Review it before copying any summary to GitHub.

## Expected paths

```text
Archive root: /srv/story-evidence-collector
Repository:   /home/storyevidence/story-evidence-collector
Database:     /srv/story-evidence-collector/db/mp_evidence_cache.sqlite
Seed rows:    /home/storyevidence/story-evidence-collector/parlparse_batches/parlparse_2003_01_rows.json
```

Alternative locations can be inspected explicitly:

```bash
python3 server_imports/audit_server_state.py \
  --archive-root /srv/story-evidence-collector \
  --repo-root /home/storyevidence/story-evidence-collector
```

## Interpretation rule

The inventory proves only what files and normalised rows currently exist. It does not prove that source coverage is complete, current, correctly interpreted or publication-ready.

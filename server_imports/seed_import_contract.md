# Seed Import Contract

## Purpose

This note defines the first controlled seed import before any code writes are added.

The first seed should be one small local rows file only.

Preferred seed name:

```text
parlparse_2003_01
```

## Required command shape

The seed importer should accept:

```text
--config server_imports/example_config.example.json
--seed-id parlparse_2003_01
--rows PATH_TO_LOCAL_ROWS_JSON
--apply
```

Without `--apply`, the importer should run as dry-run only.

## Required row handling

The importer should accept either:

- a JSON list of row objects
- a JSON object containing `rows`, `vote_rows`, `items`, or `data`

Each usable row must have:

```text
division_id
division_date
target_mp
```

Rows missing those fields should be skipped with a validation message.

## Required database writes

For each usable row, the importer should write or reuse:

```text
sources
imports
members
divisions
member_votes
validation_messages
```

Historic ParlParse rows must keep:

```text
meaning_quality: needs_review
```

## Required output

The command should print JSON with:

```text
status
rows_read
rows_written
rows_skipped
warning_count
error_count
network_access_used
```

## Hard limits

- no web fetch
- no bulk download
- no raw archive committed
- no SQLite database committed
- no import logs committed
- no coverage claim beyond the seed

## Stop rule

If the code path is blocked or uncertain, stop at this contract and implement the seed importer in a later narrow PR.

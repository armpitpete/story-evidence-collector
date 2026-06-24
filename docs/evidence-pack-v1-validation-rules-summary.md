# Evidence Pack v1 Validation Rules Summary

This is the short v1 summary of what the evidence pack validator checks.

The validator checks structure only.

It does not decide whether evidence is true, fair, complete, or publishable.

## What v1 validation guarantees

A passing v1 validation means the evidence pack has the expected basic shape.

It means:

- `pack.json` exists.
- `pack.json` is valid JSON.
- `pack.json` can be read even if a Windows tool added a UTF-8 BOM.
- required manifest fields exist.
- unexpected manifest fields are rejected.
- manifest field values have the expected basic type or format.
- `pack_id` follows the readable v1 ID pattern.
- `status`, `editorial_risk`, and `publishability` use allowed values.
- `created_at` and `updated_at` look like ISO date-time strings.
- `records` is an object.
- required `records` fields exist.
- unexpected `records` fields are rejected.
- `outputs` is an object.
- required `outputs` fields exist.
- unexpected `outputs` fields are rejected.
- paths listed in `records` and `outputs` are relative.
- parent-traversal paths are rejected.
- files listed in `records` exist.
- files listed in `outputs` exist.
- `.jsonl` files parse line by line.
- each non-empty `.jsonl` line is a JSON object.
- each `.jsonl` record has a non-empty string `id`.
- JSONL record IDs are unique inside each `.jsonl` file.
- known invalid pack shapes are covered by regression tests.

## What v1 validation does not guarantee

A passing v1 validation does not mean the evidence is good enough to publish.

It does not check:

- whether the evidence is true.
- whether a source is authoritative.
- whether a source has been archived.
- whether the claim is fair.
- whether the interpretation is reasonable.
- whether the evidence pack is complete.
- whether important counter-evidence has been found.
- whether quotations are in full context.
- whether article wording is legally safe.
- whether the final brief is publishable.
- whether a human has reviewed the pack.

Those checks belong to later editorial, provenance, contradiction, and human-review layers.

## Why this matters

The v1 validator protects the foundation.

It makes sure an evidence pack is structured enough to be checked, referenced, and extended safely.

It prevents common structural problems from entering the project, including missing files, unsafe paths, broken JSONL records, missing record IDs, and duplicate record IDs.

This gives later evidence tools a stable base to build on.

## v1 finish line

Evidence Pack v1 validation is good enough when:

- valid packs pass.
- known invalid structures fail.
- unsafe paths are rejected.
- JSONL records are identifiable.
- duplicate JSONL IDs are rejected.
- the validator remains small, readable, and stdlib-only.

v1 is not the final evidence system.

It is the safe structural foundation for the proof-trail system.

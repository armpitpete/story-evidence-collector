# Evidence Pack v1 Current Status

Evidence Pack v1 is complete for controlled structural use.

It provides a stable folder contract, manifest, validators, regression cases, controlled fixtures and a deterministic collector-to-draft-pack bridge. Human review remains mandatory for factual sufficiency, interpretation and publication.

## Current state

Evidence Pack v1 includes:

- a documented pack folder structure;
- a machine-readable `pack.json` manifest schema;
- single-pack and all-pack validators;
- GitHub Actions validation;
- validator failure regression tests;
- path traversal protection;
- JSONL parsing and record ID checks;
- duplicate ID checks within files and across a pack;
- cross-reference checks between sources, claims, evidence, authority records, timeline records and denial checks;
- optional Power Profile chart validation;
- six controlled committed packs;
- a deterministic collector-to-draft-pack integration bridge.

Structural validation proves that records are well formed and references resolve. It does not prove that evidence is true, complete, fair or publication-ready.

## Controlled packs

The committed Evidence Pack fixtures are:

1. `2026-06-22-example-topic`
2. `2026-06-24-story-evidence-collector-foundation`
3. `2026-06-25-code-of-practice-statistics-method`
4. `2026-06-25-power-profile-generic-leadership-mp`
5. `2026-06-26-the-politics-of-calling-people-ordinary`
6. `2026-06-27-west-built-cheap-china-system`

The two TWIS article/sandbox packs demonstrate repeated use of the same structure with article drafts, external public sources, source-authority records, claims, evidence, search diaries, negative evidence, timelines, denial checks, human review and output briefs.

They remain controlled research fixtures. Their presence does not make an article publishable.

## Collector integration

The collector-to-Evidence-Pack bridge is documented in `docs/collector-to-evidence-pack-v1.md`.

It accepts bounded collector source-record JSON and creates a complete pack skeleton containing:

- source records;
- one search diary record;
- one pending human-review record;
- empty authority, claim, evidence, negative-evidence, timeline and denial-check files;
- explicit draft-only output briefs.

The bridge forces:

```text
status: draft
publishability: not_ready
human_review_required: true
```

It does not generate claims, evidence conclusions, authority ratings, contradictions or publication approval.

The controlled regression fixture uses five external source URLs already recorded in `2026-06-27-west-built-cheap-china-system`.

## Validation state

Run:

```bash
python scripts/validate_all_evidence_packs.py
python scripts/test_evidence_pack_validator_failures.py
python scripts/test_collector_to_evidence_pack.py
```

Expected all-pack result:

```text
All evidence packs passed validation. Count: 6
```

The collector bridge regression additionally proves:

- deterministic byte-identical generation;
- five source URLs preserved;
- no generated claims or evidence conclusions;
- fixed draft and `not_ready` state;
- duplicate and missing URL rejection;
- overwrite protection;
- successful validation by the existing Evidence Pack validator.

## Completion boundary

Evidence Pack v1 foundation is complete for controlled repository use.

Further validator expansion requires a specific failure exposed by real use. New research should use the existing structure rather than create competing pack formats.

Work that remains outside Evidence Pack structural completion includes:

- human source-authority assessment;
- claim and evidence writing;
- contradiction analysis;
- legal and reputational review;
- publication decisions;
- archive-link and source-availability checking;
- evidence completeness judgements.

## Working rule

```text
Collect sources.
Create or update one pack.
Validate structure.
Review evidence manually.
Record uncertainty.
Publish only after explicit human approval.
```

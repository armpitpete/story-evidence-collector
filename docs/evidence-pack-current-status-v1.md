# Evidence Pack v1 Current Status

Evidence Pack v1 is now complete enough for controlled use.

The current priority is to use the pack system on real TWIS-style evidence work, not to keep expanding validator infrastructure.

## Current state

Evidence Pack v1 now has:

- a documented pack folder structure.
- a manifest schema for `pack.json`.
- a single-pack validator.
- an all-pack validator.
- GitHub Actions validation.
- validator failure regression tests.
- path traversal protection.
- JSONL record ID checks.
- duplicate record ID checks.
- cross-reference checks between sources, claims, evidence, authority records, timeline records, and denial checks.
- optional Power Profile chart validation.

This is enough to support controlled evidence-pack use.

## Completed controlled packs

The fixture evidence packs now include:

- `2026-06-22-example-topic`
- `2026-06-24-story-evidence-collector-foundation`
- `2026-06-25-code-of-practice-statistics-method`
- `2026-06-25-power-profile-generic-leadership-mp`
- `2026-06-26-the-politics-of-calling-people-ordinary`

The TWIS pack for `the-politics-of-calling-people-ordinary` is the first controlled TWIS article/sandbox pack.

It now includes:

- one TWIS article-draft source.
- one external ONS public statistics source.
- source records.
- source authority mapping.
- claim records.
- evidence items.
- search diary records.
- negative evidence records.
- timeline records.
- denial-check records.
- human-review records.
- output briefs.

## What the latest TWIS pack proves

The latest TWIS pack proves that Evidence Pack v1 can hold:

- an article-draft source.
- one external public source.
- a narrow editorial-method claim.
- a narrow external material-conditions claim.
- traceable links between source, claim, evidence, authority, timeline, denial-check, review, and output records.

It does not prove that the article is ready for publication.

It does not prove every external policy claim.

It does not prove motive.

It remains a controlled sandbox pack.

## Validation state

The expected local validation commands are:

    python scripts\validate_evidence_pack.py fixtures\evidence-packs\2026-06-26-the-politics-of-calling-people-ordinary
    python scripts\validate_all_evidence_packs.py

Expected all-pack result:

    All evidence packs passed validation. Count: 5

## Current stop point

Evidence Pack v1 foundation should be treated as done enough.

Do not add more validator features unless a real pack exposes a specific structural failure.

The system should now move from foundation-building to evidence-pack use.

## Next use-case

The next useful use-case is:

    Create a second controlled real TWIS Evidence Pack, or expand the existing TWIS pack with one more carefully chosen external source.

Preferred next route:

    Use the existing TWIS pack as the model, then create a second small pack for another low-risk TWIS article.

Reason:

- proves the process can be repeated.
- avoids overfitting the system to one article.
- keeps the validator stable.
- tests whether the docs are clear enough for repeated use.

## Working rule

For the next phase:

    One pack. One source addition or one new controlled pack. Validate. Stop.

Avoid turning one pack into a full research project too early.
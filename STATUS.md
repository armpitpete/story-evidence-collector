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
- Exact starting head for this lane: `bee40fe38b25abdf31fefadc2a4684ce4aa3fe31`.
- January 2003 seed-row shape implementation remains complete at merge `4cc7cef44ad92af1ed0f0d15f0fb9e9c063bde2b`.
- Repository Release v1 remains complete and authoritative.
- Backup-and-restore hardening remains complete, with the accepted backup and disposable restore retained on the private server.

## Current lane

January 2003 vote-review queue preparation.

Goal: create a deterministic, read-only human-review queue and protocol for the existing 33 January 2003 member-vote records whose `meaning_quality` remains `needs_review`, without making, inferring or applying any vote-meaning decision.

Authorised implementation scope:

- `server_imports/build_january_2003_vote_review_queue.py`
- `server_imports/january_2003_vote_review_queue_schema.json`
- `server_imports/README.md`
- `server_imports/example_config.example.json`
- `docs/january-2003-vote-review-protocol.md`
- `scripts/test_january_2003_vote_review_queue.py`
- `.github/workflows/january-2003-vote-review-queue-test.yml`

## Done

- Repository Release v1 is complete and authoritative.
- Backup-and-restore hardening is complete.
- The first real backup and disposable restore passed.
- January 2003 seed-row shape reconciliation is complete.
- The accepted restored database baseline remains 33 January 2003 ParlParse divisions, 33 member votes, one member, one source and one import.
- All 33 vote meanings remain `needs_review`.
- Exact current `main` was verified as `bee40fe38b25abdf31fefadc2a4684ce4aa3fe31` before opening this lane.
- No open pull requests existed before this authority branch was created.

## To do

- Define a machine-readable queue schema containing division date and identifiers, motion title, canonical recorded vote, source URL, source XML URL, evidence status, existing `meaning_quality` and blank reviewer-decision fields.
- Add a deterministic read-only queue generator for the existing SQLite evidence cache.
- Preserve source trace and existing evidence values unchanged.
- Separate technical queue states such as recorded Aye, recorded No, not recorded and source ambiguity without assigning political meaning.
- Document the human evidence standard, permitted reviewer decisions, unresolved-state handling and private-server output procedure.
- Keep the real 33-row review packet outside GitHub; commit only the generator, schema, protocol, configuration example and synthetic regression proof.
- Add disposable regression coverage proving deterministic ordering, required fields, blank review decisions, unchanged `needs_review` values and refusal of incomplete or ambiguous records.
- Run the dedicated review-queue test, Repository release validation and Project control.
- Open and review one bounded implementation pull request, then synchronise this authority after merge.

## Next bounded gate

Merge this authority-only activation change after Project control passes, then open one controlled implementation pull request changing only the seven authorised files.

The implementation may generate a local review packet from the accepted private database, but it must not commit the real packet or write any decision back to the database.

## Stop point

Do not review, accept, reject or rewrite any of the 33 vote meanings. Do not infer political meaning from the recorded side, motion title or source metadata. Do not change source coverage, MP coverage, publication state, live database content, backups or the retained disposable restore. Stop after the deterministic review-queue machinery, protocol and regression proof are complete and reviewed.

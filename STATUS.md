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
- Exact starting main for this closure and lane selection: `c7b57bb1d47d934bb0b44901df130d9b65138fb1`.
- PR #204 merged the Jeremy Corbyn current-Parliament explicit-commitments and public-positions baseline from exact reviewed head `ca54308f06e5d69831d353e039e71657104945f0` as merge commit `c7b57bb1d47d934bb0b44901df130d9b65138fb1`.
- Direct comparison confirms exact main is identical to that merge commit.
- The accepted spoken-contributions, written-questions, identity-and-career, roles-and-committees, current-financial-interests, regulated-donee-donations, outside-work/company-links, Complete MP Report fixture, Complete MP Portfolio view, Repository Release and Project Control baselines remain authoritative.

## Closed lane

Jeremy Corbyn current-Parliament explicit commitments and public positions baseline.

The bounded baseline is complete within its declared source, date and statement-form contract. Closure does not mean an exhaustive position history, publication approval or completion of the canonical section.

Canonical section:

- `public_positions_over_time`

The accepted baseline records:

- 8 accepted source documents or pages;
- 109 reviewed candidate occurrences;
- 48 accepted statement occurrences;
- 8 explicit personal commitments;
- 0 conditional personal commitments;
- 8 collective commitments;
- 32 public positions;
- 19 unresolved statement forms;
- 42 excluded candidates;
- 0 duplicate accepted record IDs;
- accepted dates from `2024-07-18` through `2026-07-16`;
- fixed capture SHA-256 `fc5651b9f5647bcbfee822121f3188b0438fc826ad604351d044a8144e3df3db`.

PR #204 changed exactly:

- `.github/workflows/jeremy-corbyn-current-parliament-commitments-public-positions-test.yml`
- `docs/jeremy-corbyn-current-parliament-commitments-and-public-positions-source-note-v1.md`
- `fixtures/complete-mp-reports/jeremy-corbyn-fixture-v1.json`
- `research/complete-mp-reports/jeremy-corbyn/current-parliament-commitments-and-public-positions-v1.json`
- `scripts/test_jeremy_corbyn_current_parliament_commitments_and_public_positions_v1.py`

Before merge, all twelve required workflows passed at the exact implementation head:

- Project Control;
- Repository Release validation;
- Complete MP Report fixture test;
- Complete MP Portfolio view test;
- commitments and public positions test;
- spoken contributions test;
- written questions test;
- identity and career test;
- roles and committees test;
- current financial interests test;
- regulated donee donations test;
- current outside-work and company-links test.

The closed baseline:

- preserves exact quotations and surrounding context;
- preserves personal versus collective agency;
- creates no claim, interpretation or relationship record;
- creates no delivery, fulfilment, broken-promise, reversal, contradiction, consistency or hypocrisy assessment;
- leaves `public_positions_over_time` `partial`;
- leaves `changes_and_contradictions` unchanged and human-review-required;
- keeps the report `not_ready`, human-review-required and unauthorised for public output.

## Current lane

Jeremy Corbyn current-Parliament Early Day Motions tabled by him.

This lane is selected because the accepted fixture identifies Early Day Motions as an unresolved adjacent parliamentary-record type, and UK Parliament maintains a dedicated official Early Day Motions publication with a current-member tabled-by filter.

The lane records parliamentary motion activity only. It does not convert motion text into a commitment or public-position record, assess support, infer ideology or compare any motion with later conduct.

## Date and identity boundary

- Parliament beginning `2024-07-04`;
- Jeremy Corbyn, UK Parliament member ID `185`;
- motions returned by the official current-member `Tabled by Member` filter for Jeremy Corbyn;
- one declared fixed UTC capture timestamp;
- no pre-4-July-2024 motion history in this lane.

## Accepted source boundary

Primary official source only:

- UK Parliament Early Day Motions publication: `https://edm.parliament.uk/`;
- the official member-filtered result pages for member ID `185`;
- each linked official individual motion page;
- official page metadata and text captured or fixed by checksum.

Search-engine results, snippets, media reports, member websites, social-media posts, third-party trackers and paraphrases are navigation evidence only and may not become accepted records.

## Record boundary

The lane may capture only records officially attributed as tabled by Jeremy Corbyn.

For each accepted official record, preserve where available:

- stable repository record ID;
- parliamentary session;
- EDM number and any official suffix;
- title;
- date tabled;
- full official motion text;
- official tabled-by member identity;
- party and constituency exactly as displayed at capture;
- official URL;
- prayer, amendment, withdrawn or other official record-type/status labels;
- signature count as a dated snapshot only;
- capture timestamp;
- source checksum;
- limitations and unresolved fields.

The lane must distinguish:

- a motion tabled by Jeremy Corbyn;
- a motion tabled by another member and merely signed by Jeremy Corbyn;
- an amendment or other separately labelled record;
- an original motion;
- a withdrawn record;
- a current snapshot from a historical fact.

Motions merely signed by Jeremy Corbyn but tabled by another member are outside this first lane. Signature count must not be presented as support quality, influence, importance or outcome.

## Interpretation exclusions

This lane must create no:

- topic, ideology, sentiment, personality or motive classification;
- commitment or public-position promotion by implication;
- delivery or fulfilment assessment;
- contradiction, consistency or hypocrisy assessment;
- importance, influence, effectiveness or success judgement;
- legal, ethical or reputational conclusion;
- relationship record;
- publication authority.

Absence from the official result set is not evidence that no other motion, amendment, signature or parliamentary action existed.

## First controlled phase

The first phase is a source-interface and fixed-inventory proof only. It must not integrate records into the canonical fixture.

The first implementation PR may change exactly:

- `research/complete-mp-reports/jeremy-corbyn/current-parliament-early-day-motions-source-inventory-v1.json`
- `docs/jeremy-corbyn-current-parliament-early-day-motions-source-note-v1.md`
- `scripts/test_jeremy_corbyn_current_parliament_early_day_motions_source_inventory_v1.py`
- `.github/workflows/jeremy-corbyn-current-parliament-early-day-motions-source-inventory-test.yml`

That proof must:

- resolve the official member-filtered result set at one fixed capture timestamp;
- derive the record count mechanically rather than authorising a count in advance;
- preserve every returned result URL and visible result metadata;
- inspect every linked individual motion page;
- preserve full official text and available official labels by checksum;
- prove pagination completeness;
- reject duplicate stable IDs and duplicate official URLs;
- preserve tabled-by attribution separately from signatures;
- classify prayer, amendment, withdrawn and other record labels only when explicitly displayed;
- record missing or inconsistent fields as unresolved rather than infer them;
- run read-only CI, deterministic validation and `git diff --check`;
- make no canonical fixture, schema, generator, existing packet, existing regression, server or database change.

If the official interface cannot support deterministic complete capture, or neutral later integration would require a schema or generator change, the phase must stop and return for separate authority.

## Deferred work

The following remain explicitly unstarted and unauthorised:

- motions merely signed by Jeremy Corbyn but tabled by another member;
- pre-current-Parliament Early Day Motions;
- canonical fixture integration of Early Day Motions;
- tabled oral questions;
- written statements;
- committee oral evidence;
- future refreshes of completed baselines;
- review of the 19 unresolved statement forms;
- commitment-versus-conduct comparison;
- delivery, fulfilment or broken-promise assessment;
- changes-and-contradictions analysis;
- public-output authorisation.

## Done

- PR #204 was reviewed, passed all twelve required workflows and merged with an exact-head guard.
- The current-Parliament explicit-commitments and public-positions bounded baseline is closed at exact main `c7b57bb1d47d934bb0b44901df130d9b65138fb1`.
- No commitment-versus-conduct, delivery or contradiction work has begun.
- The next lane has been selected as current-Parliament Early Day Motions tabled by Jeremy Corbyn.
- Only the source-interface and fixed-inventory proof is authorised as the first phase.

## To do

- merge this `STATUS.md`-only closure and lane-authority change after Project Control passes;
- from the resulting exact main, open one draft four-file Early Day Motions source-inventory PR;
- verify official interface completeness, deterministic capture and exact four-file scope;
- stop for owner review before any fixture integration or scope expansion.

## Next bounded gate

After this closure and authority change merges, open one draft current-Parliament Early Day Motions source-interface and fixed-inventory PR from the exact resulting main. Change exactly the four authorised files, make no canonical fixture change, and stop if the official interface cannot provide a deterministic complete tabled-by-member capture.

## Stop point

Do not begin commitment-versus-conduct comparison, delivery assessment, fulfilment assessment or contradiction analysis; review or reclassify the 19 unresolved statement forms; include motions merely signed but not tabled by Jeremy Corbyn; include pre-4-July-2024 material; integrate Early Day Motions into the canonical fixture; change schema or generator code; weaken or replace any accepted baseline; access or mutate the private server or SQLite; mark a partial section complete; mark the report publishable; or authorise public output.
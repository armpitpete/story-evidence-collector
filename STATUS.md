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
- Exact starting main for this closure and lane selection: `a287ce0054a23821c222b8046c4058b4e5fd6210`.
- PR #218 merged the Jeremy Corbyn current-Parliament Early Day Motions source-interface and fixed-inventory proof from exact reviewed head `5db8be0706c8ea2b55c5f2e2e45099cb541f8e80` as merge commit `a287ce0054a23821c222b8046c4058b4e5fd6210`.
- Direct comparison confirms exact main is identical to that merge commit.
- All previously accepted Complete MP Report baselines remain authoritative.

## Closed lane

Jeremy Corbyn current-Parliament Early Day Motions tabled by him — source-interface and fixed-inventory proof.

The bounded proof is complete within its declared official-source, date, member-role and pagination contract. Closure does not integrate the motions into the canonical fixture, classify their text as commitments or positions, assess support or outcome, or authorise publication.

The accepted proof records:

- Jeremy Corbyn, UK Parliament member ID `185`;
- Parliament beginning `2024-07-04`;
- fixed capture timestamp `2026-07-22T07:46:43Z`;
- six motions officially returned as tabled by Jeremy Corbyn;
- sessions `2024-26` and `2026-27`;
- accepted tabled dates from `2024-09-02` through `2026-06-23`;
- one API page with `Skip=0`, `Take=100`, `Total=6` and `GlobalTotal=6`;
- exact official motion IDs `62446`, `63037`, `64576`, `65102`, `65889` and `66149`;
- canonical capture SHA-256 `4558d82deddbee2168449d64aa4998672ae08faf212ac1338ce17fb8bab0304a`.

PR #218 changed exactly:

- `research/complete-mp-reports/jeremy-corbyn/current-parliament-early-day-motions-source-inventory-v1.json`
- `docs/jeremy-corbyn-current-parliament-early-day-motions-source-note-v1.md`
- `scripts/test_jeremy_corbyn_current_parliament_early_day_motions_source_inventory_v1.py`
- `.github/workflows/jeremy-corbyn-current-parliament-early-day-motions-source-inventory-test.yml`

Before merge, the exact implementation head passed:

- Project Control;
- Repository Release validation;
- Early Day Motions source inventory test, including compilation, fixed checksum validation, supported official API replay, all six detail endpoints, exact four-file enforcement and `git diff --check`.

The closed proof:

- excludes motions merely signed or secondarily sponsored by Jeremy Corbyn;
- excludes records tabled before 4 July 2024;
- preserves full official motion text and explicit primary-sponsor attribution;
- preserves signature totals only as dated snapshots;
- leaves page-level prayer and whole-motion-withdrawal fields unresolved where not explicitly labelled;
- creates no claim, interpretation or relationship record;
- creates no commitment, public-position, delivery, fulfilment, contradiction, importance, influence or success assessment;
- makes no canonical fixture, schema, generator, server or database change;
- creates no public-output authority.

## Current lane

Neutral canonical fixture integration of the six accepted current-Parliament Early Day Motions.

This lane is selected because the official inventory is now mechanically complete and the existing Complete MP Report schema can represent each motion without a schema or generator change. The canonical `speeches_and_questions` section already contains adjacent written-question and spoken-contribution facts, and the schema permits neutral `fact_type: other` records.

The lane integrates accepted parliamentary activity only. It must not convert motion text into a commitment or public-position record, infer ideology or motive, assess support or outcome, or compare a motion with later conduct.

## Fixed integration authority

The sole research authority for this lane is:

- inventory ID `jeremy-corbyn-current-parliament-early-day-motions-source-inventory-v1`;
- repository packet `research/complete-mp-reports/jeremy-corbyn/current-parliament-early-day-motions-source-inventory-v1.json`;
- capture SHA-256 `4558d82deddbee2168449d64aa4998672ae08faf212ac1338ce17fb8bab0304a`;
- exact accepted motion IDs `62446`, `63037`, `64576`, `65102`, `65889` and `66149`.

No live refresh, new motion, changed signature count or later source state may enter this integration lane.

## Canonical record contract

The integration may add exactly one canonical source record for the fixed packet and exactly six canonical facts.

Required source ID:

- `source-uk-parliament-corbyn-current-parliament-early-day-motions-2026-07-22`

Required fact IDs:

- `fact-early-day-motion-62446`
- `fact-early-day-motion-63037`
- `fact-early-day-motion-64576`
- `fact-early-day-motion-65102`
- `fact-early-day-motion-65889`
- `fact-early-day-motion-66149`

Each fact must:

- use section `speeches_and_questions`;
- use `fact_type: other`;
- preserve the official motion ID, EDM number, title and tabled date;
- identify Jeremy Corbyn only as the official primary sponsor or tabled-by member;
- reference the one fixed inventory source;
- use neutral factual wording;
- use high confidence and verified or source-recorded evidence status;
- keep the full motion text, official URLs, signature snapshot and unresolved fields traceable to the fixed packet rather than reinterpreting them;
- create no claim, interpretation or relationship record.

The `speeches_and_questions` section summary and `fact_ids` may be updated only to acknowledge the six integrated EDM records. The section must remain `partial`.

The report must remain:

- `not_ready`;
- human-review-required;
- unauthorised for public output.

## Exact first-phase file scope

The first integration PR may change exactly:

- `fixtures/complete-mp-reports/jeremy-corbyn-fixture-v1.json`
- `scripts/test_jeremy_corbyn_current_parliament_early_day_motions_fixture_integration_v1.py`
- `.github/workflows/jeremy-corbyn-current-parliament-early-day-motions-fixture-integration-test.yml`

No other file is authorised.

The existing Complete MP Report fixture and Complete MP Portfolio workflows are expected to run because the canonical fixture changes. Their source files must not be edited in this lane.

## Required deterministic proof

The dedicated regression must:

- load the fixed source inventory and canonical fixture;
- verify the fixed inventory ID and capture checksum;
- derive the accepted six-record set from the fixed packet;
- require one and only one canonical source record for the packet;
- require a one-to-one mapping from the six official motion IDs to the six required fact IDs;
- require all six facts in `speeches_and_questions` with `fact_type: other`;
- verify exact EDM number, title, tabled date, official motion ID and source reference for every fact;
- reject missing, duplicate or additional EDM facts;
- reject any EDM-derived claim, interpretation or relationship record;
- reject commitment, public-position, delivery, fulfilment, contradiction, ideology, motive, importance, influence, effectiveness or success language;
- require the section to remain `partial`;
- require publication to remain `not_ready`, human-review-required and unauthorised;
- run the existing Complete MP Report generator regression;
- run the existing Complete MP Portfolio view regression;
- enforce the exact three-file scope;
- run `git diff --check`.

If neutral integration cannot be completed within the existing schema and generator, or if any accepted record requires interpretive classification, the lane must stop and return for separate authority.

## Interpretation exclusions

This lane must create no:

- commitment or public-position promotion;
- topic, ideology, sentiment, personality or motive classification;
- delivery or fulfilment assessment;
- contradiction, consistency or hypocrisy assessment;
- importance, influence, effectiveness or success judgement;
- legal, ethical or reputational conclusion;
- relationship record;
- publication authority.

A motion's text is an official parliamentary record. Its presence in the fixture does not establish that the motion was debated, adopted, implemented, influential or representative of all later conduct.

## Deferred work

The following remain explicitly unstarted and unauthorised:

- any schema or generator change for Early Day Motions;
- any live refresh of the fixed EDM inventory;
- motions merely signed by Jeremy Corbyn but tabled by another member;
- pre-current-Parliament Early Day Motions;
- tabled oral questions;
- written statements;
- committee oral evidence;
- review of the 19 unresolved commitment or position statement forms;
- commitment-versus-conduct comparison;
- delivery, fulfilment or broken-promise assessment;
- changes-and-contradictions analysis;
- public-output authorisation.

## Done

- PR #218 was reviewed, passed all required workflows and merged with an exact-head guard.
- The current-Parliament Early Day Motions source-interface and fixed-inventory proof is closed at exact main `a287ce0054a23821c222b8046c4058b4e5fd6210`.
- Six official tabled-by-member records are fixed and checksum-bound.
- No canonical fixture integration, interpretation, conduct comparison, delivery or contradiction work has begun.
- The next lane has been selected as neutral canonical fixture integration of those six fixed records.
- The first phase is limited to one fixture, one dedicated regression and one read-only workflow.

## To do

- merge this `STATUS.md`-only closure and lane-authority change after Project Control passes;
- from the resulting exact main, open one draft three-file EDM fixture-integration PR;
- prove exact one-to-one integration and all exclusion boundaries;
- require the existing fixture and portfolio regressions to remain green;
- stop for owner review before promotion or merge.

## Next bounded gate

After this closure and authority change merges, open one draft current-Parliament Early Day Motions canonical fixture-integration PR from the exact resulting main. Change exactly the three authorised files, integrate only the six checksum-bound records as neutral `fact_type: other` facts in `speeches_and_questions`, make no schema or generator change, and stop if neutral integration requires interpretation or scope expansion.

## Stop point

Do not begin commitment-versus-conduct comparison, delivery assessment, fulfilment assessment or contradiction analysis; review or reclassify the 19 unresolved statement forms; include motions merely signed but not tabled by Jeremy Corbyn; include pre-4-July-2024 material; refresh the fixed EDM inventory; change schema or generator code; weaken or replace any accepted baseline; access or mutate the private server or SQLite; mark a partial section complete; mark the report publishable; or authorise public output.

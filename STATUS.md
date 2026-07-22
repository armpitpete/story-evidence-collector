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
- Exact current main: `dbb30decff8029b4e775d7faf33194fa6800fe20`
- PR #220 merged at exact reviewed head `bbf0a5bd457c8f79acdd993140c08c7704a9d9c3`.
- Merge commit: `dbb30decff8029b4e775d7faf33194fa6800fe20`.
- All previously accepted Complete MP Report baselines remain authoritative.

## Closed lane

The current-Parliament Early Day Motions canonical fixture-integration lane is complete.

The merged five-file scope was exactly:

- `.github/workflows/jeremy-corbyn-current-parliament-early-day-motions-fixture-integration-test.yml`
- `fixtures/complete-mp-reports/jeremy-corbyn-fixture-v1.json`
- `scripts/test_jeremy_corbyn_current_parliament_commitments_and_public_positions_v1.py`
- `scripts/test_jeremy_corbyn_current_parliament_early_day_motions_fixture_integration_v1.py`
- `scripts/test_jeremy_corbyn_current_parliament_spoken_contributions_v1.py`

The completed lane:

- added one checksum-bound canonical source for inventory `jeremy-corbyn-current-parliament-early-day-motions-source-inventory-v1`;
- bound the source to capture SHA-256 `4558d82deddbee2168449d64aa4998672ae08faf212ac1338ce17fb8bab0304a`;
- added exactly six neutral `fact_type: other` records for official motion IDs `62446`, `63037`, `64576`, `65102`, `65889` and `66149`;
- placed those facts only in `speeches_and_questions`;
- preserved that section as `partial`;
- preserved publication as `not_ready`, human-review-required and unauthorised;
- created no EDM-derived claim, interpretation or relationship record;
- created no commitment, public-position, delivery, fulfilment, contradiction, ideology, motive, importance, influence, effectiveness or success assessment.

## Historical-regression repairs completed

The commitments/public-positions and spoken-contributions regressions now recognise only the exact authorised EDM extension while retaining their complete accepted historical baselines.

The repairs:

- require the live fixture to equal the accepted fixture at exact commit `426920b968927a4293b595eeda726d1b57d388bf` plus only the exact EDM source, six EDM facts and authorised `speeches_and_questions` extension;
- execute the complete accepted historical regression scripts from that fixed commit;
- retain exact source, fact, section, gap, packet, count, hash, output and publication assertions;
- do not use broad prefix exclusions or relaxed collection comparisons;
- reject every unrelated fixture change.

## Closure proof

At exact PR head `bbf0a5bd457c8f79acdd993140c08c7704a9d9c3`, the complete triggered matrix passed:

- Project Control;
- Repository Release validation;
- Early Day Motions fixture integration;
- commitments and public positions;
- spoken contributions;
- Complete MP Report fixture;
- Complete MP Portfolio view;
- written questions;
- identity and career;
- roles and committees;
- current financial interests;
- regulated donee donations;
- current outside work and company links.

The dedicated EDM workflow also passed:

- compilation;
- fixed-inventory identity and SHA-256 verification;
- exact six-record neutral fixture reconciliation;
- Complete MP Report fixture regression;
- Complete MP Portfolio regression;
- exact five-file PR #220 scope enforcement;
- `git diff --check`.

PR #220 is closed and merged. Current `main` is exactly the merge commit above.

## Next selected lane

One bounded **current-Parliament tabled oral questions source-interface proof** lane is authorised from exact main:

- `dbb30decff8029b4e775d7faf33194fa6800fe20`

This lane exists only to establish whether official UK Parliament first-party interfaces can provide a complete, reproducible inventory of oral questions tabled by Jeremy Corbyn in the current Parliament.

## Exact authorised scope

The lane may create or change exactly:

- `research/complete-mp-reports/jeremy-corbyn/current-parliament-tabled-oral-questions-source-interface-v1.md`
- `scripts/test_jeremy_corbyn_current_parliament_tabled_oral_questions_source_interface_v1.py`
- `.github/workflows/jeremy-corbyn-current-parliament-tabled-oral-questions-source-interface-test.yml`

No other file is authorised.

## Source-interface proof contract

The lane must:

- use only official UK Parliament first-party pages, APIs or downloadable records;
- identify the exact interface or interfaces relevant to oral questions tabled by a named member;
- distinguish tabled oral questions from written questions, answered oral contributions, supplementaries, speeches and Early Day Motions;
- determine the exact member-attribution semantics, including whether the interface identifies the member who tabled or asked the question;
- determine current-Parliament date boundaries and how the interface represents sessions;
- test pagination, result counts, ordering, filtering, duplication and completeness behaviour;
- record exact request URLs, parameters, response fields and observed limitations;
- state clearly whether a complete reproducible fixed inventory is possible;
- record a zero-result outcome neutrally if the official interface returns no qualifying records;
- provide deterministic regression coverage for the documented interface evidence;
- keep every conclusion limited to source-interface capability and record availability.

## Required proof

Before the lane can close, require:

- the source-interface note to distinguish confirmed behaviour from unresolved behaviour;
- every claimed interface behaviour to be supported by fixed first-party evidence;
- the regression to reject changed interface identity, member semantics, date boundaries, result-count evidence or documented completeness conclusions;
- the workflow to compile and run the regression;
- exact three-file scope enforcement;
- `git diff --check`;
- Project Control and Repository Release validation to pass;
- a draft PR at an exact head for owner review.

If no official interface can establish a complete named-member inventory, the lane must stop with that limitation documented. It must not substitute search-engine results, parliamentary-monitoring sites, manually assembled secondary lists or inference from answered-question pages.

## Explicit exclusions

This lane does not authorise:

- capture of a canonical oral-question inventory beyond the minimum fixed evidence needed to prove interface behaviour;
- canonical fixture integration;
- source or fact records in the Complete MP fixture;
- classification of any oral question as a commitment or public position;
- analysis of content, ideology, motive, importance, influence, effectiveness or outcome;
- comparison with conduct, delivery, fulfilment, contradiction or broken promises;
- changes to the existing written-question, spoken-contribution or EDM records;
- schema, generator, server or database changes;
- completion of any partial report section;
- publication, deployment or public-output authority.

## Deferred work

The following remain explicitly unstarted and unauthorised:

- a fixed tabled-oral-questions inventory;
- canonical fixture integration of oral questions;
- written statements;
- committee oral evidence;
- pre-current-Parliament EDM coverage;
- motions merely signed by Jeremy Corbyn;
- review or reclassification of the 19 unresolved commitment or position statement forms;
- commitment-versus-conduct comparison;
- delivery, fulfilment or broken-promise assessment;
- changes-and-contradictions analysis;
- public-output authorisation.

## Done

- PR #220 merged at exact authorised head.
- The six current-Parliament EDM records are neutrally integrated.
- Both historical-regression guards are repaired without weakening their baselines.
- The complete triggered matrix is green.
- The EDM fixture-integration lane is closed.
- The next bounded source-interface proof lane is selected and authorised.

## Next bounded gate

From exact main `dbb30decff8029b4e775d7faf33194fa6800fe20`, open one draft three-file current-Parliament tabled oral questions source-interface proof PR. Change only the three authorised files, establish the official first-party interface and completeness boundary, run the dedicated and project-control checks, and stop at an exact PR head for owner review.

## Stop point

Do not create a fixed oral-question inventory, integrate any oral-question record into the canonical fixture, modify the existing Complete MP fixture, classify content, begin commitment-versus-conduct comparison, assess delivery or fulfilment, perform contradiction analysis, change schema or generator code, access or mutate the private server or SQLite, mark a partial section complete, mark the report publishable, deploy, or authorise public output.

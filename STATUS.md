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
- Exact starting main for this review and repair authority: `56a83febbac218e5ab5482da67b08c1014e0a949`.
- PR #220 is open and draft from exact base `56a83febbac218e5ab5482da67b08c1014e0a949` at exact reviewed head `0f5538554025193422c642e0a67b155c2fe59f2d`.
- Direct comparison confirms current `main` remains identical to the exact PR base.
- All previously accepted Complete MP Report baselines remain authoritative.

## Current lane

Neutral canonical fixture integration of the six accepted current-Parliament Early Day Motions.

The three-file implementation in draft PR #220 is complete within the authorised integration contract but remains blocked by two pre-existing fixture-preservation regressions. The integration must remain draft and unmerged until the separately authorised guard repair is applied and both regressions pass at a new exact PR head.

## Owner review of PR #220

Owner review was completed at exact head:

- `0f5538554025193422c642e0a67b155c2fe59f2d`

The reviewed PR remains:

- open;
- draft;
- mergeable;
- unmerged;
- based on exact main `56a83febbac218e5ab5482da67b08c1014e0a949`;
- limited at the reviewed head to the three originally authorised implementation files.

Those three files are:

- `fixtures/complete-mp-reports/jeremy-corbyn-fixture-v1.json`
- `scripts/test_jeremy_corbyn_current_parliament_early_day_motions_fixture_integration_v1.py`
- `.github/workflows/jeremy-corbyn-current-parliament-early-day-motions-fixture-integration-test.yml`

The reviewed implementation:

- adds exactly one checksum-bound canonical source for inventory `jeremy-corbyn-current-parliament-early-day-motions-source-inventory-v1`;
- binds the source to capture SHA-256 `4558d82deddbee2168449d64aa4998672ae08faf212ac1338ce17fb8bab0304a`;
- adds exactly six neutral `fact_type: other` records for official motion IDs `62446`, `63037`, `64576`, `65102`, `65889` and `66149`;
- places those facts only in `speeches_and_questions`;
- preserves the section as `partial`;
- preserves publication as `not_ready`, human-review-required and unauthorised;
- creates no EDM-derived claim, interpretation or relationship record;
- creates no commitment, public-position, delivery, fulfilment, contradiction, ideology, motive, importance, influence, effectiveness or success assessment.

No blocking defect was found in the three-file EDM integration itself.

## Validation at the reviewed head

At exact head `0f5538554025193422c642e0a67b155c2fe59f2d`, the following passed:

- Project Control;
- Repository Release validation;
- dedicated Early Day Motions fixture-integration test;
- Complete MP Report fixture test;
- Complete MP Portfolio view test;
- written-questions test;
- identity-and-career test;
- roles-and-committees test;
- current-financial-interests test;
- regulated-donee-donations test;
- current outside-work and company-links test.

The dedicated workflow passed:

- compilation;
- exact fixed-inventory checksum verification;
- exact six-record fixture reconciliation;
- Complete MP Report generator regression;
- Complete MP Portfolio regression;
- exact three-file scope enforcement;
- `git diff --check`.

## Confirmed regression blockers

Two pre-existing regression guards fail only because they do not yet recognise the separately authorised six-EDM fixture addition.

### Commitments and public positions guard

`scripts/test_jeremy_corbyn_current_parliament_commitments_and_public_positions_v1.py` reconstructs the fixture from its historical authority merge, adds only that lane's authorised records and requires whole-fixture equality. It therefore rejects every later separately authorised canonical fixture addition, including the six EDM facts and their one source.

### Spoken contributions guard

`scripts/test_jeremy_corbyn_current_parliament_spoken_contributions_v1.py` preserves hashes for the pre-spoken fixture and already omits later public-position additions, but it does not omit the separately authorised EDM source, six EDM facts and the authorised `speeches_and_questions` summary extension. It therefore rejects the EDM integration despite the spoken baseline remaining unchanged.

These are regression-recognition defects. They are not evidence that the accepted commitments, positions, spoken-contribution or EDM records changed.

## Separately authorised repair

A bounded regression-guard repair is authorised on the existing PR #220 branch after this `STATUS.md` authority change merges.

The repair may change exactly:

- `scripts/test_jeremy_corbyn_current_parliament_commitments_and_public_positions_v1.py`
- `scripts/test_jeremy_corbyn_current_parliament_spoken_contributions_v1.py`

No other repair file is authorised.

The existing three PR #220 implementation files are frozen except for a separately evidenced defect requiring new owner authority. The repair must not alter the fixture, EDM integration regression, EDM workflow, schema, generator, source inventory, source note, server or database.

## Repair contract

The repair must make each legacy guard recognise only the separately authorised EDM integration while preserving its historical baseline checks.

The commitments and public-positions guard must:

- continue to reconstruct and verify the exact accepted commitments/public-positions baseline;
- continue to require the exact 8-source, 48-accepted, 19-unresolved and 42-excluded packet results;
- continue to preserve its exact source, fact, section, gap, publication and output contracts;
- permit only the exact EDM source ID `source-uk-parliament-corbyn-current-parliament-early-day-motions-2026-07-22` as a later authorised source addition;
- permit only the six exact EDM fact IDs as later authorised fact additions;
- permit only the authorised `speeches_and_questions` fact-reference and summary extension;
- reject any other unexpected later source, fact, section, claim, interpretation, relationship, publication or gap change.

The spoken-contributions guard must:

- continue to verify all 306 accepted spoken contributions and their fixed packet, source and preservation hashes;
- continue to recognise the separately accepted public-position additions;
- additionally omit only the exact EDM source, six exact EDM facts and the authorised `speeches_and_questions` EDM extension when reconstructing its pre-spoken preservation boundary;
- continue to reject any change to spoken facts, spoken sources, contribution counts, source hashes, publication state, claims, interpretations or relationships;
- reject any other unexpected later fixture change.

Both repairs must use explicit exact IDs and exact expected values. Broad prefix exclusions, unconstrained filtering, relaxed whole-collection comparisons or removal of historical assertions are forbidden.

## Required proof after repair

At the new exact PR #220 head, require all triggered workflows to complete successfully, including:

- commitments and public positions;
- spoken contributions;
- dedicated Early Day Motions fixture integration;
- Complete MP Report fixture;
- Complete MP Portfolio view;
- Project Control;
- Repository Release validation;
- every other fixture-triggered baseline regression.

The repair must also prove:

- PR #220 contains only its original three implementation files plus the two separately authorised regression files;
- no sixth changed file exists;
- `git diff --check` passes;
- the PR remains draft and unmerged;
- the exact head is recorded for a new owner review.

If either guard cannot be repaired using explicit recognition of the exact authorised EDM additions, stop without weakening the baseline or expanding scope.

## Deferred work

The following remain explicitly unstarted and unauthorised:

- marking PR #220 ready for review;
- merging PR #220;
- any schema or generator change;
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

- PR #220 was reviewed at exact head `0f5538554025193422c642e0a67b155c2fe59f2d`.
- No defect was found in the authorised three-file EDM integration.
- The two failing legacy guards were identified precisely.
- A two-file repair scope and strict non-weakening contract have been selected.
- No PR #220 state change, merge or repair implementation has occurred in this authority change.

## To do

- merge this `STATUS.md`-only repair-authority change after Project Control passes;
- update only the two authorised regression files on the existing PR #220 branch;
- rerun the complete triggered regression matrix;
- stop at the resulting new exact head for owner review;
- do not mark PR #220 ready or merge it.

## Next bounded gate

After this `STATUS.md` authority change merges, apply the bounded two-file regression-guard repair to the existing draft PR #220 branch at reviewed head `0f5538554025193422c642e0a67b155c2fe59f2d`. Change only the two authorised legacy regression files, require both previously failing guards and the entire triggered matrix to pass, verify the resulting five-file PR scope, and stop for owner review at the new exact head.

## Stop point

Do not mark PR #220 ready or merge it; change any file other than the two explicitly authorised regression files during the repair; weaken or delete historical baseline assertions; use broad exclusions that could conceal unrelated future fixture changes; modify the accepted fixture integration; begin commitment-versus-conduct comparison, delivery assessment, fulfilment assessment or contradiction analysis; review or reclassify the 19 unresolved statement forms; refresh or expand the EDM inventory; change schema or generator code; access or mutate the private server or SQLite; mark a partial section complete; mark the report publishable; or authorise public output.

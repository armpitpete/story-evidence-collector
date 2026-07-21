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
- Exact starting head for this clarification: `3bc4b68027efaf1897a1d65f8f5ea02f3233cdb7`.
- The Jeremy Corbyn current-Parliament spoken-contributions baseline and closure remain complete.
- The 306-record spoken baseline, 90-question baseline, identity and career, roles and committees, current financial interests, regulated-donee donations, outside-work/company links, Complete MP Report fixture, Complete MP Portfolio view, Repository Release validation and Project Control remain authoritative.
- PR #213 repaired the populated-position synthetic spoken-regression boundary at exact head `21604bac48ab3c5f371d30c0734f7875cf2ea44a` and merged as `3bc4b68027efaf1897a1d65f8f5ea02f3233cdb7` after every fresh required check passed.

## Current lane

Jeremy Corbyn current-Parliament explicit commitments and public positions baseline.

The lane records only source-verbatim explicit commitments and directly stated public positions attributable to Jeremy Corbyn from `2024-07-04` through the fixed capture timestamp. It does not compare statements with conduct, decide delivery, infer contradiction, classify political character or authorise publication.

Canonical section:

- `public_positions_over_time`

The `changes_and_contradictions` section remains outside this lane and human-review-required.

## Fixed implementation contract

The accepted capture contains:

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
- capture SHA-256 `fc5651b9f5647bcbfee822121f3188b0438fc826ad604351d044a8144e3df3db`.

The implementation must:

- preserve exact quotations and enough surrounding context to prevent changed meaning;
- preserve personal versus collective agency;
- preserve conditions and deadlines only when explicit;
- create no topic, ideology, sentiment, personality, motive, sincerity, importance or truth classification;
- create no delivery, fulfilment, broken-promise, reversal, contradiction, consistency or hypocrisy assessment;
- create no claim, interpretation or relationship record;
- preserve all accepted evidence outside `public_positions_over_time` and its directly related coverage gap;
- leave `public_positions_over_time` `partial`;
- keep the report `not_ready`, human-review-required and unauthorised for public output.

## Exact PR #204 implementation scope

PR #204 is open, draft and unmerged at exact head:

- `ca54308f06e5d69831d353e039e71657104945f0`

Its base is exact main:

- `3bc4b68027efaf1897a1d65f8f5ea02f3233cdb7`

GitHub independently confirms that PR #204 changes exactly:

- `.github/workflows/jeremy-corbyn-current-parliament-commitments-public-positions-test.yml`
- `docs/jeremy-corbyn-current-parliament-commitments-and-public-positions-source-note-v1.md`
- `fixtures/complete-mp-reports/jeremy-corbyn-fixture-v1.json`
- `research/complete-mp-reports/jeremy-corbyn/current-parliament-commitments-and-public-positions-v1.json`
- `scripts/test_jeremy_corbyn_current_parliament_commitments_and_public_positions_v1.py`

No sixth file is authorised in PR #204.

The temporary write-enabled reconciler has been removed. The final lane workflow is read-only and verifies:

- Python compilation;
- the fixed commitments/public-positions regression;
- the preserved spoken-contributions regression;
- the preserved written-question regression;
- the exact five-file scope;
- `git diff --check`.

## Fresh PR #204 regression result

At exact head `ca54308f06e5d69831d353e039e71657104945f0`, the following fresh workflows passed:

- Project Control;
- Repository Release validation;
- Complete MP Report fixture test;
- Complete MP Portfolio view test;
- commitments and public positions test;
- written questions test;
- identity and career test;
- roles and committees test;
- current financial interests test;
- regulated donee donations test;
- current outside-work and company-links test.

The spoken-contributions workflow also passed:

- exact-head checkout;
- Python compilation;
- the complete 306-record spoken-contributions regression;
- the complete 90-question preservation regression.

Its only failing step is its historical final exact-scope guard. That guard currently recognises the original spoken five-file implementation, exact PR #206 and exact PR #213. It does not yet recognise the separately authorised PR #204 five-file commitments/public-positions implementation even though the substantive spoken evidence passes.

PR #204 must remain draft and unmerged until that scope-only conflict is repaired and all twelve fresh workflows are green.

## Authorised PR #204 spoken-workflow scope correction

One separate workflow-only PR may change exactly:

- `.github/workflows/jeremy-corbyn-current-parliament-spoken-contributions-test.yml`

It may alter only the final exact-scope validation. It must:

- retain the original exact spoken five-file implementation allowance unchanged;
- retain the exact PR #206 allowance unchanged;
- retain the exact PR #213 allowance unchanged;
- additionally accept only PR `#204` at exact head `ca54308f06e5d69831d353e039e71657104945f0` when its changed-file set is exactly the five authorised PR #204 paths listed above;
- reject the allowance if the PR number, head SHA or changed-file set differs;
- retain read-only permissions;
- retain exact-head checkout;
- retain Python setup and compilation;
- retain the full spoken-contributions regression;
- retain the written-question regression;
- retain the evaluated PR number, head SHA and changed-file diagnostics;
- retain `git diff --check`;
- create no branch wildcard, title test, general five-file allowance, general one-file allowance, `continue-on-error`, skipped test, reduced permission boundary or silent success path;
- make no change to a packet, source note, fixture, schema, generator, regression script, publication state or any other workflow.

The workflow-only correction may merge after:

- Project Control passes;
- GitHub confirms exactly one changed file;
- the patch is verified to contain only the bounded PR #204 number/head/file-set allowance.

The inherited spoken scope guard may reject the workflow-repair PR itself. That expected self-rejection is not authority to weaken or skip any substantive test.

After the workflow-only correction merges, PR #204 must be retriggered without changing exact head `ca54308f06e5d69831d353e039e71657104945f0`.

PR #204 may be marked ready for review only when:

- all twelve fresh required workflows pass;
- GitHub still confirms exactly the five authorised files;
- the head remains exactly `ca54308f06e5d69831d353e039e71657104945f0`.

PR #204 must then stop for owner review and remain unmerged.

## Done

- The fixed source inventory and candidate capture are complete.
- The schema represents the neutral position records without schema or generator change.
- Both spoken-regression prerequisite repairs are merged.
- PR #204 has been reconciled against exact repaired main.
- The fixed packet, source note, fixture integration, deterministic regression and final read-only CI are restored in exactly five files.
- Eleven of twelve fresh required workflows pass.
- The substantive spoken and written-question regressions pass inside the remaining workflow.
- The remaining failure is isolated to the spoken workflow's historical final exact-scope guard.
- PR #204 remains draft and unmerged.
- The commitment-versus-conduct comparison remains unstarted.

## To do

- merge this `STATUS.md`-only clarification after Project Control passes;
- open one workflow-only PR implementing the exact PR #204 number/head/file-set allowance;
- verify its exact one-file scope and bounded patch;
- merge that workflow-only correction with an exact-head guard;
- retrigger PR #204 at unchanged head `ca54308f06e5d69831d353e039e71657104945f0`;
- verify all twelve fresh workflows pass and the exact five-file set remains unchanged;
- mark PR #204 ready for review;
- stop for owner review without merging PR #204.

## Next bounded gate

Merge this `STATUS.md`-only clarification after Project Control passes. Then open and merge one workflow-only correction that adds only the exact PR #204/head-SHA/five-file allowance described above. Do not change or mark PR #204 ready until every fresh required workflow is green.

## Stop point

Do not merge PR #204; change its exact head; add a sixth file to PR #204; create a general scope bypass; weaken, skip or silence any substantive regression; change any accepted spoken contribution, written question, vote, identity, role, financial-interest, donation, outside-work or company-link record; change the fixed commitments/public-positions capture; compare any commitment or position with conduct or outcomes; declare a promise delivered, broken, attempted, blocked, reversed or contradicted; infer topic, ideology, personality, motive, sincerity, importance, accuracy, legality, propriety or influence; access or mutate the private server or SQLite; mark a partial section complete; mark the report publishable; or authorise public output.

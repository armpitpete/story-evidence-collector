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
- Exact starting head for this clarification: `c214ff202dbd7a7a4d5427a40341aeac161ed250`.
- Jeremy Corbyn current-Parliament spoken-contributions baseline is complete at merge `098cc5f77ef30e4c259a164f70e79b8451d138c9` from exact reviewed implementation head `ab36c84dd089adbb3bae151bd4547423a297741b`.
- Its closure is complete at merge `dfe99df47a0808ca1bf1ebfe1cf816725fbb758f` from exact closure head `56b6aaada7998a33740490599c3716cb3827c1c6`.
- The current-Parliament explicit-commitments and public-position evidence lane was authorised at merge `4964c6b00f91c08ef9e06b5150455eaea18e8e47` from exact authority head `a29919d21daa9ce38e6390d0c0d47c7b815b507e`.
- PR #205 authorised the first spoken-regression preservation repair at merge `8b08f55a9dafff912e89cc3dcd74ee274f7b0631`.
- PR #208 added the bounded PR-#206 workflow scope exception at merge `f160fbad41dad8ceab7d82a96a482ddc194a9e5c`.
- PR #209 authorised the event-field correction at merge `1f56db9518c4253bf0f23741939afe0afae1b842`.
- PR #210 corrected the workflow event field at merge `e598a62fffffd3b16dd5fc45f934d48e2bc58ca9`.
- PR #206 merged the first one-file spoken-regression repair at exact reviewed head `30a8c4dab909cecc244786884360c3d142c9d9ee` as `c214ff202dbd7a7a4d5427a40341aeac161ed250`.
- Current-Parliament written questions, regulated-donee donations, outside-work/company links, current financial interests, roles and committees, and identity and parliamentary career remain complete within their declared bounded source scopes.
- Complete MP Portfolio vertical slice, January 2003 vote-review queue, Repository Release v1 and backup-and-restore hardening remain complete and authoritative.

## Current lane

Jeremy Corbyn current-Parliament explicit-commitments and public-position evidence baseline, with draft PR #204 parked after a controlled reconciliation attempt exposed one further prerequisite regression defect.

Goal: create a bounded, source-verbatim evidence packet of explicit commitments and directly stated public positions attributable to Jeremy Corbyn from `2024-07-04` through one declared capture timestamp. This lane records what was expressly said, who the stated actor was, and any literal condition or deadline. It does not compare statements with later conduct, decide delivery, infer contradiction, classify political character or authorise publication.

Canonical section:

- `public_positions_over_time`

The `changes_and_contradictions` section remains outside this lane.

## Date and identity boundary

- statement publication or delivery date from `2024-07-04` through one declared UTC capture timestamp;
- Jeremy Corbyn, UK Parliament member ID `185`;
- direct statements made by him;
- documents or statements issued under his name;
- collective statements only when the source identifies the issuing organisation and his evidenced role or direct endorsement at the time;
- no pre-4-July-2024 election or career history in this baseline.

## Accepted source boundary

Primary attributable text only:

- the already accepted official Hansard spoken-contributions packet and its official UK Parliament/Hansard permalinks;
- official UK Parliament pages or structured records that reproduce a direct statement by Jeremy Corbyn;
- dated first-party statements, speeches, policy documents, manifestos or press releases published under Jeremy Corbyn's name or by his official parliamentary office;
- dated first-party documents issued by a political organisation, campaign or party where the source separately establishes the collective issuer and Jeremy Corbyn's evidenced role or direct endorsement;
- an archived copy of an otherwise accepted first-party page only when the original URL, publisher identity, publication date where available, archive capture timestamp and preserved text are all recorded.

The original source text must be captured or fixed by checksum. Search results, snippets and paraphrases are navigation evidence only.

## Excluded source classes

- media paraphrases, commentary, opinion pieces or unattributed quotation compilations;
- Wikipedia, commercial political databases and third-party promise trackers;
- social-media posts, reposts, screenshots or deleted-post reconstructions;
- video or audio transcription, including Parliament TV or broadcast transcription;
- interviews without an authoritative published transcript supplied by the speaker or issuing organisation;
- private correspondence, leaked material or anonymous documents;
- statements before `2024-07-04` or after the declared capture timestamp;
- conduct evidence such as votes, donations, company links or organisational actions except as separately preserved existing records that remain untouched.

## Statement-form contract

Allowed record classes:

- `explicit_personal_commitment`;
- `conditional_personal_commitment`;
- `collective_commitment`;
- `public_position`;
- `unresolved_statement_form`.

An accepted record must preserve the exact quotation and enough adjacent context to prevent a sentence fragment from changing its meaning. Hopes, aims, ambitions, predictions, rhetorical questions, past conduct, attendance, sponsorship, association, silence and written questions do not become commitments or positions by implication.

## Required evidence packet behaviour

- create one stable record ID per accepted statement occurrence;
- preserve exact quotation, surrounding context, source title, source URL or repository location, publication date, capture timestamp and checksum;
- preserve whether the statement is personal or collective;
- preserve conditions and deadlines only where explicitly stated;
- retain repeated statements as separate occurrences when source locations or dates differ;
- reject duplicate record IDs;
- record every excluded or unresolved candidate with a neutral reason code;
- distinguish source absence from evidence that no commitment or position existed;
- create no topic, ideology, sentiment, personality, motive, sincerity, importance or truth classification;
- create no delivery, fulfilment, broken-promise, reversal, contradiction, consistency or hypocrisy assessment;
- create no relationship record and change no organisation, voting, financial, question or speech evidence;
- leave `public_positions_over_time` `partial`;
- leave `changes_and_contradictions` unchanged and human-review-required;
- keep the report `not_ready`, human review required and public output unauthorised.

## Authorised PR #204 implementation scope

Draft PR #204 may change exactly:

- `research/complete-mp-reports/jeremy-corbyn/current-parliament-commitments-and-public-positions-v1.json`
- `docs/jeremy-corbyn-current-parliament-commitments-and-public-positions-source-note-v1.md`
- `fixtures/complete-mp-reports/jeremy-corbyn-fixture-v1.json`
- `scripts/test_jeremy_corbyn_current_parliament_commitments_and_public_positions_v1.py`
- `.github/workflows/jeremy-corbyn-current-parliament-commitments-public-positions-test.yml`

No schema, generator, interface, existing source packet, existing regression, server or database file is authorised in PR #204.

## Fixed capture accepted for implementation

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
- accepted statement dates from `2024-07-18` through `2026-07-16`;
- capture SHA-256 `fc5651b9f5647bcbfee822121f3188b0438fc826ad604351d044a8144e3df3db`.

## Controlled PR #204 reconciliation result

PR #204 remains open, draft and unmerged at exact head:

- `e0df9e8e6fea793c403d6f6b0fb755c820d42179`

Its current diff remains limited to:

- `.github/workflows/jeremy-corbyn-current-parliament-commitments-public-positions-test.yml`
- `research/complete-mp-reports/jeremy-corbyn/current-parliament-commitments-and-public-positions-v1.json`

A controlled run checked out PR #204, verified exact repaired main `c214ff202dbd7a7a4d5427a40341aeac161ed250`, merged that main only inside the runner, restored the fixed packet, source note and regression payloads, and attempted fixture integration.

The new lane implementation passed its own fixed validation:

- 8 sources;
- 48 accepted statements;
- 19 unresolved statements;
- 42 excluded candidates.

The run then stopped before committing or pushing the five-file implementation because the merged spoken-contributions regression failed inside `test_position_lane_preservation_boundary()` at:

- `assert positions == POSITION_SECTION_BASELINE`

That synthetic test assumes the canonical `public_positions_over_time` section is still the exact `not_researched` baseline. It passes before PR #204 is integrated but cannot run against the separately authorised populated `partial` section. The preservation-hash calculation itself accepted the populated lane before this synthetic setup assertion was reached.

No five-file implementation commit was pushed. PR #204 was returned to the exact parked head above and must not be expanded to a sixth file.

## Authorised second prerequisite regression repair

One separate prerequisite PR may change only:

- `scripts/test_jeremy_corbyn_current_parliament_spoken_contributions_v1.py`

It may alter only the synthetic position-lane boundary test and directly supporting test helper code. It must:

- retain `POSITION_SECTION_ID`, `POSITION_SECTION_BASELINE`, `exclusively_position_source_ids()`, `legacy_sections_for_spoken_hash()` and `current_preservation_hashes()` unchanged;
- retain every fixed spoken packet, fixture, source, fact, section, claim, interpretation, relationship and publication hash requirement;
- retain all 306 spoken contribution checks and all 90 written-question preservation checks;
- prove the synthetic position record can be added when the position section is the exact original baseline;
- prove another synthetic position record can be added when the position section is already validly `partial` and populated;
- preserve all existing position fact IDs and append only the new synthetic fact ID in memory;
- require position claims, interpretations and relationships to remain empty;
- continue rejecting a position source that is referenced by a non-position fact, claim, relationship or subject identity record;
- continue rejecting any unrelated canonical-section change;
- create no fixture mutation, packet mutation, source-note change, schema change, generator change, workflow change or publication change;
- run Python compilation, the complete spoken-contributions regression, the written-question regression and `git diff --check`.

The repair must remain one-file and must stop if supporting the already-populated fixture requires changing preservation logic, another regression, a canonical fixture, schema, generator or workflow.

## Authorised exact-scope workflow follow-up

After the one-file repair PR exists at a fixed exact head, one separate workflow-only PR may change only:

- `.github/workflows/jeremy-corbyn-current-parliament-spoken-contributions-test.yml`

It may alter only the final exact-scope validation to recognise that exact repair PR number, exact head SHA and exact one-file set. It must:

- retain the original five-file implementation allowance;
- retain the exact historical PR #206 allowance unchanged;
- add no branch wildcard, title test, general one-file allowance or silent success path;
- retain read-only permissions, exact-head checkout, Python setup, compilation, the full spoken regression, the written-question regression and `git diff --check`;
- print the evaluated PR number, head SHA and changed-file set;
- reject every differing PR number, head SHA or file set.

The workflow-only follow-up may merge after Project Control passes and GitHub independently confirms exactly one changed workflow file, even though the inherited final scope guard necessarily rejects the workflow-repair PR itself. The one-file regression repair must then be rerun unchanged and may merge only when every fresh required check is green.

## Required PR #204 validation after prerequisites

After both prerequisite repairs merge, PR #204 must be reconciled against the new exact main and prove:

- all fixed source and statement-form counts;
- exact date coverage, unique stable IDs and deterministic duplicate handling;
- every quotation is present in its preserved source payload or fixed source text;
- every accepted record is inside the date and identity boundary;
- every collective commitment preserves collective rather than personal agency;
- no written-question record has been reclassified as a commitment or position;
- no claim, interpretation, relationship or contradiction record is created;
- all existing accepted facts, sources and ordering remain unchanged outside `public_positions_over_time` and its directly related coverage gap;
- canonical fixture validation and deterministic report generation pass;
- current-Parliament spoken-contributions and written-questions regressions pass;
- identity-and-career, roles-and-committees, current financial-interests, regulated-donee donations and outside-work/company-links regressions pass;
- Complete MP Report fixture, Complete MP Portfolio view, Repository Release validation and Project Control pass;
- exactly the five authorised implementation files change relative to repaired `main`.

PR #204 must remain draft until all exact-scope and regression requirements are green. It must stop for owner review without merging.

## Done

- Spoken-contributions baseline and closure are complete.
- The current commitments/public-positions lane, fixed source inventory and candidate capture are complete.
- The current schema represents the neutral records without schema or generator change.
- PR #206 and both required workflow corrections merged.
- The first controlled PR #204 reconciliation reached and passed the new lane regression.
- The remaining failure is isolated to the spoken regression's synthetic empty-section assumption.
- Temporary repair PR #211 was closed unmerged and its branch was reset to exact main; it creates no authority or implementation state.
- PR #204 remains draft, parked and unmerged.
- The commitment-versus-conduct comparison remains unstarted.

## To do

- merge this `STATUS.md`-only clarification after Project Control passes;
- open one exact one-file populated-position spoken-regression repair PR;
- freeze and verify its exact head;
- open and merge one exact workflow-only scope follow-up for that frozen PR/head/file set;
- rerun, review and merge the one-file regression repair only after every fresh required check is green;
- reconcile PR #204 against the resulting exact main;
- restore exactly the five authorised implementation files;
- run the complete required regression matrix;
- mark PR #204 ready only after exact five-file scope and every required check are green;
- stop for owner review without merging PR #204.

## Next bounded gate

Merge this `STATUS.md`-only clarification after Project Control passes. Then open one one-file prerequisite repair changing only `scripts/test_jeremy_corbyn_current_parliament_spoken_contributions_v1.py` so its synthetic boundary test supports both the original empty position section and the already-populated authorised position section without changing preservation logic.

## Stop point

Do not resume, expand, mark ready or merge PR #204; modify its five-file evidence implementation to absorb this prerequisite; weaken, skip or silence any substantive regression; change the spoken packet, spoken source note, fixture, schema, generator or another workflow in the one-file repair; create a general scope bypass; weaken or replace any accepted spoken contribution, written question, vote, identity, role, financial-interest, donation, outside-work or company-link record; compare any commitment or position with conduct or outcomes; declare a promise delivered, broken, attempted, blocked, reversed or contradicted; infer topic, ideology, personality, motive, sincerity, importance, accuracy, legality, propriety or influence; use excluded source classes; include pre-4-July-2024 material; change another canonical section; access or mutate the private server or SQLite; mark a partial section complete; mark the report publishable; or authorise public output.

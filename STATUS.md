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
- Exact starting head for this clarification: `f160fbad41dad8ceab7d82a96a482ddc194a9e5c`.
- Jeremy Corbyn current-Parliament spoken-contributions baseline is complete at merge `098cc5f77ef30e4c259a164f70e79b8451d138c9` from exact reviewed implementation head `ab36c84dd089adbb3bae151bd4547423a297741b`.
- Its closure is complete at merge `dfe99df47a0808ca1bf1ebfe1cf816725fbb758f` from exact closure head `56b6aaada7998a33740490599c3716cb3827c1c6`.
- The current-Parliament explicit-commitments and public-position evidence lane was authorised at merge `4964c6b00f91c08ef9e06b5150455eaea18e8e47` from exact authority head `a29919d21daa9ce38e6390d0c0d47c7b815b507e`.
- PR #205 clarified the spoken-regression preservation boundary at merge `8b08f55a9dafff912e89cc3dcd74ee274f7b0631` from exact authority head `6fdb0d7731437bfafd17af4fff1417d50538990d`.
- PR #208 added the bounded PR-#206 workflow scope exception at merge `f160fbad41dad8ceab7d82a96a482ddc194a9e5c` from exact reviewed head `b6de3964ca9a8b0842f9208a3d5bfbe430255fde`.
- Current-Parliament written questions, regulated-donee donations, outside-work/company links, current financial interests, roles and committees, and identity and parliamentary career remain complete within their declared bounded source scopes.
- Complete MP Portfolio vertical slice, January 2003 vote-review queue, Repository Release v1 and backup-and-restore hardening remain complete and authoritative.

## Current lane

Jeremy Corbyn current-Parliament explicit-commitments and public-position evidence baseline, with PR #204 parked, PR #206 unmerged, and one authorised workflow-only event-field correction required before PR #206 may proceed.

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
- an archived copy of an otherwise accepted first-party page only when the original URL, publisher identity, publication date where available, archive capture timestamp and preserved text are all recorded. The archive is preservation evidence, not a separate authority for the statement.

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

An accepted record must preserve the exact quotation and enough adjacent context to prevent a sentence fragment from changing its meaning.

Allowed record classes:

- `explicit_personal_commitment`: a direct future-oriented undertaking by Jeremy Corbyn with an identifiable personal action;
- `conditional_personal_commitment`: the same, with an explicit condition preserved verbatim;
- `collective_commitment`: a future-oriented undertaking using collective agency, attributed to the named issuing body and not silently converted into a personal promise;
- `public_position`: an explicit statement of support, opposition, endorsement, rejection, request or call for action;
- `unresolved_statement_form`: a potentially relevant passage whose actor, action, condition, quotation boundary or statement form cannot be resolved without interpretation.

The following do not become commitments merely because they express preference:

- hopes, aims, ambitions or desired outcomes;
- predictions or descriptions of what another person or institution will do;
- rhetorical questions;
- statements describing past conduct;
- attendance, sponsorship, association or silence;
- written questions. The accepted 90 written-question records remain evidence of questions asked and may not be promoted into positions or commitments by implication.

Literal fields may include actor, collective issuer, stated action, stated position, explicit condition and explicit deadline. Missing conditions, deadlines, power, motive or intended outcome must remain unknown rather than inferred.

## Required evidence packet behaviour

- create one stable record ID per accepted statement occurrence;
- preserve exact quotation, surrounding context, source title, source URL or repository location, publication date, capture timestamp and checksum;
- preserve whether the statement is personal or collective;
- preserve conditions and deadlines only where the source states them explicitly;
- retain repeated statements as separate occurrences when they have distinct source locations or dates, while recording exact duplicates deterministically;
- reject duplicate record IDs;
- record every excluded or unresolved candidate with a neutral reason code;
- distinguish source absence from evidence that no commitment or position existed;
- create no topic, ideology, sentiment, personality, motive, sincerity, importance or truth classification;
- create no delivery, fulfilment, broken-promise, reversal, contradiction, consistency or hypocrisy assessment;
- create no relationship record and change no organisation, voting, financial, question or speech evidence;
- leave `public_positions_over_time` `partial`;
- leave `changes_and_contradictions` unchanged and human-review-required;
- keep the report `not_ready`, human review required and public output unauthorised.

## Authorised implementation scope

The parked implementation PR may change exactly:

- `research/complete-mp-reports/jeremy-corbyn/current-parliament-commitments-and-public-positions-v1.json`
- `docs/jeremy-corbyn-current-parliament-commitments-and-public-positions-source-note-v1.md`
- `fixtures/complete-mp-reports/jeremy-corbyn-fixture-v1.json`
- `scripts/test_jeremy_corbyn_current_parliament_commitments_and_public_positions_v1.py`
- `.github/workflows/jeremy-corbyn-current-parliament-commitments-public-positions-test.yml`

No schema, generator, interface, existing source packet, server or database file is authorised in that implementation PR.

## Fixed capture accepted for implementation

The fixed pre-implementation capture records:

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

Draft PR #204 remains the parked five-file implementation lane. Fixture integration must not resume until the prerequisite repair and workflow correction below have passed and merged.

## Authorised prerequisite regression repair

PR #206 is the separately authorised one-file repair:

- PR: `#206`;
- exact head: `30a8c4dab909cecc244786884360c3d142c9d9ee`;
- current base: `f160fbad41dad8ceab7d82a96a482ddc194a9e5c`;
- changed path: `scripts/test_jeremy_corbyn_current_parliament_spoken_contributions_v1.py` only.

The repair makes the legacy spoken preservation calculation aware only of the separately authorised `public_positions_over_time` lane. It must continue to protect:

- the exact 306 spoken contribution IDs, records, facts, dates, venues, text-presence checks and source records;
- the exact 90 written-question facts before the 306 speech facts in `speeches_and_questions`;
- the exact spoken section status, no claims, no interpretations, no relationships and the accepted spoken coverage gap;
- `not_ready`, human-review-required and public-output-unauthorised states;
- every canonical section other than `public_positions_over_time` and `speeches_and_questions`;
- all claims, interpretations, relationships and publication authority.

Fresh checks against exact head `30a8c4dab909cecc244786884360c3d142c9d9ee` after PR #208 merged show:

- Repository release validation: passed;
- Project Control: passed;
- Spoken-contributions compilation: passed;
- 306-record spoken-contributions regression: passed;
- 90-question preservation regression: passed;
- Final exact-scope guard: failed.

GitHub independently confirms that PR #206 changes exactly:

- `scripts/test_jeremy_corbyn_current_parliament_spoken_contributions_v1.py`

PR #206 must remain unmerged until the workflow event-field correction below is merged and every fresh required check is green.

## Authorised second workflow-only correction

PR #208 correctly introduced the bounded PR-#206/head-SHA/file-set rule in:

- `.github/workflows/jeremy-corbyn-current-parliament-spoken-contributions-test.yml`

The remaining failure is limited to the PR-number event field used by the final exact-scope guard. One separate correction PR may change only:

- `.github/workflows/jeremy-corbyn-current-parliament-spoken-contributions-test.yml`

The correction may alter only the final exact-scope validation and must:

- change the PR-number source from `github.event.pull_request.number` to `github.event.number`;
- retain the exact PR requirement `206`;
- retain exact head `30a8c4dab909cecc244786884360c3d142c9d9ee`;
- retain the exact one-file set `scripts/test_jeremy_corbyn_current_parliament_spoken_contributions_v1.py`;
- retain the current pull-request path filters;
- retain read-only permissions;
- retain exact-head checkout;
- retain Python setup and compilation;
- retain the full 306-record spoken-contributions regression;
- retain the 90-question preservation regression;
- retain every other substantive test;
- retain `git diff --check`;
- print the evaluated PR number, head SHA and changed-file set before applying the bounded decision;
- reject the one-file exception if the PR number, head SHA or changed-file set differs;
- create no general exception, one-file allowance, branch wildcard, title-based allowance, `continue-on-error`, skipped test, reduced permission boundary or silent success path;
- make no change to the spoken packet, source note, fixture, schema, generator, regression script or any other workflow.

The second workflow-only correction must pass Project Control and must show exactly one changed file. After it merges, PR #206 must be retriggered at the unchanged exact head `30a8c4dab909cecc244786884360c3d142c9d9ee`. PR #206 may merge only when Repository Release validation, Project Control, compilation, both substantive regressions, the final exact-scope guard and every other required check are freshly green.

## Required implementation validation

After both prerequisite repairs merge, PR #204 must prove:

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

## Done

- PR #197 was reviewed at exact head `ab36c84dd089adbb3bae151bd4547423a297741b` and merged as `098cc5f77ef30e4c259a164f70e79b8451d138c9` after all 11 required workflows passed.
- PR #202 closed the spoken-contributions lane at merge `dfe99df47a0808ca1bf1ebfe1cf816725fbb758f`.
- PR #203 authorised this lane at merge `4964c6b00f91c08ef9e06b5150455eaea18e8e47`.
- The fixed source inventory and candidate-statement capture are complete with the accepted 8-source, 48-accepted, 19-unresolved and 42-excluded result.
- The current schema represents the neutral records as `position` facts without schema or generator change.
- PR #205 authorised the bounded spoken-regression preservation repair and merged as `8b08f55a9dafff912e89cc3dcd74ee274f7b0631`.
- PR #208 added the bounded workflow scope exception and merged at `f160fbad41dad8ceab7d82a96a482ddc194a9e5c`.
- PR #206 remains open at exact head `30a8c4dab909cecc244786884360c3d142c9d9ee`, changes exactly one regression file, and passes every required check except the final exact-scope guard.
- Draft PR #204 remains parked and unmerged.
- The commitment-versus-conduct comparison remains unstarted.

## To do

- merge this `STATUS.md`-only clarification after Project Control passes;
- open one separate workflow-only correction changing only `.github/workflows/jeremy-corbyn-current-parliament-spoken-contributions-test.yml`;
- replace only the PR-number event source, preserve all exact constraints and add explicit evaluated-value diagnostics;
- review and merge that workflow-only correction after exact one-file scope and Project Control pass;
- retrigger PR #206 at unchanged exact head `30a8c4dab909cecc244786884360c3d142c9d9ee`;
- review and merge PR #206 only after every fresh required check is green;
- reconcile draft PR #204 against repaired `main`;
- restore the full fixed packet, source note, fixture integration, deterministic regression and read-only CI in exactly the five authorised files;
- run the complete required regression matrix;
- mark PR #204 ready only after exact five-file scope and all checks are green;
- stop for review without merging PR #204.

## Next bounded gate

Merge this `STATUS.md`-only clarification after Project Control passes. Then open, review and merge one separate workflow-only correction that changes only the PR-number event source from `github.event.pull_request.number` to `github.event.number`, preserves every exact PR-#206/head-SHA/file-set and substantive validation requirement, and prints the evaluated PR number, head SHA and changed-file set. Retrigger PR #206 at unchanged exact head `30a8c4dab909cecc244786884360c3d142c9d9ee`. Do not merge PR #206 or resume PR #204 until every fresh required check passes.

## Stop point

Do not merge PR #206 while any required check is red; resume or expand PR #204; create a general one-file scope bypass; weaken, skip or silence any substantive regression; change the spoken packet, source note, fixture, schema, generator or another workflow in the workflow-only correction; weaken or replace any accepted spoken contribution, written question, vote, identity, role, financial-interest, donation, outside-work or company-link record; compare any commitment or position with conduct or outcomes; declare a promise delivered, broken, attempted, blocked, reversed or contradicted; infer topic, ideology, personality, motive, sincerity, importance, accuracy, legality, propriety or influence; use excluded source classes; include pre-4-July-2024 material; change another canonical section; access or mutate the private server or SQLite; mark a partial section complete; mark the report publishable; or authorise public output.

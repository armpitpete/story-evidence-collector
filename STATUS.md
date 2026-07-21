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
- Exact starting head for this lane: `dfe99df47a0808ca1bf1ebfe1cf816725fbb758f`.
- Jeremy Corbyn current-Parliament spoken-contributions baseline is complete at merge `098cc5f77ef30e4c259a164f70e79b8451d138c9` from exact reviewed implementation head `ab36c84dd089adbb3bae151bd4547423a297741b`.
- Its closure is complete at merge `dfe99df47a0808ca1bf1ebfe1cf816725fbb758f` from exact closure head `56b6aaada7998a33740490599c3716cb3827c1c6`.
- Current-Parliament written questions, regulated-donee donations, outside-work/company links, current financial interests, roles and committees, and identity and parliamentary career remain complete within their declared bounded source scopes.
- Complete MP Portfolio vertical slice, January 2003 vote-review queue, Repository Release v1 and backup-and-restore hardening remain complete and authoritative.

## Current lane

Jeremy Corbyn current-Parliament explicit-commitments and public-position evidence baseline.

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

One later implementation PR may change exactly:

- `research/complete-mp-reports/jeremy-corbyn/current-parliament-commitments-and-public-positions-v1.json`
- `docs/jeremy-corbyn-current-parliament-commitments-and-public-positions-source-note-v1.md`
- `fixtures/complete-mp-reports/jeremy-corbyn-fixture-v1.json`
- `scripts/test_jeremy_corbyn_current_parliament_commitments_and_public_positions_v1.py`
- `.github/workflows/jeremy-corbyn-current-parliament-commitments-public-positions-test.yml`

No schema, generator, interface, existing source packet, existing regression, server or database file is authorised. If the current schema cannot represent the bounded neutral records without changing another file, stop and open a separate authority clarification rather than expanding the implementation PR.

## Required validation

The implementation must prove:

- fixed source-document or source-page count;
- accepted explicit-personal-commitment count;
- accepted conditional-personal-commitment count;
- accepted collective-commitment count;
- accepted public-position count;
- unresolved-statement-form count;
- exact earliest and latest accepted statement dates and capture timestamp;
- unique stable record IDs and deterministic duplicate handling;
- every quotation is present in its preserved source payload or fixed source text;
- every accepted record is inside the date and identity boundary;
- every collective commitment preserves collective rather than personal agency;
- no written-question record has been reclassified as a commitment or position;
- no claim, interpretation, relationship or contradiction record is created by this lane;
- all existing accepted facts, sources and ordering remain unchanged outside `public_positions_over_time` and its directly related coverage gap;
- canonical fixture validation and deterministic report generation pass;
- current-Parliament spoken-contributions and written-questions regressions pass;
- identity-and-career, roles-and-committees, current financial-interests, regulated-donee donations and outside-work/company-links regressions pass;
- Complete MP Report fixture, Complete MP Portfolio view, Repository Release validation and Project Control pass;
- exactly the five authorised implementation files change.

## Done

- PR #197 was reviewed at exact head `ab36c84dd089adbb3bae151bd4547423a297741b` and merged as `098cc5f77ef30e4c259a164f70e79b8451d138c9` after all 11 required workflows passed.
- PR #202 closed the spoken-contributions lane at merge `dfe99df47a0808ca1bf1ebfe1cf816725fbb758f`.
- The accepted current-Parliament evidence now includes 306 spoken contributions and 90 written questions, without position or commitment inference.
- The commitment-versus-conduct comparison remains unstarted.

## To do

- merge this `STATUS.md`-only authority activation after Project Control passes;
- enumerate the accepted first-party and official source inventory inside the date boundary;
- freeze the source payloads or texts and their checksums;
- extract candidate passages without assigning political topics or outcomes;
- classify only the authorised statement forms, preserving unresolved candidates;
- publish the fixed counts, date coverage, identifier method and unresolved count before fixture integration;
- open one exact five-file implementation PR;
- stop after that implementation PR is complete, tested and reviewed.

## Next bounded gate

Merge this authority-only activation PR after Project Control passes. Then produce one fixed source inventory and candidate-statement capture. Before implementation begins, report the source count, each accepted statement-form count, exact date coverage, stable record-ID method and unresolved count.

## Stop point

Do not compare any commitment or position with votes, questions, speeches, amendments, organisational conduct or outcomes; declare a promise delivered, broken, attempted, blocked, reversed or contradicted; infer a political topic, ideology, personality, motive, sincerity, importance, accuracy, legality, propriety or influence; use media, social media, video/audio transcription, commercial databases or unattributed sources; include pre-4-July-2024 material; alter accepted spoken-contribution, written-question, voting, identity, roles, financial-interest, donation, outside-work or company-link records; change another canonical section; access or mutate the private server or SQLite; mark a partial section complete; mark the report publishable; or authorise public output. Stop after one five-file evidence-baseline implementation PR is complete, tested and reviewed.
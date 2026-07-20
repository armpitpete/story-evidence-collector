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
- Exact starting head for this lane: `d83e3d7b5e1bf5f0b20a7bef2e2c54131d6f03f2`.
- Jeremy Corbyn regulated-donee donations baseline is complete at merge `419ac75a5261f66149494805946d154a4ef41339` from exact reviewed head `fd4f16a8c1767f00416f837336237944b82480ff`.
- Jeremy Corbyn outside-work-and-company-links baseline remains complete at merge `d9bac48a0561b2a807c24f72b32a757607dea9d6`.
- Jeremy Corbyn current financial-interests baseline remains complete at merge `e92262ccafa2e9628bc5e8f5bba6be4c14541750`.
- Jeremy Corbyn roles-and-committees baseline remains complete at merge `968d33dac9e80cdf0f6c9107c195c5f7d7f70a1b`.
- Jeremy Corbyn identity-and-parliamentary-career baseline remains complete at merge `93c8da204d9709a1490dfa24a7b722a5f6a85199`.
- Complete MP Portfolio vertical slice and local acceptance remain complete.
- January 2003 vote-review queue, Repository Release v1 and backup-and-restore hardening remain complete and authoritative.

## Current lane

Jeremy Corbyn current-Parliament Commons written-questions baseline.

Goal: replace the unresearched written-question part of `speeches_and_parliamentary_questions` with a bounded official-source baseline for Commons written questions tabled by Jeremy Corbyn from 4 July 2024 through one declared capture timestamp, without beginning spoken-contribution research or treating question text as proof that its premise is true.

Canonical section:

- `speeches_and_parliamentary_questions`

Date and record boundary:

- Commons written questions tabled from `2024-07-04` through the declared capture timestamp;
- Jeremy Corbyn identified by UK Parliament member ID `185` and by the official question-detail author record;
- one official UIN/detail record per question;
- answered and unanswered questions included;
- later answer updates or holding-answer replacements preserved when the official detail page exposes them.

Official source boundary:

- the UK Parliament member written-questions index at `members.parliament.uk/member/185/writtenquestions`, including its displayed result count and pagination at capture time;
- the official Written Questions, Answers and Statements detail page for every accepted UIN;
- official question text, UIN, tabled date, answered status, answer text, answered date, answering body, answering member, named-day marker, interests-declared marker, grouped-question references and House when displayed;
- official index/detail links only; no search-engine snippets as evidence.

Known source limits to preserve:

- the member written-questions index is a live current service and its result count may change after capture;
- unanswered questions may later receive answers;
- holding answers may later be superseded or updated;
- question wording records what Jeremy Corbyn asked and does not establish the truth of any premise within the question;
- this lane does not claim complete career-wide written-question coverage before 4 July 2024.

Forbidden source classes and expansion:

- spoken Hansard contributions, debates, interventions, speeches, points of order and oral supplementary questions;
- written ministerial statements, Early Day Motions, voting records, committee evidence and correspondence;
- media, party, campaign or personal websites, social media, Wikipedia, commercial parliamentary databases and search-result snippets;
- topic classification, sentiment analysis, policy-position inference, contradiction analysis or claims about motive, influence, accuracy, significance or effectiveness;
- changing `public_positions_over_time`, `changes_and_contradictions`, `organisations_and_relationships` or any other canonical section.

Authorised implementation scope:

- `research/complete-mp-reports/jeremy-corbyn/current-parliament-written-questions-v1.json`
- `docs/jeremy-corbyn-current-parliament-written-questions-source-note-v1.md`
- `fixtures/complete-mp-reports/jeremy-corbyn-fixture-v1.json`
- `scripts/test_jeremy_corbyn_current_parliament_written_questions_v1.py`
- `.github/workflows/jeremy-corbyn-current-parliament-written-questions-test.yml`

Required behaviour:

- capture every official member-index result within the date boundary, reconciling displayed result count, page count, accepted UIN count and duplicate UIN count;
- fetch and preserve the official detail record for every accepted UIN with a bounded delay and no concurrent or anti-bot behaviour;
- reject any record whose detail page does not identify Jeremy Corbyn as the question author without guessing;
- preserve official text and displayed metadata without silently correcting names, punctuation, dates or departmental wording;
- create one `question` fact per accepted UIN, describing only that the official record shows Jeremy Corbyn tabled the recorded question and its answer status;
- preserve full question and answer fields in the machine-readable packet rather than compressing them into interpretive summaries;
- create no position, relationship, claim or interpretation record;
- leave the section `partial` with explicit open gaps for spoken contributions, pre-4-July-2024 written questions, future answer changes and any inaccessible or unresolved detail record;
- keep the report `not_ready`, human review required and public output unauthorised;
- preserve every accepted identity, roles, voting, financial-interests, donations and outside-work/company record unchanged;
- validate the complete fixture through the canonical Complete MP Report validator and deterministic generator;
- run the new lane regression, identity-and-career regression, roles-and-committees regression, current financial-interests regression, regulated-donee donations regression, outside-work/company-links regression, Complete MP Report fixture test, Complete MP Portfolio view test, Repository Release validation and Project Control;
- change exactly the five authorised files.

## Done

- Repository Release v1 and backup/restore proof are complete.
- January 2003 seed-row shape and vote-review queue preparation are complete.
- The accepted Streamlit interface exposes `Simple`, `MP Portfolio` and `Advanced` views.
- Jeremy Corbyn identity-and-career, roles-and-committees, current financial-interests, regulated-donee donations and current outside-work/company-links baselines are complete within their declared official-source scopes.
- UK Parliament exposes a distinct Jeremy Corbyn written-questions index and official question-detail pages with UIN identifiers.
- At authority drafting time the member index displayed approximately 251 results across 13 pages; this is provisional only and must be re-captured and reconciled at the implementation capture timestamp.
- UK Parliament exposes spoken contributions separately and warns that spoken-contribution counts can be approximate; spoken contributions are outside this lane.
- The `speeches_and_parliamentary_questions` section remains `not_researched` in current `main`.

## To do

- Build one bounded, disposable capture script outside the committed five-file scope or embed equivalent fixed capture logic in the implementation handoff.
- Capture the complete member-index result set within the date boundary with a polite sequential delay.
- Fetch and reconcile every official question-detail page.
- Record unanswered, holding-answer, superseded-answer, named-day, interests-declared and grouped-question states exactly when displayed.
- Create the machine-readable packet and readable source note.
- Update only the speeches-and-parliamentary-questions section, its official sources, question facts and directly related coverage gaps.
- Add deterministic validation and CI.
- Open and review one five-file implementation PR.
- After implementation merge, close this lane through a separate `STATUS.md`-only authority PR.

## Next bounded gate

Merge this authority-only activation PR after Project Control passes. Then ChatGPT Work must capture and reconcile the official member index and detail records. Codex may encode the fixed packet only after the capture timestamp, result count, UIN set and unresolved-record count are explicit.

## Stop point

Do not research another MP or canonical section; begin spoken-contribution collection; include pre-4-July-2024 questions; alter accepted identity, roles, voting, financial-interests, donations, outside-work, positions, relationships or human-review records; infer the truth of question premises, policy positions, influence, motive, accuracy, legality or propriety; review January 2003 vote meanings; access or mutate the private server or SQLite; create claims or interpretations; mark the section complete; mark the report publishable; or authorise public output. Stop after one five-file implementation PR is complete, tested and reviewed.

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
- Exact starting head for this lane: `95178576da8a24ffa42a50d30c22cba8de3948e0`.
- Jeremy Corbyn current-Parliament written-questions baseline is complete at merge `e1b21c1e4de1eefb827ac1f337017858510bc192` from exact reviewed head `324590ec9c2db1ad3bbbc92ce33de06c2cb430a1`.
- Jeremy Corbyn regulated-donee donations, outside-work/company-links, current financial-interests, roles-and-committees and identity-and-career baselines remain complete within their declared official-source scopes.
- Complete MP Portfolio vertical slice, January 2003 vote-review queue, Repository Release v1 and backup-and-restore hardening remain complete and authoritative.

## Current lane

Jeremy Corbyn current-Parliament spoken-contributions baseline.

Goal: add a bounded official Hansard index of individual spoken contribution segments made by Jeremy Corbyn from 4 July 2024 through one declared capture timestamp, without treating the approximate member-page debate count as authoritative and without converting what he said into policy-position, contradiction or significance claims.

Canonical section:

- `speeches_and_questions`

Date and identity boundary:

- Commons records dated from `2024-07-04` through the declared capture timestamp;
- UK Parliament member ID `185`;
- individual contribution segments whose official Hansard/member record identifies Jeremy Corbyn as speaker;
- Commons Chamber and Westminster Hall included;
- any other venue or committee context remains unresolved unless the official record unambiguously places it inside this authorised Commons spoken-contribution boundary.

Official source boundary:

- UK Parliament member spoken-contributions index at `https://members.parliament.uk/member/185/contributions`, including every page required to cross the 4 July 2024 boundary;
- Hansard member-contributions search at `https://hansard.parliament.uk/search/MemberContributions?house=Commons&memberId=185` with the authorised date boundary;
- official Hansard debate, section and contribution pages or official structured responses directly used by those services;
- official debate title, sitting date, venue, contribution type, member identity, stable debate/section/contribution identifier, permalink, contribution text, ordering and correction/version status when displayed.

Known source limits to preserve:

- the member page states that its contribution counts can be approximate, so summary counts are navigation and reconciliation evidence only;
- Hansard is an edited record and may expose uncorrected rolling text before a corrected daily version replaces it;
- the live result set can change after capture;
- one debate index row may contain several individual contribution segments;
- contribution type labels record parliamentary form and do not establish a policy position or the truth of any statement.

Forbidden source classes and expansion:

- media, party, campaign or personal websites, social media, Wikipedia, commercial parliamentary databases and search-result snippets;
- video/audio transcription, Parliament TV, committee oral evidence, correspondence, written statements, Early Day Motions, voting records or tabled oral-question records;
- topic or sentiment classification, summarisation of political meaning, policy-position inference, contradiction analysis, motive, influence, accuracy, legality, propriety or significance claims;
- changing `public_positions_over_time`, `changes_and_contradictions`, `organisations_and_relationships` or any other canonical section.

Authorised implementation scope:

- `research/complete-mp-reports/jeremy-corbyn/current-parliament-spoken-contributions-v1.json`
- `docs/jeremy-corbyn-current-parliament-spoken-contributions-source-note-v1.md`
- `fixtures/complete-mp-reports/jeremy-corbyn-fixture-v1.json`
- `scripts/test_jeremy_corbyn_current_parliament_spoken_contributions_v1.py`
- `.github/workflows/jeremy-corbyn-current-parliament-spoken-contributions-test.yml`

Required behaviour:

- capture every official member-index debate row required to cover the date boundary, recording the displayed total and page count only as volatile navigation checks;
- resolve every in-scope debate row to its individual official contribution segments;
- preserve official stable identifiers and permalinks; reject duplicate contribution identifiers;
- reject or explicitly record any segment whose speaker identity, date, venue, identifier or full text cannot be resolved without guessing;
- preserve exact official contribution text and displayed metadata in the machine-readable packet;
- preserve whether the source was corrected, uncorrected/rolling or unspecified when the official page exposes that state;
- create one neutral `speech` fact per accepted individual contribution segment, stating only that Hansard records Jeremy Corbyn making the identified contribution in the named proceeding;
- do not use the approximate debate-summary count as the individual-contribution count;
- create no claim, interpretation, relationship or position record;
- retain all accepted written-question facts and sources unchanged;
- leave `speeches_and_questions` `partial` with explicit gaps for pre-4-July-2024 spoken history, future contributions and corrections, tabled oral questions, written statements, Early Day Motions, committee oral evidence and unresolved records;
- keep the report `not_ready`, human review required and public output unauthorised;
- preserve every accepted identity, roles, voting, financial-interests, donations and outside-work/company record unchanged;
- validate the complete fixture through the canonical Complete MP Report validator and deterministic generator;
- run the new lane regression, current-Parliament written-questions regression, identity-and-career regression, roles-and-committees regression, current financial-interests regression, regulated-donee donations regression, outside-work/company-links regression, Complete MP Report fixture test, Complete MP Portfolio view test, Repository Release validation and Project Control;
- change exactly the five authorised files.

## Done

- Repository Release v1, backup/restore proof, January 2003 vote-review preparation and the accepted Streamlit interface are complete.
- Jeremy Corbyn current-Parliament written questions are captured as 90 neutral official records.
- The UK Parliament member page exposes Jeremy Corbyn's spoken contributions as debate rows with expandable individual segments and warns that displayed contribution counts can be approximate.
- The official Hansard member-contributions search is separately available for Commons member ID `185`.
- Hansard is the edited official record of what was said in Parliament and can distinguish rolling/uncorrected from corrected records.
- The current member page displayed 1,577 all-career debate results across 79 pages during authority research; that volatile all-career figure is not an accepted current-Parliament count and must be re-captured.

## To do

- Resolve the exact official index, expansion and Hansard detail request shapes without using browser automation or anti-bot workarounds.
- Capture all debate rows required to cross the `2024-07-04` boundary with polite sequential requests.
- Reconcile those rows to unique individual contribution segments and stable official identifiers.
- Record source version/correction status and unresolved records explicitly.
- Create the machine-readable packet and readable source note.
- Update only `speeches_and_questions`, adding spoken-contribution sources, `speech` facts and its directly related coverage gap while preserving the 90 written-question facts unchanged.
- Add deterministic validation and CI.
- Open and review one five-file implementation PR.
- After implementation merge, close this lane through a separate `STATUS.md`-only authority PR.

## Next bounded gate

Merge this authority-only activation PR after Project Control passes. Then ChatGPT Work must resolve the official member-index and Hansard contribution request shapes and produce a fixed capture. Codex may encode the five-file implementation only after the debate-row count, unique contribution count, identifier scheme, date coverage and unresolved-record count are explicit.

## Stop point

Do not research another MP or canonical section; include pre-4-July-2024 spoken contributions; begin policy-position or contradiction analysis; include media, video/audio transcription, committee evidence, written statements, Early Day Motions, voting or oral-question datasets; alter accepted identity, roles, voting, financial-interests, donations, outside-work/company-links or written-question records; infer accuracy, influence, motive, legality, propriety or significance; review January 2003 vote meanings; access or mutate the private server or SQLite; mark the section complete; mark the report publishable; or authorise public output. Stop after one five-file implementation PR is complete, tested and reviewed.

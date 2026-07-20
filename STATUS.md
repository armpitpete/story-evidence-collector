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
- Exact starting head for this lane: `f646112b093fdf38343c3e8d2dd5e8518e945fc2`.
- Jeremy Corbyn official roles-and-committees baseline remains complete at merge `968d33dac9e80cdf0f6c9107c195c5f7d7f70a1b` from exact reviewed head `bd5487de67f84a218bd1bb50490e83dc077e9eb4`.
- Jeremy Corbyn official identity-and-career baseline remains complete at merge `93c8da204d9709a1490dfa24a7b722a5f6a85199` from exact reviewed head `e22c9d6d262867e19f2b059677acc3ba9e6fcd4c`.
- Complete MP Portfolio vertical slice and local acceptance remain complete.
- January 2003 vote-review queue, Repository Release v1 and backup-and-restore hardening remain complete and authoritative.

## Current lane

Jeremy Corbyn current financial interests baseline.

Goal: replace the unresearched `financial_interests` section with a complete capture of the current published Register of Members’ Financial Interests snapshot displayed by UK Parliament for member ID `185`, without claiming complete historical coverage or reclassifying entries into other canonical sections.

Canonical section:

- `financial_interests`

Official source boundary:

- Jeremy Corbyn's official UK Parliament `Registered Interests` member page;
- every pagination page and official category-filtered view needed to capture the complete current published snapshot;
- the official current-register metadata or version page linked from that member page, used only to identify the captured register version or publication date;
- an official Parliamentary Commissioner for Standards rectification record only when the member entry itself explicitly links to rectification details.

Forbidden source classes and adjacent lanes:

- Wikipedia, newspapers, broadcasters, party, campaign or personal websites, social media, aggregators and search-result snippets;
- Electoral Commission records, which belong to `donations_and_political_finance`;
- Companies House or other company-registry expansion, which belongs to `outside_work_and_company_links`;
- inference about legality, propriety, influence, motive, benefit or political significance;
- grouping differently named donors, correcting source spelling, deduplicating repeated entries or calculating aggregate values.

Authorised financial-interests implementation scope:

- `research/complete-mp-reports/jeremy-corbyn/current-financial-interests-v1.json`
- `docs/jeremy-corbyn-current-financial-interests-source-note-v1.md`
- `fixtures/complete-mp-reports/jeremy-corbyn-fixture-v1.json`
- `scripts/test_jeremy_corbyn_current_financial_interests_v1.py`
- `.github/workflows/jeremy-corbyn-current-financial-interests-test.yml`

Authorised prerequisite regression repair, in one separate one-file PR before the five-file implementation PR:

- `scripts/test_jeremy_corbyn_roles_committees_v1.py`

The prerequisite repair may only replace the roles test's closed-world assertion about all non-role fixture facts with a section-scoped non-interference assertion. It must not change any accepted role, committee, source, date, gap, report data or workflow.

Required behaviour:

- record the source URL, publisher, capture date, captured register version or publication date when available, pagination boundary, total displayed result count and source limitations;
- capture every entry in the current published member snapshot across all pages and categories at one declared capture time;
- preserve the official category, names, descriptions, values, relevant dates, destinations, purposes, donor status and rectification wording exactly as displayed, with missing fields left explicitly absent rather than inferred;
- preserve repeated entries and source spelling variants as separate source records;
- encode one `interest` fact per captured register entry and prove each fact resolves to its source packet entry;
- do not create donation, employment, company, relationship or position facts in this lane;
- do not calculate totals, merge donors, standardise names or infer that an entry remains active beyond the register's own retention rules;
- set `financial_interests` to `partial`, replacing the generic unresearched gap with an explicit open historical-register and retention-boundary gap;
- keep every other canonical section, existing fact, claim, interpretation, relationship, gap and review decision unchanged;
- keep the report `not_ready`, human review required and public output unauthorised;
- validate the complete fixture through the canonical Complete MP Report validator and deterministic generator;
- prove the encoded fact count equals the captured source result count and that every added fact has `fact_type: interest`, `confidence: high`, `evidence_status: verified` and only official Parliament source IDs;
- run the new lane regression, identity-and-career regression, repaired roles-and-committees regression, Complete MP Report fixture test, Complete MP Portfolio view test, Repository release validation and Project control;
- change exactly one file in the prerequisite regression-repair PR and exactly five files in the financial-interests implementation PR.

## Done

- Repository Release v1 and backup/restore proof are complete.
- January 2003 seed-row shape and vote-review queue preparation are complete.
- The accepted Streamlit interface exposes `Simple`, `MP Portfolio` and `Advanced` views.
- Jeremy Corbyn identity-and-career and roles-and-committees baselines are complete within their bounded official-source scopes.
- The `financial_interests` section remains `not_researched` in current `main`.
- Repository tracing identified that the roles regression currently rejects any future-section facts added to the shared fixture, which would make the authorised financial-interests fixture integration fail despite leaving the roles section unchanged.

## To do

- Repair the prior roles regression's closed-world assertion in one controlled one-file PR.
- Capture the full current official Registered Interests snapshot at one declared time.
- Create the machine-readable source packet and readable source note.
- Encode only the financial-interest section, official source records, `interest` facts and directly related coverage gap.
- Add deterministic validation and CI.
- Open and review one five-file implementation PR.
- After implementation merge, close this lane through a separate `STATUS.md`-only authority PR.

## Next bounded gate

Merge this authority clarification after Project control passes, merge the one-file regression repair after its existing checks pass, then open the five-file financial-interests implementation PR.

## Stop point

Do not research another MP or canonical section; alter accepted identity, roles, voting, donations, outside-work, speeches, positions, relationships or human-review records; use non-official sources; deduplicate or normalise source entries; calculate aggregates; infer impropriety, influence or motive; review January 2003 vote meanings; access or mutate the private server or SQLite; mark the section complete; mark the report publishable; or authorise public output. Stop after the five-file implementation PR is complete, tested and reviewed.

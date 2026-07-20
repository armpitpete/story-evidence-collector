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
- Exact starting head for this lane: `8bdf09238e6c75eb415793c91951e226b0b8184a`.
- Jeremy Corbyn current financial-interests baseline is complete at merge `e92262ccafa2e9628bc5e8f5bba6be4c14541750` from exact reviewed head `4dce322af5220c62b7b20537094ab7d683b966d9`.
- Jeremy Corbyn official roles-and-committees baseline remains complete at merge `968d33dac9e80cdf0f6c9107c195c5f7d7f70a1b`.
- Jeremy Corbyn official identity-and-career baseline remains complete at merge `93c8da204d9709a1490dfa24a7b722a5f6a85199`.
- Complete MP Portfolio vertical slice and local acceptance remain complete.
- January 2003 vote-review queue, Repository Release v1 and backup-and-restore hardening remain complete and authoritative.

## Current lane

Jeremy Corbyn current outside work and company links baseline.

Goal: replace the unresearched `outside_work_and_company_links` section with a bounded official-source baseline for the four organisations explicitly named in the accepted current UK Parliament Registered Interests snapshot, without expanding to unrelated companies, connected people, political-finance conclusions or relationship inference.

Canonical section:

- `outside_work_and_company_links`

Declared-link boundary from the accepted Parliament snapshot:

- Your Party UK Ltd;
- Jeremy Corbyn Campaign Ltd;
- Community Unity Limited;
- the Peace and Justice Project company named by the register.

Official source boundary:

- the accepted UK Parliament current financial-interests packet and the corresponding official Registered Interests entries, used only to record the member’s own declared role wording and dates;
- official Companies House company overview pages for exact registry identity, company number, status, incorporation date and registered nature of business;
- official Companies House officer pages or appointment records only for Jeremy Corbyn’s own appointment or termination dates;
- official Companies House filing history only when needed to resolve a company-name, status or appointment ambiguity;
- an explicit unresolved record when an exact official company match cannot be established without guessing.

Forbidden source classes and expansion:

- Wikipedia, newspapers, broadcasters, party, campaign or personal websites, social media, OpenCorporates, commercial company aggregators and search-result snippets;
- unrelated companies discovered through addresses, other officers, filing agents, shareholders, persons with significant control or connected organisations;
- inference about beneficial ownership, control, remuneration, influence, motive, political significance, legality or propriety;
- treating a bank-signatory declaration as directorship, employment, ownership or control;
- changing `financial_interests`, `donations_and_political_finance`, `organisations_and_relationships` or any other canonical section.

Authorised implementation scope:

- `research/complete-mp-reports/jeremy-corbyn/current-outside-work-company-links-v1.json`
- `docs/jeremy-corbyn-current-outside-work-company-links-source-note-v1.md`
- `fixtures/complete-mp-reports/jeremy-corbyn-fixture-v1.json`
- `scripts/test_jeremy_corbyn_current_outside_work_company_links_v1.py`
- `.github/workflows/jeremy-corbyn-current-outside-work-company-links-test.yml`

Required behaviour:

- preserve the four Parliament declarations exactly as already captured and link each new company record back to its source entry;
- establish the exact registered company name and number from Companies House before adding a `company` fact;
- record only company status, incorporation date, nature of business and Jeremy Corbyn’s own official appointment or termination dates when displayed;
- distinguish Parliament-declared unpaid director roles from the separately declared unpaid bank-signatory role;
- do not encode the bank-signatory declaration as a Companies House officer appointment unless Companies House independently records one;
- preserve any difference between Parliament wording and Companies House wording rather than silently reconciling it;
- create no donation, relationship, position, claim or interpretation record;
- leave the section `partial` with an explicit open historic outside-work and company-coverage gap;
- keep the report `not_ready`, human review required and public output unauthorised;
- preserve every accepted identity, roles, voting and financial-interests record unchanged;
- validate the complete fixture through the canonical Complete MP Report validator and deterministic generator;
- prove each added fact resolves only to the accepted Parliament source and/or official Companies House source records;
- prove no unrelated company, officer or organisation was added;
- run the new lane regression, identity-and-career regression, roles-and-committees regression, current financial-interests regression, Complete MP Report fixture test, Complete MP Portfolio view test, Repository release validation and Project control;
- change exactly the five authorised files.

## Done

- Repository Release v1 and backup/restore proof are complete.
- January 2003 seed-row shape and vote-review queue preparation are complete.
- The accepted Streamlit interface exposes `Simple`, `MP Portfolio` and `Advanced` views.
- Jeremy Corbyn identity-and-career, roles-and-committees and current financial-interests baselines are complete within their declared official-source scopes.
- The current Parliament snapshot supplies four bounded organisation/company declarations suitable for this lane.
- The `outside_work_and_company_links` section remains `not_researched` in current `main`.

## To do

- Resolve the exact Companies House identity for each of the four declared organisations without guessing.
- Capture the bounded official company and subject-officer records.
- Create the machine-readable source packet and readable source note.
- Update only the outside-work-and-company-links section, its official sources, company facts and directly related coverage gap.
- Add deterministic validation and CI.
- Open and review one five-file implementation PR.
- After implementation merge, close this lane through a separate `STATUS.md`-only authority PR.

## Next bounded gate

Merge this authority-only activation PR after Project control passes. Then conduct the bounded official-source research and open one controlled five-file implementation PR.

ChatGPT Work owns bounded official-source collection and exact fact extraction. Codex owns deterministic encoding, tests and fixture integration after the source packet is fixed. Neither may expand beyond the four declared organisations or the authorised source boundary.

## Stop point

Do not research another MP or canonical section; expand to unrelated companies or connected people; alter accepted identity, roles, voting, financial-interests, donations, speeches, positions, relationships or human-review records; infer ownership, control, remuneration, influence, motive, legality or propriety; review January 2003 vote meanings; access or mutate the private server or SQLite; create claims or interpretations; mark the section complete; mark the report publishable; or authorise public output. Stop after the five-file implementation PR is complete, tested and reviewed.

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
- Exact current main before this closure record: `97ff94d78fa50f9f8a0d7cf2c3bf68d0aff1eb9f`
- PR #226 merged at exact reviewed head `2c71dbd139a78a5fd93c57d192d8edcdf02d3fbb`.
- PR #226 merge commit: `97ff94d78fa50f9f8a0d7cf2c3bf68d0aff1eb9f`.
- All previously accepted Complete MP Report evidence, fixture and regression baselines remain authoritative.

### Governing project purpose

> Build a complete, traceable public evidence record for each MP, then use that evidence to reveal significant patterns, relationships, changes and inconsistencies that are difficult to see through ordinary human reading—without overstating what the evidence proves.

Every future lane must materially improve the final MP report, its evidence completeness, its traceability, its reproducible analytical capability or its interpretation safeguards. A lane must not be selected merely because another source exists.

## Closed lane

The **current-Parliament tabled oral questions source-interface proof** lane is complete.

The merged scope was exactly:

- `research/complete-mp-reports/jeremy-corbyn/current-parliament-tabled-oral-questions-source-interface-v1.md`
- `scripts/test_jeremy_corbyn_current_parliament_tabled_oral_questions_source_interface_v1.py`
- `.github/workflows/jeremy-corbyn-current-parliament-tabled-oral-questions-source-interface-test.yml`

The lane established that:

- the official UK Parliament Oral Questions API exposes `GET /oralquestions/list`;
- `parameters.askingMemberIds=185` identifies Jeremy Corbyn as the asking member;
- the fixed `2026-07-22` capture returned 12 member-filtered records;
- seven records met the inclusive current-Parliament `TabledWhen` boundary from `2024-07-04` through `2026-07-22`;
- five records were earlier;
- the API exposes no supported tabled-date or parliamentary-session filter;
- current-Parliament selection must therefore be applied locally to `TabledWhen`;
- API `Id`, not session-resetting `UIN`, is the paging and deduplication identity;
- an invalid-member control returned zero records;
- a complete fixed inventory is reproducible for records exposed by the official API at a fixed capture time.

The fixed evidence block is bound to SHA-256:

- `25cd378069d42a50c1a4c36d514f188767c4f2721cf95f6c8c5d2c3a48a40a5b`

The unbounded member-query response is bound to SHA-256:

- `f47822206b73bbac2fc557f6911750eda5165376905e3651323e59ccf02c94aa`

At exact PR head `2c71dbd139a78a5fd93c57d192d8edcdf02d3fbb`, the dedicated regression, compilation, evidence and hash assertions, member and paging assertions, date-boundary assertions, invalid-member control, exact three-file scope enforcement, `git diff --check`, Project Control and Repository Release validation passed.

The lane created no canonical oral-question inventory, Complete MP fixture record, classification, interpretation or public output. PR #226 is closed and merged.

## Current lane

One bounded **master MP report and analysis architecture contract** lane is selected and authorised only after this `STATUS.md`-only closure-and-authority record merges and the resulting exact `main` is verified.

The later architecture lane may create or change exactly:

- `docs/complete-mp-report-and-analysis-architecture-contract-v1.md`
- `scripts/test_complete_mp_report_and_analysis_architecture_contract_v1.py`
- `.github/workflows/complete-mp-report-and-analysis-architecture-contract-test.yml`

No other file is authorised.

The contract must define:

1. the governing project purpose exactly as recorded above;
2. intended users and the separation between readable report and evidence view;
3. the evidence-record, report-model, pattern-detection, interpretation-safeguard and controlled-public-presentation layers;
4. the complete intended MP report section catalogue;
5. section completeness states and required evidence;
6. traceability from official source through capture, inventory, canonical fact, report section, measured finding and public statement;
7. source authority, capture date, checksum, version, refresh and correction rules;
8. allowed pattern families: frequency, time change, co-occurrence, concentration, network, sequence, gap, cross-channel consistency and peer deviation;
9. the required distinction between fact, measured pattern, supported inference, unresolved possibility and unsupported claim;
10. confidence, comparison baseline, materiality, alternative explanation and non-proof requirements;
11. peer-comparison rules that prevent unlike MPs, roles, periods or coverage from being compared misleadingly;
12. acceptance criteria for calling one report pristine;
13. the ordered route from the Jeremy Corbyn proof report to a reusable report for every MP;
14. stop conditions for incomplete, conflicting, stale, inaccessible or interpretation-inadequate evidence;
15. the boundary between architecture definition and later implementation.

Before that lane can close, require the contract, a deterministic regression, a workflow that compiles and runs it, exact three-file scope enforcement, `git diff --check`, Project Control, Repository Release validation and a draft PR at an exact head for owner review.

The architecture lane does not authorise evidence capture or integration, Complete MP fixture or schema changes, pattern-algorithm implementation, analytical findings, commitment-versus-conduct comparison, delivery or contradiction assessment, reclassification, final-report production, public output, deployment or generalisation to other MPs.

## Done

- The current-Parliament Early Day Motions canonical fixture-integration lane is closed.
- The current-Parliament tabled oral questions source-interface proof lane is closed.
- PR #226 merged at exact authorised head.
- The governing project purpose is recorded as repository completion authority.
- The master MP report and analysis architecture contract lane is selected.
- Its exact future three-file scope, contract requirements, proof obligations and exclusions are recorded.

## To do

- merge this `STATUS.md`-only closure, purpose and lane-authority PR after Project Control passes;
- treat Repository Release validation as path-inapplicable to this metadata-only `STATUS.md` PR under its current trigger contract;
- verify the resulting exact `main` merge commit;
- from that exact `main`, open one draft three-file master MP report and analysis architecture contract PR;
- change only the three authorised architecture-contract files;
- define the architecture without implementing evidence capture, pattern detection, interpretation or public output;
- run the dedicated regression, exact-scope check, `git diff --check`, Project Control and Repository Release validation;
- stop at an exact PR head for owner review.

## Next bounded gate

After this `STATUS.md`-only authority PR merges, verify the resulting exact `main`. From that exact `main`, open one draft three-file master MP report and analysis architecture contract PR using only the authorised scope. Define the complete report model, evidence-to-finding traceability, pattern families, interpretation safeguards, pristine-report acceptance standard and Jeremy-Corbyn-to-all-MPs route. Run all required checks and stop at an exact PR head for owner review.

## Stop point

Do not begin the architecture contract lane before this closure-and-authority record merges and the resulting exact `main` is verified. Do not create or modify an architecture-contract file in this authority PR. Do not capture or integrate further evidence, modify the Complete MP fixture, implement pattern detection, produce analytical findings, compare commitments with conduct, assess delivery or contradiction, create the final Jeremy Corbyn report, generalise to other MPs, authorise public output, publish or deploy.

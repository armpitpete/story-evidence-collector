# Complete MP Report and Analysis Architecture Contract v1

**Status:** architecture definition only
**Authority base:** `e8273d415d513f055347d71a09d7c61517d609da`
**Subject proof route:** Jeremy Corbyn first; reusable MP architecture later
**Publication authority:** none

## Governing project purpose

> Build a complete, traceable public evidence record for each MP, then use that evidence to reveal significant patterns, relationships, changes and inconsistencies that are difficult to see through ordinary human reading—without overstating what the evidence proves.

Every later source, model, analysis and presentation lane must materially improve evidence completeness, traceability, reproducibility or interpretation safety. The existence of another available source is not by itself a reason to add a lane.

## Architecture layers

The complete system has five separated layers:

1. **Evidence-record layer** — immutable captures, source inventories, canonical source records, canonical facts, coverage gaps and correction history.
2. **Report-model layer** — one scoped MP record with the complete section catalogue, section-completeness decisions and links to every supporting record.
3. **Measured-analysis layer** — deterministic calculations over versioned fact sets, limited to the allowed pattern families in this contract.
4. **Interpretation-safeguard layer** — classification, confidence, materiality, baseline, alternative-explanation, peer-comparison and human-review controls.
5. **Controlled-presentation layer** — a readable report and a separate evidence view, with every public statement linked back through the complete traceability chain.

No layer may silently repair, reinterpret or conceal a failure in an earlier layer. Presentation cannot convert incomplete evidence into apparent certainty.

## Complete MP report model and section catalogue

The report envelope must identify the MP, the exact research scope, the as-of time, publication state, section-completeness decisions, source register, facts, measured patterns, interpretations, relationships, evidence gaps, review decisions, correction history and public statements.

The canonical section catalogue remains the following thirteen sections, in this order:

| Section ID | Readable-report purpose | Pristine requirement |
|---|---|---|
| `identity_and_parliamentary_career` | Establish the correct person, seats, party or affiliation, elections and service chronology. | Identity is unambiguous and the declared career scope is complete or has a justified accepted limit. |
| `roles_and_committees` | Record parliamentary, party, government, opposition and committee roles over time. | Eligible role classes and periods are covered with role dates and authority. |
| `voting_record_and_coverage` | Describe vote participation and positions while stating the limits of available division records. | The declared vote universe, absences, eligibility and coverage denominator are reproducible. |
| `financial_interests` | Record declared financial interests and the retention boundaries of each register. | Every in-scope register edition is captured, versioned and reconciled. |
| `donations_and_political_finance` | Record regulated donations, visits, benefits, loans and relevant political-finance records. | Entity identity, transaction type, dates, values and database limits are reconciled. |
| `outside_work_and_company_links` | Record paid work, directorships, clients and official company or organisation links. | Current and in-scope historic links are resolved against authoritative records. |
| `speeches_and_questions` | Record parliamentary speeches, written and oral questions, motions and other authorised contribution classes. | Every declared channel has a complete fixed inventory or an explicit accepted limit. |
| `public_positions_over_time` | Record attributable public positions and commitments as dated evidence, not summaries of reputation. | Each position has exact wording, date, venue, source and classification review. |
| `changes_and_contradictions` | Compare like statements or conduct across time without treating every change as contradiction. | The compared propositions, periods, context, baseline and alternative explanations are explicit. |
| `organisations_and_relationships` | Show defined, evidenced relationships without implying hidden influence. | Every edge has a neutral type, dates, sources, confidence and public-chart decision. |
| `evidence_gaps` | Make missing, inaccessible, conflicting and unresolved evidence visible. | Every known gap has status, severity, consequence and next action or accepted-limit decision. |
| `source_register` | Expose source authority, captures, checksums, versions, coverage and corrections. | Every used source and capture is registered and every derived record resolves to it. |
| `human_review` | Record the decisions that permit or block findings and public wording. | Required reviews are complete, attributable, dated and linked to the reviewed records. |

The readable report may group or shorten material for comprehension, but it must not remove a section, hide a completeness state or break the route to the evidence view.

## Readable report and evidence view

The **readable report** is the human-facing explanation. It contains scoped summaries, material facts, approved measured patterns, carefully worded supported inferences, visible limitations and direct routes to supporting evidence. It must state what period and source universe each finding covers.

The **evidence view** is the inspection surface. It contains source metadata, captures, checksums, inventories, canonical facts, transformations, denominators, calculation inputs, result records, review decisions, gaps, alternative explanations, corrections and superseded records.

A readable statement must have a stable public-statement ID and link to one evidence-view trace. The evidence view may contain unresolved possibilities and rejected claims for audit purposes, but the readable report must not present them as findings. Evidence detail must remain available even when the readable report is shortened.

## Full source-to-public-statement traceability chain

Every public statement must resolve through this ordered chain without a skipped link:

1. **Official source record** — the originating first-party or otherwise explicitly rated record.
2. **Immutable capture** — the exact captured bytes or structured response with request identity and capture time.
3. **Source inventory** — the bounded record universe, paging and inclusion or exclusion decisions.
4. **Canonical source record** — authority, coverage, checksum, version and limitations.
5. **Canonical fact** — a neutral proposition directly supported by one or more source records.
6. **Report-section placement** — the fact's role in one section and its effect on section completeness.
7. **Measurement dataset** — the exact versioned fact set, exclusions, denominator and transformation inputs.
8. **Measured pattern** — a reproducible result from an allowed pattern family.
9. **Interpretation and review decision** — classification, safeguards, alternatives and approved wording boundary.
10. **Public statement** — the exact readable wording, evidence-view link, as-of date and correction state.

The chain may stop at a canonical fact when no analysis is justified. A measured pattern cannot cite only a readable summary. A public statement cannot cite only an interpretation. Each derived step must preserve identifiers for every immediate input and the software or rule version that produced it.

## Section completeness states

A section has exactly one primary completeness state:

- `not_researched` — no adequate bounded research has been completed.
- `partial` — some in-scope evidence is present, but material classes, periods or checks remain open.
- `complete` — all evidence required by the declared scope and acceptance rules is captured, reconciled and current.
- `accepted_limit` — complete research reached a demonstrable external boundary; the missing material, attempts and consequences are explicit and approved.
- `not_applicable` — the section or a declared sub-class genuinely does not apply to the MP, with supporting evidence.
- `blocked` — access, identity, parser, legal or source failure prevents completion.
- `stale` — the section was complete or accepted-limit but has passed its refresh boundary or a material new edition exists.
- `conflicting` — authoritative records materially disagree and the conflict is unresolved.
- `human_review_required` — evidence or calculation exists, but a required interpretation or risk review is incomplete.

`complete`, `accepted_limit` and `not_applicable` are the only terminal research states. `accepted_limit` and `not_applicable` must remain visibly qualified; neither may be used to disguise work that is merely unstarted or inconvenient. Any stale, conflicting, blocked or review-required state blocks pristine acceptance.

## Source authority, capture, checksum, version, refresh and correction rules

### Authority

Authority is claim-specific. Official primary records, regulators, courts, electoral records and statutory registries normally outrank secondary descriptions for facts within their remit. Official secondary material may explain but cannot silently replace an available primary record. Reputable reporting and research may supply context or independently evidenced facts, but reported possession of evidence is not the evidence itself. No source is trusted beyond what it can directly support.

### Capture

A source used for a canonical fact must have an immutable capture or a documented reason why lawful capture is impossible. The capture record must include the canonical URL or endpoint, request parameters, UTC capture time, response identity, publication or edition date when available, coverage dates, content type, retrieval result and limitations. Live-link-only evidence is insufficient for a pristine report.

### Checksum

Raw captures require SHA-256 checksums over the exact stored bytes. Canonicalised inventories and derived datasets require separate deterministic checksums. A transformed checksum must never be presented as the raw-capture checksum. Checksum mismatch stops use until the version difference is explained and reconciled.

### Version

Captures are immutable and append-only. Source records, inventories, facts, datasets, measurements, reviews and public statements require stable IDs and explicit versions. Every derived record must name its input versions, schema version and transformation or code version. Superseded records remain inspectable.

### Refresh

Each source class must have a declared refresh trigger: fixed schedule, new official edition, parliamentary event, correction notice or manual risk review. Every section records its last successful refresh and next due boundary. A missed boundary changes affected sections to `stale`; it does not silently preserve `complete`.

### Correction

Corrections never overwrite history. A correction creates a new capture or record version, states why it changed, links the superseded version, identifies affected facts, measurements, interpretations and public statements, and records the review outcome. Material public errors require visible amendment or withdrawal. A correction cannot broaden a claim beyond the new evidence.

## Allowed pattern families

Only these pattern families are architecturally allowed:

1. `frequency` — counts or rates within a declared record universe and denominator.
2. `time_change` — change between predeclared comparable periods.
3. `co_occurrence` — items appearing together within a defined unit, without treating association as cause.
4. `concentration` — distribution across topics, organisations, donors, channels or periods using a declared measure.
5. `network` — patterns in explicitly defined evidenced relationships, without inferring hidden influence.
6. `sequence` — ordered events or statements where chronology is complete enough for the stated conclusion.
7. `gap` — systematic absence, missing coverage or non-observation, distinguished from evidence that an event did not occur.
8. `cross_channel_consistency` — comparison of like propositions across votes, speeches, questions, declarations or other channels.
9. `peer_deviation` — measured difference from a valid comparable cohort, never a standalone judgement of merit.

A later implementation may use more than one family for a finding, but every family and calculation must be declared. Topic classification, entity resolution or statement matching are supporting transformations, not additional pattern families and not findings by themselves.

## Evidence and conclusion classes

Every candidate statement must be assigned exactly one class:

- **Fact** — a neutral proposition directly supported by identified evidence, with no analytical leap.
- **Measured pattern** — a deterministic result produced from a versioned dataset by a declared allowed method.
- **Supported inference** — a cautious interpretation that follows from facts or measured patterns after safeguards and human review; it must state that it is an inference.
- **Unresolved possibility** — a plausible explanation or question not sufficiently supported to become an inference; retained only for review and future research.
- **Unsupported claim** — a statement that lacks adequate evidence, uses an invalid comparison or exceeds what the evidence can prove; rejected from report findings and public wording.

Facts and measured patterns may appear in the readable report when their scope and limitations are visible. Supported inferences require explicit human approval. Unresolved possibilities may be shown only as clearly labelled open questions when there is a public-interest reason and a reviewer approves that limited wording. Unsupported claims must not be published as findings.

## Analytical safeguards

### Confidence

Evidence confidence and analytical confidence are separate. Evidence confidence assesses identity, authority, completeness, consistency and capture integrity. Analytical confidence assesses dataset fitness, measurement stability, classification reliability, sensitivity and review. A high analytical score cannot repair weak evidence. Public wording must follow the lower applicable confidence.

### Materiality

A finding must meet a predeclared materiality rule appropriate to its family. Materiality may depend on absolute size, rate, persistence, monetary value, institutional relevance or public consequence. Statistical difference alone is not automatically materially significant. Thresholds chosen after seeing the result invalidate the finding until independently re-specified and rerun.

### Comparison baseline

Every comparison must declare its question, unit, denominator, period, inclusion rules and baseline before interpretation. Baselines selected because they make the subject appear unusual are prohibited. Where more than one reasonable baseline exists, sensitivity across those baselines must be recorded.

### Alternative explanations

Before a supported inference, reviewers must record credible alternative explanations and identify which are contradicted, consistent, untestable or still open. Role, opportunity, parliamentary procedure, source retention, media exposure, constituency demand, party status and changing external events must be considered when relevant. Failure to resolve an alternative does not prove it; it lowers or blocks the inference.

### Non-proof safeguards

Correlation, sequence, contact, donation, membership, shared language, absence from a source and peer deviation do not by themselves prove motive, causation, control, influence, dishonesty, corruption, effectiveness or wrongdoing. The report must say what the evidence does not prove whenever a reasonable reader could otherwise overread the finding.

## Peer-comparison rules

Peer comparison is permitted only when:

- the comparison question is defined before selecting the cohort;
- MPs are comparable for chamber, eligibility, role, government or opposition status, party or independent status where relevant, tenure and exposure opportunity;
- periods and parliamentary sessions align or are normalised transparently;
- every MP has materially equivalent source coverage, capture freshness and classification rules;
- raw counts are not used where opportunity-adjusted rates or denominators are required;
- missingness, abstentions, absences, role restrictions and source-retention differences are represented rather than treated as zero;
- the cohort size, inclusion rules, exclusions, distribution and outliers are visible;
- multiple reasonable cohorts are tested when cohort choice could change the conclusion;
- no peer rank is presented as a moral, competence, integrity or effectiveness score without separately authorised evidence and methodology;
- a reviewer confirms that the comparison is like-for-like enough for the exact public wording.

A subject may be reported as different from a cohort only for the measured variable and bounded period. Peer deviation alone cannot establish motive, importance, influence, effectiveness or wrongdoing.

## Pristine report acceptance standard

A report is **pristine** only when all of the following are true:

1. MP identity and scope are unambiguous, versioned and current.
2. Every mandatory section is `complete`, `accepted_limit` or evidenced `not_applicable`.
3. No section is `not_researched`, `partial`, `blocked`, `stale`, `conflicting` or `human_review_required`.
4. Every in-scope source has authority, capture, checksum, coverage, version, refresh and limitation records.
5. Every fact resolves through the full source and capture chain.
6. Every measured pattern is reproducible from fixed input versions with declared code, parameters, denominators and outputs.
7. Every candidate statement is assigned one evidence-and-conclusion class.
8. Every supported inference has confidence, materiality, baseline, alternatives, non-proof wording and attributable human approval.
9. Every peer comparison satisfies the complete peer-comparison rules.
10. Every known gap, conflict, inaccessible source and accepted limit is visible in both the section state and evidence view.
11. Every readable public statement has a stable ID, exact evidence trace, as-of date and correction state.
12. Deterministic report, traceability, analysis, scope and release regressions pass at the exact reviewed head.
13. A final independent human review confirms that wording does not exceed the evidence.
14. Publication remains separately authorised; pristine status alone does not publish, deploy or authorise public output.

## Route from the Jeremy Corbyn proof report to every MP

The ordered route is:

1. **Architecture contract** — fix the model, safeguards, completeness states and acceptance standard without implementation.
2. **Jeremy Corbyn source completion** — finish the declared source universe and accepted-limit decisions one bounded lane at a time.
3. **Jeremy Corbyn canonical evidence completion** — reconcile all captures, inventories, facts, relationships, gaps and corrections.
4. **Jeremy Corbyn measured-analysis proof** — implement one allowed family at a time with fixed datasets, negative fixtures and interpretation controls.
5. **Jeremy Corbyn pristine proof report** — satisfy every pristine criterion before any generalisation claim.
6. **Contrasting-MP shadow proof** — test the architecture on one separately authorised MP with materially different tenure, role or affiliation, without publication.
7. **Calibration cohort** — use a separately authorised small cohort to test source parity, denominators, classifications and peer-comparison rules.
8. **Reusable implementation contract** — freeze schemas, interfaces, generators, validators, correction handling and migration rules only after the proofs expose their real requirements.
9. **Current-MP controlled expansion** — create evidence records for current MPs in bounded batches, with per-MP completeness and review gates.
10. **Every-MP completion programme** — extend to the authorised historic or current population only when source coverage, compute, review capacity and correction operations are demonstrably sustainable.
11. **Per-report publication gate** — require pristine acceptance and separate owner publication authority for each MP or explicitly authorised batch.

Passing a Jeremy Corbyn proof does not prove universal fitness. Each generalisation step must test a new source, role, tenure or comparison risk and may require the architecture to return to draft.

## Failure and stop conditions

Stop the affected lane or finding when any of these occurs:

- exact base, head, authorised scope or governing contract changes;
- MP identity or source attribution is ambiguous;
- an in-scope source is inaccessible, incomplete, unexpectedly paginated, silently changed or cannot be lawfully captured;
- capture, checksum, version or lineage cannot be reproduced;
- source editions conflict materially and reconciliation is unresolved;
- a section is stale or its refresh boundary is unknown;
- inventory completeness, inclusion rules or denominator cannot be established;
- parser, entity-resolution, classification or statement-matching behaviour drifts beyond its accepted regression;
- a pattern falls outside the allowed families or cannot be reproduced deterministically;
- materiality or comparison baselines were selected after results were seen;
- a peer cohort lacks coverage parity or like-for-like opportunity;
- credible alternative explanations are omitted or public wording exceeds the lower confidence;
- the evidence supports only an unresolved possibility or unsupported claim;
- required human review is missing, conflicted or not attributable;
- a correction affects a finding and the downstream report has not been revalidated;
- pristine or publication status is requested despite a blocking state;
- work would cross from architecture definition into later implementation without separate authority.

A stop must be recorded as a visible gap, failure or deferred decision. The system must not substitute secondary material, broader claims, relaxed tests or presentation polish to make the report appear complete.

## Architecture and implementation boundary

This contract defines the target architecture, vocabulary, invariants, acceptance gates and ordered proof route. The dedicated regression validates only that this definition remains complete and internally fixed.

This lane does **not** authorise evidence capture, source integration, fixture or schema changes, database or server work, pattern-detection code, analytical calculations, findings about Jeremy Corbyn or any other MP, final-report generation, public-output design, publication, deployment or generalisation to other MPs. Every implementation lane requires a later exact base, exact file scope, deterministic proof and separate authority.

## Deterministic contract block

The following block is the machine-checked architecture index. It does not replace the fuller rules above.

<!-- BEGIN COMPLETE_MP_REPORT_ANALYSIS_ARCHITECTURE_V1 -->
```json
{
  "authority_base": "e8273d415d513f055347d71a09d7c61517d609da",
  "contract_version": "1",
  "epistemic_classes": [
    "fact",
    "measured_pattern",
    "supported_inference",
    "unresolved_possibility",
    "unsupported_claim"
  ],
  "layers": [
    "evidence_record",
    "report_model",
    "measured_analysis",
    "interpretation_safeguard",
    "controlled_presentation"
  ],
  "pattern_families": [
    "frequency",
    "time_change",
    "co_occurrence",
    "concentration",
    "network",
    "sequence",
    "gap",
    "cross_channel_consistency",
    "peer_deviation"
  ],
  "pristine_terminal_states": [
    "complete",
    "accepted_limit",
    "not_applicable"
  ],
  "route": [
    "architecture_contract",
    "jeremy_corbyn_source_completion",
    "jeremy_corbyn_canonical_evidence_completion",
    "jeremy_corbyn_measured_analysis_proof",
    "jeremy_corbyn_pristine_proof_report",
    "contrasting_mp_shadow_proof",
    "calibration_cohort",
    "reusable_implementation_contract",
    "current_mp_controlled_expansion",
    "every_mp_completion_programme",
    "per_report_publication_gate"
  ],
  "section_states": [
    "not_researched",
    "partial",
    "complete",
    "accepted_limit",
    "not_applicable",
    "blocked",
    "stale",
    "conflicting",
    "human_review_required"
  ],
  "sections": [
    "identity_and_parliamentary_career",
    "roles_and_committees",
    "voting_record_and_coverage",
    "financial_interests",
    "donations_and_political_finance",
    "outside_work_and_company_links",
    "speeches_and_questions",
    "public_positions_over_time",
    "changes_and_contradictions",
    "organisations_and_relationships",
    "evidence_gaps",
    "source_register",
    "human_review"
  ],
  "source_controls": [
    "authority",
    "capture",
    "checksum",
    "version",
    "refresh",
    "correction"
  ],
  "traceability_chain": [
    "official_source_record",
    "immutable_capture",
    "source_inventory",
    "canonical_source_record",
    "canonical_fact",
    "report_section_placement",
    "measurement_dataset",
    "measured_pattern",
    "interpretation_and_review_decision",
    "public_statement"
  ]
}
```
<!-- END COMPLETE_MP_REPORT_ANALYSIS_ARCHITECTURE_V1 -->

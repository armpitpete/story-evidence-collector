# Complete MP Report Specification v1

## Status

Canonical repository authority for complete MP reports.

This specification defines what one finished MP report must contain, how evidence and interpretation are separated, and what must remain visible when source coverage is incomplete.

It extends the existing `power_profile` Evidence Pack direction. It does not replace Evidence Pack v1. Evidence Packs hold research records; the complete MP report is the deterministic, reviewable output assembled from those records and other structured evidence stores.

## Purpose

A complete MP report should answer:

> What is publicly recorded about this MP's parliamentary career, actions, declared interests, political finance, public positions and evidenced relationships, and where does the public record remain incomplete?

A report is not complete because every section contains data. It is complete when every required section has been assessed and given an explicit coverage status.

## Core principles

1. **Facts first.** Record what a source proves before offering interpretation.
2. **No hidden gaps.** Missing, partial and unavailable evidence must remain visible.
3. **No motive inference.** Public records do not prove private intention or belief.
4. **No guilt by association.** A documented relationship is not evidence of wrongdoing.
5. **Every public claim is traceable.** Claims must resolve to sources and structured facts.
6. **Interpretation is labelled.** Interpretations cannot be presented as facts.
7. **Human review remains mandatory.** Political, legal and reputational risk cannot be delegated to the generator.
8. **Generation is deterministic.** The generator formats approved records. It does not browse, research or infer.

## Required report sections

Every report must contain exactly these canonical section IDs:

| Section ID | Human title | Required scope |
|---|---|---|
| `identity_and_parliamentary_career` | Identity and parliamentary career | Stable identity, Parliament IDs, constituencies, party history and service periods |
| `roles_and_committees` | Roles and committees | Ministerial, opposition, parliamentary and committee roles with dates |
| `voting_record_and_coverage` | Voting record and coverage | Available vote records, source boundaries, unresolved periods and meaning-review status |
| `financial_interests` | Financial interests | Register entries, editions, categories, values where declared, and change history |
| `donations_and_political_finance` | Donations and political finance | Electoral Commission and other authoritative political-finance records |
| `outside_work_and_company_links` | Outside work and company links | Declared employment, directorships, consultancies and evidenced company matches |
| `speeches_and_questions` | Speeches and parliamentary questions | Hansard contributions, questions, corrections and indexed themes |
| `public_positions_over_time` | Public positions over time | Dated, sourced statements and actions on defined subjects |
| `changes_and_contradictions` | Changes and contradictions | Evidence-led comparison of dated records, including explanations or denials |
| `organisations_and_relationships` | Organisations and evidenced relationships | Defined public relationships with source, dates, confidence and neutral wording |
| `evidence_gaps` | Evidence gaps | Missing periods, inaccessible sources, unresolved identity matches and research limits |
| `source_register` | Source register | All sources used, authority, capture date, limits and stable identifiers |
| `human_review` | Human review | Review decisions, unresolved risks, publication status and reviewer notes |

## Section coverage statuses

Each required section must use one status:

| Status | Meaning |
|---|---|
| `complete` | All evidence expected for the declared scope was collected and checked |
| `partial` | Useful evidence exists, but a material boundary or missing period remains |
| `not_available` | The evidence is not publicly available or the source cannot provide it |
| `not_researched` | The lane has not yet been researched |
| `human_review_required` | Evidence exists but cannot safely be summarised before review |

`complete` applies only to the report's declared scope. It must not imply that every possible historical record exists.

## Record classes

### Source

A source record describes where evidence came from and how much weight it should carry.

It records:

- stable source ID;
- title and publisher;
- source type and authority level;
- URL, repository path or server path;
- publication and capture dates;
- coverage period;
- limitations.

### Fact

A fact is a narrowly worded statement directly supported by one or more sources.

It must include:

- stable fact ID;
- section ID;
- statement;
- source IDs;
- confidence;
- evidence status;
- relevant date or date range where applicable.

A fact must not include speculation about motive.

### Claim

A claim is a report-level proposition assembled from facts or direct source evidence.

A claim must be marked:

- `supported`;
- `partially_supported`;
- `contested`;
- `unsupported`;
- `needs_review`.

Unsupported claims remain private and must not be rendered as conclusions.

### Interpretation

An interpretation explains what the evidence may mean. It is explicitly labelled and linked to its supporting facts or claims.

Interpretations always require human review before publication.

### Relationship

A relationship is a defined public connection between the MP and a person or organisation.

Examples include:

- employed by;
- director of;
- member of;
- appointed by;
- donor to;
- donation received from;
- adviser to;
- committee member;
- declared client;
- public campaign support.

Avoid vague labels such as `linked to`. Every public relationship requires a source and confidence of `medium` or `high`.

### Coverage gap

A coverage gap identifies:

- affected section;
- date range or source where relevant;
- severity;
- reason;
- next action;
- whether the gap blocks publication.

### Review decision

A review decision records a human judgement about evidence quality, wording, risk or publication.

The generator may display review decisions. It must not create them.

## Publication states

A report uses one publication state:

- `not_ready`
- `needs_review`
- `publishable`
- `archived`

A report cannot be treated as `publishable` when:

- any blocking coverage gap remains open;
- any public claim is unsupported;
- a high-risk interpretation lacks approval;
- required human review is incomplete;
- source references do not resolve;
- required sections are absent.

## Output set

The canonical generator writes:

```text
<slug>-full-profile.json
<slug>-full-profile.md
<slug>-source-register.md
<slug>-coverage-report.md
<slug>-human-review.md
```

The JSON file is a normalised copy of the structured input.

The Markdown files are views of the same records. They are not new evidence.

## Generator boundaries

The generator may:

- validate required structure and cross-references;
- sort records deterministically;
- render coverage and evidence summaries;
- write the canonical output set;
- stop on invalid references or duplicate IDs.

It must not:

- access the network;
- read the live server unless explicitly given an input export;
- infer missing facts;
- turn source titles into political meaning;
- decide that evidence is true;
- resolve contradictions;
- mark a report publishable;
- hide empty or incomplete sections.

## First proof target

The first real proof target remains one long-serving MP because that tests:

- multiple parliamentary periods;
- historic and modern voting sources;
- long service and role histories;
- changes in public position;
- repeated register editions;
- source gaps across decades.

The included fixture is deliberately not publication-ready. It proves the schema and generator, not the completeness of the MP research.

## Acceptance checks

The v1 implementation is accepted when:

1. the schema parses as valid JSON;
2. the fixture parses as valid JSON;
3. all 13 canonical sections are present;
4. duplicate record IDs are rejected;
5. unresolved source, fact, claim and gap references are rejected;
6. the generator writes all five outputs;
7. repeated runs with the same input produce identical output;
8. the fixture remains `not_ready`;
9. no network or live-server access is used;
10. generated prose does not claim source completeness beyond recorded coverage.

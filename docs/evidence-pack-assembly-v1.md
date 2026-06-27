# Evidence Pack Assembly v1

## Purpose

An evidence pack is the complete file-based proof bundle for one TWIS investigation, article, audit, or contradiction check.

It brings together:

- source records
- claim records
- evidence items
- search diary records
- negative evidence log entries
- source authority map entries
- public record timeline entries
- denial check notes
- human review notes
- final brief

The pack must be understandable without a database.

The database may index, search, filter, and compare evidence packs later, but the proof itself must live in files.

## Core Principle

The proof lives in files.

The database helps find it later.

An evidence pack should still be readable if it is copied, archived, zipped, printed, or reviewed by another person.

## TWIS Evidence Rule

TWIS must not overclaim.

Each pack must separate:

- fact
- interpretation
- uncertainty
- absence of evidence
- contradiction
- public record change
- human review need

TWIS does not punish changed minds.

TWIS checks whether the public record has been denied, rewritten, hidden, softened, blurred, or made hard to follow.

## Evidence Pack Folder Shape

Recommended structure:

    evidence-packs/
      <pack-id>/
        pack.json
        README.md
        sources/
          source-records.jsonl
          source-authority-map.jsonl
        claims/
          claim-records.jsonl
        evidence/
          evidence-items.jsonl
        search/
          search-diary.jsonl
          negative-evidence-log.jsonl
        timeline/
          public-record-timeline.jsonl
          denial-checks.jsonl
        review/
          human-review.jsonl
        output/
          final-brief.md
          evidence-summary.md
          contradiction-brief.md

## Pack ID

A pack ID should be stable and readable.

Recommended format:

    YYYY-MM-DD-topic-short-name

Example:

    2026-06-22-starmer-resignation-power-crisis

The pack ID should not change just because the title changes.

## pack.json

pack.json is the control file for the evidence pack.

It should describe:

- what the pack is about
- why it was created
- what question it is trying to answer
- what files belong to it
- whether the pack is draft, reviewed, or publishable
- what still needs human checking

Minimum fields:

    {
      "pack_id": "2026-06-22-example-topic",
      "title": "Example evidence pack",
      "status": "draft",
      "created_at": "2026-06-22T00:00:00Z",
      "updated_at": "2026-06-22T00:00:00Z",
      "research_question": "What is being checked?",
      "scope": "What is inside and outside this pack?",
      "editorial_risk": "low|medium|high",
      "publishability": "not_ready|needs_review|publishable",
      "human_review_required": true,
      "records": {
        "source_records": "sources/source-records.jsonl",
        "source_authority_map": "sources/source-authority-map.jsonl",
        "claim_records": "claims/claim-records.jsonl",
        "evidence_items": "evidence/evidence-items.jsonl",
        "search_diary": "search/search-diary.jsonl",
        "negative_evidence_log": "search/negative-evidence-log.jsonl",
        "public_record_timeline": "timeline/public-record-timeline.jsonl",
        "denial_checks": "timeline/denial-checks.jsonl",
        "human_review": "review/human-review.jsonl"
      },
      "outputs": {
        "final_brief": "output/final-brief.md",
        "evidence_summary": "output/evidence-summary.md",
        "contradiction_brief": "output/contradiction-brief.md"
      }
    }

## Record Relationships

The pack should be built around stable IDs.

Recommended relationship model:

    source_record
      -> source_authority_map_entry
      -> evidence_item
      -> claim_record
      -> public_record_timeline_entry
      -> denial_check
      -> human_review
      -> final_brief

A final brief should never contain a serious claim unless it links back to evidence items and source records.

## Source Records

Source records describe where information came from.

They should answer:

- What is the source?
- Who published it?
- When was it published?
- When was it collected?
- Is there an archived copy?
- Is the source primary, secondary, official, journalistic, campaign material, commentary, or unknown?

## Source Authority Map

The source authority map explains how much weight a source should carry.

It should not treat all sources as equal.

Example source weight factors:

- official record
- direct quote
- primary document
- archived version
- contemporary reporting
- later interpretation
- partisan material
- unsourced claim
- social media clip without full context

Authority does not mean truth by itself.

It means the source has a known evidential role.

## Claim Records

Claim records describe what is being said.

They should separate:

- exact claim
- claimant
- date
- context
- whether the claim is factual, interpretive, predictive, denial-based, or rhetorical
- what evidence supports it
- what evidence weakens it
- what needs human review

## Evidence Items

Evidence items are the usable proof fragments.

Each evidence item should connect:

- a source record
- a claim record where relevant
- a short evidence summary
- the exact location in the source
- any quote or paraphrase
- archive information
- confidence level
- review status

Evidence items should be small enough to check.

## Search Diary

The search diary records how the evidence was looked for.

It should include:

- search terms
- dates searched
- source types searched
- filters used
- pages checked
- useful results
- dead ends
- why the search was stopped

This matters because it shows method, not just results.

## Negative Evidence Log

The negative evidence log records what was searched for but not found.

It should not claim that something does not exist unless the search was strong enough.

Use careful wording:

- not found in this search
- not found in checked official records
- not found in the sources reviewed so far

Avoid overclaiming:

- does not exist
- never happened
- no evidence anywhere

## Public Record Timeline

The public record timeline shows how statements, actions, omissions, explanations, and denials changed over time.

It should include:

- date
- event
- source
- public statement
- later action
- later explanation
- possible contradiction
- uncertainty
- human review need

A timeline is not automatically proof of contradiction.

It is a structured way to see whether the public record changed.

## Denial Checks

A denial check compares a denial, softening, correction, or later explanation against earlier records.

It should ask:

- What was denied?
- What was previously said or done?
- Is the denial literal, partial, misleading, or unclear?
- Is there missing context?
- Could this be a genuine changed position?
- What wording is safe to publish?

## Human Review

Human review is required before publication when:

- the subject is a living person
- the claim could damage reputation
- the evidence is incomplete
- the source is partisan or weak
- the contradiction is interpretive
- the wording could overstate what is proven
- legal, employment, medical, or safeguarding issues may be involved

Human review should record:

- reviewer
- date
- issue reviewed
- decision
- safe wording
- unresolved risk

## Final Brief

The final brief is the publishable or near-publishable summary.

It should include:

- the question
- the short answer
- what is proven
- what is interpretation
- what remains uncertain
- key sources
- key timeline points
- contradiction or no-contradiction finding
- safe wording recommendation
- publication risk level

The final brief should be written in plain language.

## Publishability Levels

Use these levels:

- not_ready
- needs_review
- publishable

### not_ready

The pack is incomplete.

Use when:

- key sources are missing
- claims are not linked to evidence
- timeline is not checked
- human review is still required

### needs_review

The pack has useful evidence but should not be published yet.

Use when:

- wording risk remains
- contradiction is plausible but not settled
- source authority is mixed
- a human needs to check the final claim

### publishable

The pack is ready to support publication.

Use only when:

- claims link back to evidence
- source authority is clear
- uncertainty is stated
- risky claims have human review
- final wording does not overclaim

## Good Evidence Pack Test

A pack is good enough when another person can answer these questions without asking the original researcher:

1. What question was investigated?
2. What sources were checked?
3. What was found?
4. What was not found?
5. Which claims are proven?
6. Which claims are interpretation?
7. What remains uncertain?
8. What needs human review?
9. What wording is safe?
10. What proof supports the final brief?

## Non-Goals

Evidence Pack Assembly v1 does not create a database schema.

It does not decide the final article structure.

It does not automate judgement.

It defines how proof files fit together into one usable evidence pack.

## Later Versions

Later versions may add:

- JSON Schema for pack.json
- CLI pack validation
- pack completeness scoring
- evidence graph generation
- contradiction map generation
- archive integrity checks
- export to Markdown, PDF, and HTML
- database indexing
- pack comparison across topics

---

## Evidence Pack creation checklist

Use this checklist before validating or sharing an evidence pack.

- [ ] Create one folder for the evidence pack.
- [ ] Add a manifest file for the pack.
- [ ] Give the pack a stable `pack_id`.
- [ ] Give the pack a clear `title`.
- [ ] Set the pack `status` to an allowed value.
- [ ] Add only expected top-level manifest fields.
- [ ] Store records in JSONL files.
- [ ] Make each JSONL line a valid JSON object.
- [ ] Give every JSONL record a stable `id`.
- [ ] Check that record IDs are not duplicated inside the same JSONL file.
- [ ] Keep record paths inside the evidence-pack folder.
- [ ] Do not use absolute paths.
- [ ] Do not use `..` path traversal.
- [ ] Run the evidence-pack validator.
- [ ] Run the validator failure regression tests before changing validator behaviour.

Good enough rule:

> A new person should be able to open the pack, read the manifest, inspect the records, and follow the proof trail without guessing where files or IDs came from.

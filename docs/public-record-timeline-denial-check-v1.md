# Public Record Timeline and Denial Check Schema v1

## Purpose

This schema adds a fairer public-record check to TWIS evidence work.

It replaces crude contradiction-finding with this stricter question:

Did the person or body previously say X, and are they now denying, rewriting, hiding, or blurring that earlier public record?

## Core principle

TWIS does not punish changed minds.

People can change position, learn new information, explain a new view, apologise, or openly say that their earlier position has changed.

The issue is not change. The issue is denial, rewriting, hiding, or blurring of the public record.

## Suggested files

evidence/public-record-timelines/public-record-timeline-0001.json
evidence/public-record-timelines/public-record-timeline-0001.md

## Required fields

- id
- topic
- person_or_body
- research_question
- earlier_record
- later_record
- denial_check
- human_review

## Earlier record fields

- claim_or_position
- plain_meaning
- source_id
- source_url
- source_title
- source_type
- date_recorded
- archive_url
- local_copy_path
- evidence_grade
- context_notes

## Later record fields

- claim_or_position
- plain_meaning
- source_id
- source_url
- source_title
- source_type
- date_recorded
- archive_url
- local_copy_path
- evidence_grade
- context_notes

## Denial check fields

- earlier_record_acknowledged
- change_explained
- earlier_record_denied
- earlier_record_rewritten
- earlier_record_hidden_or_removed
- earlier_record_blurred
- assessment_label
- assessment_notes
- what_is_proven
- what_is_interpretation
- what_must_not_be_overstated

## Assessment labels

- record_acknowledged_change
- record_explained_change
- record_unclear_shift
- record_denial
- record_rewrite
- record_erasure
- record_blurring
- record_conflict_needs_check
- different_context_not_conflict
- not_enough_evidence

## Wording rules

Prefer:

- The public record shows that this was said before.
- The later statement does not acknowledge that earlier record.
- The issue is not a change of mind. The issue is the denial of what was previously said.
- The evidence shows a shift, but not enough to claim denial.
- This appears to be a different context, not a conflict.

Avoid:

- They flip-flopped.
- They lied.
- They were caught contradicting themselves.
- This proves bad faith.
- This proves corruption.

## Human review rule

A denial, rewrite, erasure, or blurring assessment must not be used in TWIS output unless human_checked is true.

The system may flag a possible public-record issue, but a human must decide whether the label is fair.

## Quality rule

The system should protect fairness as well as accuracy.

It should expose denial of the public record without treating ordinary changed minds as wrongdoing.

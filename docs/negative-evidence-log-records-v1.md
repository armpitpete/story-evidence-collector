# Negative Evidence Log Records v1

## Purpose

Negative Evidence Log records show what was checked but did not support the claim.

This protects TWIS evidence work from cherry-picking.

A good evidence system should not only record helpful sources. It should also record sources that:

- did not support the claim
- partly supported the claim but with limits
- contradicted the claim
- showed a different context
- were too weak to rely on
- were checked but could not be used

## Core principle

The absence of supporting evidence is part of the proof trail.

A Negative Evidence Log does not automatically disprove a claim. It records that a source, search, or record was checked and did not provide the support expected.

## Suggested files

evidence/negative-evidence-logs/negative-evidence-log-0001.json
evidence/negative-evidence-logs/negative-evidence-log-0001.md

## Required fields

- id
- related_research_question
- related_claim_id
- checked_at
- checked_by
- source_checked
- expected_support
- actual_finding
- result_label
- impact_on_claim
- human_review

## Source checked fields

Each checked source should include:

- source_url
- source_title
- source_type
- source_date
- archive_url
- local_copy_path
- access_notes
- search_diary_id
- source_id_if_already_recorded

## Expected support fields

- expected_claim_support
- why_this_source_was_checked
- expected_source_role
- expected_evidence_grade

## Actual finding fields

- what_the_source_actually_says
- relevant_excerpt_summary
- relevant_timestamp_or_section
- support_found
- contradiction_found
- context_difference_found
- uncertainty_notes

## Result labels

- no_support_found
- partial_support_only
- contradicts_claim
- different_context
- weaker_than_needed
- derivative_not_primary
- inaccessible
- unclear_date
- unclear_author
- unclear_context
- later_corrected
- outdated_record
- not_relevant_after_checking
- needs_more_checking

## Impact on claim fields

- claim_strength_after_check
- claim_wording_change_needed
- claim_should_be_withdrawn
- claim_should_be_softened
- claim_needs_extra_source
- claim_can_stand_with_limits
- impact_notes

## Claim strength labels

- stronger
- unchanged
- weaker
- unsupported
- contradicted
- unclear
- needs_more_evidence

## Markdown brief section

Add a section like this to evidence briefs when useful:

Negative evidence checked

Research question:
Related claim:
Source checked:
Why it was checked:
Expected support:
Actual finding:
Result label:
Impact on claim:
Wording change needed:
Uncertainty notes:
Human checked:

## Wording rules

Prefer:

- This source was checked and did not support the claim.
- This source partly supports the claim, but only in a narrower context.
- This source appears to contradict the claim.
- The claim should be softened unless stronger evidence is found.
- The absence is limited to the source checked here.

Avoid:

- This proves the claim is false.
- Nothing supports the claim.
- The claim is definitely wrong.
- The source destroys the argument.
- The search proves absence.

## Human review rule

Negative Evidence Log records should be human-checked before they are used to weaken, withdraw, or publicly challenge a claim.

The tool can flag negative evidence, but a human must decide what it means for the final wording.

## Quality rule

A Negative Evidence Log should make the research process fairer.

It should help TWIS show that evidence was tested against sources that might weaken the article, not only sources that support it.

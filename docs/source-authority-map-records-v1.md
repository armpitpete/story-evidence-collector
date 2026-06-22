# Source Authority Map Records v1

## Purpose

Source Authority Map records show how strong a source is for a specific claim.

TWIS should not treat every source as equal.

A source can be useful for one kind of claim and weak for another. For example, a news article may be useful for showing what was reported, but an official document may be stronger for showing what a policy actually says.

## Core principle

Source authority is claim-specific.

The question is not only:

Is this source reliable?

The better question is:

What can this source safely prove?

## Suggested files

evidence/source-authority-maps/source-authority-map-0001.json
evidence/source-authority-maps/source-authority-map-0001.md

## Required fields

- id
- related_research_question
- related_claim_id
- source_id
- source_assessed
- claim_type
- source_role
- authority_rating
- limits
- recommended_use
- human_review

## Source assessed fields

Each source assessment should include:

- source_id
- source_url
- source_title
- source_type
- publisher_or_body
- author_or_speaker
- publication_date
- archive_url
- local_copy_path
- access_notes

## Claim types

Use claim types to define what the source is being used to prove.

- what_was_said
- what_was_written
- what_policy_says
- what_law_says
- what_a_body_did
- what_a_person_did
- what_changed_over_time
- what_was_reported
- what_was_promised
- what_was_denied
- what_was_removed
- what_data_shows
- what_people_experienced
- expert_interpretation
- background_context
- other

## Source roles

Use source roles to define how the source is being used.

- primary_record
- official_record
- original_statement
- direct_quote_source
- transcript
- archived_page
- legal_record
- parliamentary_record
- government_record
- regulator_record
- dataset
- expert_analysis
- news_report
- secondary_summary
- commentary
- social_post
- witness_account
- background_only
- pointer_to_better_source
- other

## Authority ratings

- very_strong
- strong
- moderate
- weak
- unsuitable
- unknown

## Rating guidance

Use very_strong when the source directly proves the claim and is close to the original record.

Use strong when the source is reliable and directly relevant, but not the absolute original record.

Use moderate when the source is useful but needs support from another source.

Use weak when the source may help with context but should not carry the claim alone.

Use unsuitable when the source should not be used for the claim.

Use unknown when the source cannot yet be assessed.

## Limits fields

Each source authority record should say what the source cannot safely prove.

- cannot_prove
- missing_context
- missing_dates
- missing_original_record
- possible_bias_or_interest
- needs_archived_copy
- needs_second_source
- needs_human_check
- limits_notes

## Recommended use fields

- safe_to_use_for
- not_safe_to_use_for
- should_be_cited_as
- should_be_supported_by
- wording_limits
- recommended_next_check

## Markdown brief section

Add a section like this to evidence briefs when useful:

Source authority

Source:
Claim type:
Source role:
Authority rating:
Safe to use for:
Not safe to use for:
Limits:
Needs second source:
Needs archive:
Needs human check:
Recommended wording:

## Wording rules

Prefer:

- This is a primary source for what was written.
- This is a secondary source and should not carry the claim alone.
- This source supports the context but does not prove the central claim.
- This source is useful as a pointer to a better original source.
- This source is strong for what was reported, but weaker for what actually happened.

Avoid:

- This source proves everything.
- This source is reliable, so the claim is proven.
- This article confirms the whole story.
- This source is useless.
- All sources agree.

## Human review rule

Source Authority Map records should be human-checked before a source is used to carry a serious claim.

The tool can suggest a rating, but a human must decide what the source can safely prove.

## Quality rule

A Source Authority Map should make evidence use more precise.

It should help TWIS cite sources for the right reason, avoid overclaiming, and separate primary records from summaries, commentary, and background material.

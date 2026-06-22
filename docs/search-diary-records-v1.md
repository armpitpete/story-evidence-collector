# Search Diary Records v1

## Purpose

Search Diary records show how TWIS evidence work was carried out.

The evidence system should not only preserve what was found. It should also preserve the search path.

A reviewer should be able to see:

- what question was being researched
- where searches were run
- what search terms were used
- what filters were used
- what sources were checked
- what sources were accepted
- what sources were rejected
- what was not found
- what remains uncertain

## Core principle

A professional evidence brief should be reproducible.

The Search Diary does not prove the final claim by itself. It shows the method used to find, check, reject, or fail to find evidence.

## Suggested files

evidence/search-diary/search-diary-0001.json
evidence/search-diary/search-diary-0001.md

## Required fields

- id
- research_question
- searched_at
- searched_by
- search_locations
- accepted_sources
- rejected_sources
- not_found_notes
- uncertainty_notes
- human_review

## Search location fields

Each search location should include:

- location_name
- location_type
- location_url
- query
- filters
- date_range
- result_pages_checked
- notes

## Location types

- search_engine
- official_site
- archive
- database
- website
- parliament_record
- court_record
- government_site
- regulator_site
- news_site
- video_platform
- social_platform
- other

## Accepted source fields

Each accepted source should include:

- source_id
- source_url
- source_title
- reason_accepted
- evidence_grade
- source_role
- notes

## Rejected source fields

Each rejected source should include:

- source_url
- source_title
- reason_rejected
- rejection_type
- notes

## Rejection types

- duplicate
- irrelevant
- weak_source
- derivative_only
- no_original_source
- inaccessible
- paywalled
- login_required
- unclear_date
- unclear_author
- insufficient_context
- not_public_source
- other

## Not-found notes

Use not-found notes when a reasonable expected source was checked but no usable result was found.

Not-found notes should say where the search was run and what terms were used.

They must not claim that the record never existed unless the checked source base is strong enough to support that.

## Markdown brief section

Add a section like this to evidence briefs:

Search diary

Research question:
Searched at:
Searched by:
Search locations:
Search terms used:
Filters used:
Date range:
Sources accepted:
Sources rejected:
Expected sources not found:
Uncertainty notes:
Human checked:

## Wording rules

Prefer:

- This source was found using the listed search terms.
- This source was rejected because it did not contain the original record.
- This search did not find a usable result in the checked source.
- The absence is limited to the sources and terms listed.
- Further searching may still be needed.

Avoid:

- No evidence exists.
- This proves nothing was ever said.
- The search is complete.
- Nothing else can exist.
- This source is useless.

## Human review rule

Search Diary records should be human-checked before being relied on in a professional TWIS report.

The tool can record searches, but a human must decide whether the search was adequate.

## Quality rule

A Search Diary should make the research process inspectable.

It should help TWIS show what was searched, what was found, what was rejected, what was not found, and what still needs checking.

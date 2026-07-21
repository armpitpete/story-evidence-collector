# Jeremy Corbyn current-Parliament spoken contributions — source note v1

## Result

The fixed official-source capture recorded:

- **202** authorised member-index debate rows;
- **306** unique individual spoken contribution segments;
- official `ContentItemExtId` identifiers matched exactly to full-debate `Items[].ExternalId` values for member ID `185`;
- accepted dates from **2024-07-17** through **2026-07-16**;
- capture timestamp **2026-07-21T09:59:35Z**;
- **0** unresolved records after the official site-relative permalink paths were normalised to the official Hansard host.

## Official request shapes

1. `GET https://members-api.parliament.uk/api/Members/185/ContributionSummary?page={page}`
2. `GET https://hansard-api.parliament.uk/search/contributions/Spoken.json` with `house=Commons`, the fixed date boundary, `memberId=185`, `skip`, `take=100` and `orderBy=SittingDateAsc`.
3. `GET https://hansard-api.parliament.uk/debates/memberdebatecontributions/185.json?debateSectionExtId={id}`
4. `GET https://hansard-api.parliament.uk/debates/debate/{id}.json`
5. `GET https://hansard-api.parliament.uk/search/parlisearchredirect.json?externalId={id}`

The capture made **725** polite sequential official requests: 11 Members API requests and 714 Hansard API requests. The raw request manifest checksum is `93b729e40a8bb6cadd87033f635d825436a2376f42754f46b1c57837dd04fef8`.

## Reconciliation

The Members API pages returned 220 rows before crossing the date boundary. Of 203 rows inside the authorised date period, 202 were Commons Chamber or Westminster Hall rows and one `Written Corrections` row was excluded. The 202 authorised rows resolved to 306 member segments. Each accepted segment required:

- an official `ContentItemExtId`;
- one exact full-debate `ExternalId` match;
- full-debate member ID `185`;
- matching debate ID, date and venue;
- non-empty official contribution text;
- one matching Hansard spoken-search result;
- one official permalink resolver response.

The resolver returned valid site-relative `/Commons/...` paths. The fixed packet prefixes only `https://hansard.parliament.uk`; it does not invent or rewrite the returned path.

## Counts

- Commons Chamber: 272
- Westminster Hall: 34
- Contribution endpoint type `Spoken`: 306
- Source status `unspecified`: 306

The debate payload exposed raw source value `2`, but not an explicit corrected, rolling or uncorrected label. The packet therefore preserves `2` and classifies the status as `unspecified` rather than inferring an enum mapping.

The member-index rows displayed 306 total contributions, while their displayed category counters summed to 271. Those approximate counters are retained as navigation evidence only and are not used to classify individual segments.

## Fixed-capture provenance

- Workflow run: `29820459172`
- Artifact ID: `8491239100`
- Artifact digest: `sha256:30a68c8feda571c5d9f7d54549d54163b01e720a3eb1b3b0058fc02010dfc1de`
- Diagnostic byte length: `1650782`
- Diagnostic SHA-256: `b2776c11a5a17d9605f56434ec5b13d77e75567a9bf01f851bf48e2f440e6a88`

## Exclusions and interpretation boundary

The capture excludes pre-4-July-2024 contributions, future records and later corrections, committee oral evidence, video/audio transcription, written statements, Early Day Motions, votes, tabled oral-question datasets and non-official sources.

No topic classification, summarisation of political meaning, policy-position inference, contradiction analysis, motive, influence, accuracy, legality, propriety or significance claim is made. The report remains `partial`, `not_ready`, human-review-required and unauthorised for public output.

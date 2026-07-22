# Jeremy Corbyn current-Parliament tabled oral questions source-interface proof v1

## Purpose

Determine whether official UK Parliament first-party interfaces can provide a complete, reproducible inventory of oral questions tabled by Jeremy Corbyn in the current Parliament. This is a source-interface proof only; it creates no canonical inventory and changes no Complete MP fixture data.

## Fixed context

- Exact starting `main`: `ddaa729a9deeaec7392a89e95e9dadaa5282bd67`
- Capture date: `2026-07-22`
- Commons member/MNIS ID: `185`
- Official API: `https://oralquestionsandmotions-api.parliament.uk`
- OpenAPI: `https://oralquestionsandmotions-api.parliament.uk/swagger/docs/v1`
- List operation: `GET /oralquestions/list`
- Probe run: `29951838611` at head `1cb7be10a70c140689087698adf342b2bec8a1e5`
- Fixed evidence SHA-256: `25cd378069d42a50c1a4c36d514f188767c4f2721cf95f6c8c5d2c3a48a40a5b`

## Conclusion

**A complete reproducible fixed inventory is possible for the oral-question records exposed by the official UK Parliament API at a fixed capture time.**

The complete capture method is:

1. query `parameters.askingMemberIds=185` without date, status, question-type or answering-body restrictions;
2. page until every record reported by `PagingInfo.Total` is received;
3. deduplicate by API `Id`;
4. select current-Parliament records locally with the inclusive boundary `2024-07-04 <= TabledWhen <= 2026-07-22`;
5. freeze the request URLs, paging evidence and raw response hashes.

At capture, the member query reported `Total = 12`, `GlobalTotal = 12` and returned all 12 records with `take=100`. Seven records met the current-Parliament tabled-date boundary and five were earlier. The raw member-query response SHA-256 was `f47822206b73bbac2fc557f6911750eda5165376905e3651323e59ccf02c94aa`.

This conclusion is limited to the official public API's exposed record set at the fixed capture date. It does not claim completeness for undisclosed internal records, later questions or later corrections.

## Confirmed interface behaviour

### Interface and record type

The UK Parliament developer directory identifies the Oral Questions API as the supported API for tabled House of Commons oral questions and motions. The OpenAPI specification defines `GET /oralquestions/list` as returning oral questions meeting its criteria.

This endpoint is distinct from written questions, answered oral contributions, supplementaries, speeches and Early Day Motions. Its returned fields include `Id`, `QuestionType`, `Status`, `Number`, `TabledWhen`, `AnsweringWhen`, `AnsweringBody`, `AskingMember` and `UIN`.

### Named-member semantics

The OpenAPI parameter `parameters.askingMemberIds` is the asking-member filter. Every returned member-query record contained `AskingMemberId = 185`, `AskingMember.MnisId = 185` and `AskingMember.Name = Jeremy Corbyn`.

A control query using member ID `999999` returned `Total = 0`, `GlobalTotal = 0` and no records, proving that the member filter is applied.

### Date and session boundary

The list operation declares answering-date filters but no tabled-date filter and no parliamentary-session filter. Supplying `tabledStartDate` and `tabledEndDate` produced a response byte-identical to the unbounded member query, so those unsupported parameters were ignored at capture.

The current-Parliament boundary must therefore be applied locally to `TabledWhen`. Answering-date filters are not a safe substitute because they could exclude unanswered or differently dated questions.

No session identifier is returned. The OpenAPI documentation says UINs reset at the start of each parliamentary session, so `UIN` is not a globally unique key. This proof uses API `Id` for identity.

### Pagination and ordering

The operation exposes `skip` and `take`; the documented maximum `take` is 100. Requests with `take=1` and `skip=0`, `1` and `2` returned IDs `122465`, `127241` and `271822`, each with `Total = 12`.

The observed full response is ascending by tabled date, but no ordering parameter is exposed. Completeness must therefore rely on paging totals and ID deduplication, not assumed ordering.

## Current-Parliament qualifying compact evidence

These seven rows are the minimum fixed evidence needed to prove the local boundary. They are **not a canonical Complete MP inventory**.

| API ID | UIN | Tabled | Answering | Question type value | Status value | Answering body |
|---|---:|---|---|---:|---:|---|
| `319088` | `900072` | 2024-07-18 | 2024-07-25 | `1` | `5` | Cabinet Office |
| `319553` | `900153` | 2024-07-24 | 2024-07-30 | `1` | `5` | Foreign, Commonwealth and Development Office |
| `332039` | `901261` | 2024-11-12 | 2024-11-18 | `1` | `5` | Ministry of Defence |
| `373735` | `904786` | 2025-06-18 | 2025-06-24 | `1` | `5` | Foreign, Commonwealth and Development Office |
| `374007` | `904875` | 2025-06-19 | 2025-06-25 | `1` | `5` | Prime Minister |
| `404663` | `907375` | 2026-01-14 | 2026-01-20 | `1` | `11` | Foreign, Commonwealth and Development Office |
| `411372` | `908076` | 2026-02-25 | 2026-03-03 | `1` | `11` | Foreign, Commonwealth and Development Office |

The live JSON serialized `QuestionType` and `Status` as numbers although the OpenAPI schema presents named enums. The numeric-to-name mapping is not asserted here.

## Confirmed limitations

- There is no supported tabled-date filter.
- There is no session filter or returned session field.
- Unsupported parameters may be ignored instead of rejected.
- UINs reset by session and are not globally unique.
- Numeric enum serialization is not self-describing.
- The proof covers the official public API's exposed records only.
- The fixed result does not include later records or later corrections.

## Explicit exclusions

This proof does not authorise a fixed canonical oral-question inventory, Complete MP fixture integration, fact or source creation, commitment/public-position classification, content interpretation, ideology or motive analysis, conduct comparison, delivery or fulfilment assessment, contradiction analysis, changes to existing written-question/spoken/EDM data, schema or generator changes, section completion, publication, deployment or public output.

## Fixed evidence

<!-- BEGIN SOURCE_INTERFACE_EVIDENCE_V1 -->
```json
{
  "answering_date_window": {
    "ids": [
      319088,
      319553,
      332039,
      373735,
      374007,
      404663,
      411372
    ],
    "paging": {
      "GlobalStatusCounts": [],
      "GlobalTotal": 7,
      "Skip": 0,
      "StatusCounts": [],
      "Take": 100,
      "Total": 7
    },
    "raw_sha256": "4a4616b5a7427706c58c2856fc036b5420aa12177e24e8252f883fc056f4652f",
    "url": "https://oralquestionsandmotions-api.parliament.uk/oralquestions/list?parameters.askingMemberIds=185&parameters.skip=0&parameters.take=100&parameters.answeringDateStart=2024-07-04&parameters.answeringDateEnd=2026-07-22"
  },
  "base_main": "ddaa729a9deeaec7392a89e95e9dadaa5282bd67",
  "capture_date": "2026-07-22",
  "member_query": {
    "paging": {
      "GlobalStatusCounts": [],
      "GlobalTotal": 12,
      "Skip": 0,
      "StatusCounts": [],
      "Take": 100,
      "Total": 12
    },
    "raw_sha256": "f47822206b73bbac2fc557f6911750eda5165376905e3651323e59ccf02c94aa",
    "records": [
      {
        "answering": "2020-04-29",
        "answering_body": "Department for International Development",
        "answering_body_id": 20,
        "asking_member_id": 185,
        "asking_member_mnis_id": 185,
        "asking_member_name": "Jeremy Corbyn",
        "id": 122465,
        "question_type": 1,
        "status": 11,
        "tabled": "2020-04-23",
        "uin": 902058
      },
      {
        "answering": "2020-05-20",
        "answering_body": "Prime Minister",
        "answering_body_id": 23,
        "asking_member_id": 185,
        "asking_member_mnis_id": 185,
        "asking_member_name": "Jeremy Corbyn",
        "id": 127241,
        "question_type": 1,
        "status": 5,
        "tabled": "2020-05-13",
        "uin": 902893
      },
      {
        "answering": "2023-01-31",
        "answering_body": "Foreign, Commonwealth and Development Office",
        "answering_body_id": 208,
        "asking_member_id": 185,
        "asking_member_mnis_id": 185,
        "asking_member_name": "Jeremy Corbyn",
        "id": 271822,
        "question_type": 2,
        "status": 5,
        "tabled": "2023-01-25",
        "uin": 903396
      },
      {
        "answering": "2023-01-31",
        "answering_body": "Foreign, Commonwealth and Development Office",
        "answering_body_id": 208,
        "asking_member_id": 185,
        "asking_member_mnis_id": 185,
        "asking_member_name": "Jeremy Corbyn",
        "id": 271823,
        "question_type": 1,
        "status": 5,
        "tabled": "2023-01-25",
        "uin": 903371
      },
      {
        "answering": "2023-06-13",
        "answering_body": "Foreign, Commonwealth and Development Office",
        "answering_body_id": 208,
        "asking_member_id": 185,
        "asking_member_mnis_id": 185,
        "asking_member_name": "Jeremy Corbyn",
        "id": 287272,
        "question_type": 1,
        "status": 5,
        "tabled": "2023-06-07",
        "uin": 905348
      },
      {
        "answering": "2024-07-25",
        "answering_body": "Cabinet Office",
        "answering_body_id": 53,
        "asking_member_id": 185,
        "asking_member_mnis_id": 185,
        "asking_member_name": "Jeremy Corbyn",
        "id": 319088,
        "question_type": 1,
        "status": 5,
        "tabled": "2024-07-18",
        "uin": 900072
      },
      {
        "answering": "2024-07-30",
        "answering_body": "Foreign, Commonwealth and Development Office",
        "answering_body_id": 208,
        "asking_member_id": 185,
        "asking_member_mnis_id": 185,
        "asking_member_name": "Jeremy Corbyn",
        "id": 319553,
        "question_type": 1,
        "status": 5,
        "tabled": "2024-07-24",
        "uin": 900153
      },
      {
        "answering": "2024-11-18",
        "answering_body": "Ministry of Defence",
        "answering_body_id": 11,
        "asking_member_id": 185,
        "asking_member_mnis_id": 185,
        "asking_member_name": "Jeremy Corbyn",
        "id": 332039,
        "question_type": 1,
        "status": 5,
        "tabled": "2024-11-12",
        "uin": 901261
      },
      {
        "answering": "2025-06-24",
        "answering_body": "Foreign, Commonwealth and Development Office",
        "answering_body_id": 208,
        "asking_member_id": 185,
        "asking_member_mnis_id": 185,
        "asking_member_name": "Jeremy Corbyn",
        "id": 373735,
        "question_type": 1,
        "status": 5,
        "tabled": "2025-06-18",
        "uin": 904786
      },
      {
        "answering": "2025-06-25",
        "answering_body": "Prime Minister",
        "answering_body_id": 23,
        "asking_member_id": 185,
        "asking_member_mnis_id": 185,
        "asking_member_name": "Jeremy Corbyn",
        "id": 374007,
        "question_type": 1,
        "status": 5,
        "tabled": "2025-06-19",
        "uin": 904875
      },
      {
        "answering": "2026-01-20",
        "answering_body": "Foreign, Commonwealth and Development Office",
        "answering_body_id": 208,
        "asking_member_id": 185,
        "asking_member_mnis_id": 185,
        "asking_member_name": "Jeremy Corbyn",
        "id": 404663,
        "question_type": 1,
        "status": 11,
        "tabled": "2026-01-14",
        "uin": 907375
      },
      {
        "answering": "2026-03-03",
        "answering_body": "Foreign, Commonwealth and Development Office",
        "answering_body_id": 208,
        "asking_member_id": 185,
        "asking_member_mnis_id": 185,
        "asking_member_name": "Jeremy Corbyn",
        "id": 411372,
        "question_type": 1,
        "status": 11,
        "tabled": "2026-02-25",
        "uin": 908076
      }
    ],
    "url": "https://oralquestionsandmotions-api.parliament.uk/oralquestions/list?parameters.askingMemberIds=185&parameters.skip=0&parameters.take=100"
  },
  "pagination": [
    {
      "id": 122465,
      "paging": {
        "GlobalStatusCounts": [],
        "GlobalTotal": 12,
        "Skip": 0,
        "StatusCounts": [],
        "Take": 1,
        "Total": 12
      },
      "raw_sha256": "7d3771cd0f2775a9ecb94b0dfa18110798ef9527b282d3772afb7208e1a511dc",
      "skip": 0
    },
    {
      "id": 127241,
      "paging": {
        "GlobalStatusCounts": [],
        "GlobalTotal": 12,
        "Skip": 1,
        "StatusCounts": [],
        "Take": 1,
        "Total": 12
      },
      "raw_sha256": "1bbc92f9de095b3cba0a07533f20b42a5873e359d0380ba575274022e23062aa",
      "skip": 1
    },
    {
      "id": 271822,
      "paging": {
        "GlobalStatusCounts": [],
        "GlobalTotal": 12,
        "Skip": 2,
        "StatusCounts": [],
        "Take": 1,
        "Total": 12
      },
      "raw_sha256": "ae481a215814ff70d020a87ca68249ace3188e1f860a840610bf811a54e34ead",
      "skip": 2
    }
  ],
  "probe": {
    "artifact_digest": "sha256:ca8cb8c5eddee9d364cde740d5c2be686fceeef3a79f549e18dc7d41d83f2ea3",
    "artifact_id": 8542430328,
    "head": "1cb7be10a70c140689087698adf342b2bec8a1e5",
    "run_id": 29951838611
  },
  "spec": {
    "description": "A list of oral questions meeting the specified criteria.",
    "parameters": [
      "parameters.answeringDateStart",
      "parameters.answeringDateEnd",
      "parameters.questionType",
      "parameters.oralQuestionTimeId",
      "parameters.statuses",
      "parameters.askingMemberIds",
      "parameters.uINs",
      "parameters.answeringBodyIds",
      "parameters.skip",
      "parameters.take"
    ],
    "sha256": "bde894ce32092579b52cc419f36a5ee65a45260664fa5f89d9f78db01d65df6f",
    "statuses": [
      "Submitted",
      "Carded",
      "Unsaved",
      "ReadyForShuffle",
      "ToBeAsked",
      "ShuffleUnsuccessful",
      "Withdrawn",
      "Unstarred",
      "Draft",
      "ForReview",
      "Unasked",
      "Transferred"
    ],
    "summary": "Returns a list of oral questions",
    "url": "https://oralquestionsandmotions-api.parliament.uk/swagger/docs/v1"
  },
  "unsupported_tabled_parameters": {
    "equals_base": true,
    "paging": {
      "GlobalStatusCounts": [],
      "GlobalTotal": 12,
      "Skip": 0,
      "StatusCounts": [],
      "Take": 100,
      "Total": 12
    },
    "sha256": "f47822206b73bbac2fc557f6911750eda5165376905e3651323e59ccf02c94aa",
    "url": "https://oralquestionsandmotions-api.parliament.uk/oralquestions/list?parameters.askingMemberIds=185&parameters.skip=0&parameters.take=100&parameters.tabledStartDate=2024-07-04&parameters.tabledEndDate=2026-07-22"
  },
  "wrong_member": {
    "paging": {
      "GlobalStatusCounts": [],
      "GlobalTotal": 0,
      "Skip": 0,
      "StatusCounts": [],
      "Take": 100,
      "Total": 0
    },
    "raw_sha256": "25768e961931ac09314cd527d46efb316e4aec23613f96379d8e9327e3b2e515",
    "record_count": 0,
    "url": "https://oralquestionsandmotions-api.parliament.uk/oralquestions/list?parameters.askingMemberIds=999999&parameters.skip=0&parameters.take=100"
  }
}
```
<!-- END SOURCE_INTERFACE_EVIDENCE_V1 -->

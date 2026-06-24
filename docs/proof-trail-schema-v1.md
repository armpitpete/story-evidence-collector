# Proof Trail Schema v1

## Purpose

`story-evidence-collector` is a bounded public-source evidence tool for TWIS.

It does not only find information. It preserves the proof trail.

The tool collects public sources, extracts claims, records provenance, stores archive links or local evidence copies where appropriate, grades evidence strength, and produces human-checkable briefs.

## Core rule

> The proof lives in files.  
> The database helps find it later.

The first version should save clear JSON and Markdown files. A SQLite index can be added later when searching across many records becomes necessary.

---

## 1. Output folder structure

```text
evidence/
├─ sources/
│  └─ source-0001.json
├─ claims/
│  └─ claim-0001.json
├─ evidence-items/
│  └─ evidence-item-0001.json
├─ briefs/
│  └─ brief-0001.md
├─ archives/
│  └─ README.md
└─ transcripts/
   └─ README.md
```

---

## 2. Source record

A source record stores where information came from.

File path:

```text
evidence/sources/source-0001.json
```

Schema:

```json
{
  "id": "source-0001",
  "title": "",
  "url": "",
  "publisher": "",
  "source_type": "official_record",
  "publication_date": "",
  "collected_at": "",
  "archive_url": "",
  "local_copy_path": "",
  "author_or_speaker": "",
  "body_or_organisation": "",
  "reliability_grade": "A",
  "notes": ""
}
```

Allowed `source_type` values:

```text
official_record
government_page
parliament_record
court_document
manifesto
speech
interview
news_article
press_release
social_post
video
audio
transcript
screenshot
other
```

---

## 3. Claim record

A claim record stores what was said or asserted.

File path:

```text
evidence/claims/claim-0001.json
```

Schema:

```json
{
  "id": "claim-0001",
  "source_id": "source-0001",
  "speaker": "",
  "body_or_organisation": "",
  "claim_text": "",
  "plain_meaning": "",
  "topic": "",
  "position": "",
  "date_claimed": "",
  "confidence": "medium",
  "human_checked": false,
  "notes": ""
}
```

Allowed `confidence` values:

```text
low
medium
high
```

Rule:

> The system may suggest a claim, but a human must approve it before publication use.

---

## 4. Evidence item record

An evidence item stores the specific proof fragment supporting a claim.

File path:

```text
evidence/evidence-items/evidence-item-0001.json
```

Schema:

```json
{
  "id": "evidence-item-0001",
  "claim_id": "claim-0001",
  "source_id": "source-0001",
  "excerpt": "",
  "page_number": "",
  "timestamp_start": "",
  "timestamp_end": "",
  "transcript_path": "",
  "archive_url": "",
  "local_copy_path": "",
  "evidence_grade": "A",
  "human_checked": false,
  "context_notes": "",
  "risk_notes": ""
}
```

Rule:

> Screenshots, clipped videos, and copied quotes are weak unless traced back to a stronger source.

---

## 5. Evidence grades

Use this grading ladder.

| Grade | Evidence type | Strength |
|---|---|---|
| A | Hansard, official records, government publications, court documents | Strong |
| B | Full speech/interview transcript with timestamped video/audio | Good |
| C | Reputable news article with direct quote | Useful, needs checking |
| D | Verified social post, campaign page, archived statement | Fragile |
| E | Screenshot, clipped video, meme, montage | Weak unless traced back |

Rule:

> Grade E evidence must not be used alone for serious TWIS claims.

---

## 6. Evidence brief

An evidence brief turns records into a human-readable TWIS support note.

File path:

```text
evidence/briefs/brief-0001.md
```

Template:

```md
# Evidence Brief

## Topic

## Summary

## Claim found

**Speaker/body:**  
**Date:**  
**Exact wording:**  
**Plain meaning:**  

## Source chain

**Original source:**  
**Archive copy:**  
**Local copy:**  
**Transcript:**  
**Video/audio timestamp:**  
**Collected at:**  

## Evidence grade

A / B / C / D / E

## What is proven

## What is interpretation

## What needs checking

## What must not be overstated

## Possible contradiction or tension

## Human review status

- [ ] Source checked
- [ ] Archive checked
- [ ] Quote checked
- [ ] Context checked
- [ ] Risk wording checked
- [ ] Approved for TWIS use
```

---

## 7. Contradiction matching labels

The system must not simply say “contradiction”.

Use one of these labels:

```text
direct_contradiction
policy_reversal
promise_versus_action
tone_shift
changed_justification
selective_wording
different_context_not_contradiction
needs_human_check
```

Rule:

> The system finds evidence tension. A human decides whether it is a contradiction.

---

## 8. Safety and quality rules

TWIS should use the highest editorial and evidence standards.

The collector must avoid:

- uncontrolled spidering
- anti-bot behaviour
- automatic accusations of lying
- unsupported claims
- screenshots as final proof
- clipped evidence without context
- vague claims without dates or sources
- publishing evidence that cannot survive hostile checking

Preferred wording:

```text
This appears inconsistent.
The public record shows a shift.
The later claim does not sit easily with the earlier claim.
The evidence supports X, but does not prove Y.
```

Avoid:

```text
They lied.
This proves corruption.
They were caught.
```

---

## 9. Minimum viable test

A successful v1 test should do this:

```text
Input:
- one public URL or pasted public source text

Output:
- one source JSON file
- one claim JSON file
- one evidence item JSON file
- one Markdown evidence brief
```

Good enough result:

> A human can open the files and understand what was found, where it came from, what it proves, and what still needs checking.

---

## 10. Later database rule

SQLite can be added after the file format is stable.

The database should index:

```text
sources
claims
evidence_items
briefs
contradiction_matches
```

But the database must not become the only proof store.

Rule:

> The database is an index, not the archive.

---

## 11. Proof Trail validation checklist

Use this checklist before a proof trail is treated as ready for serious TWIS use.

A usable proof trail should preserve:

- [ ] source title
- [ ] source URL
- [ ] publisher or source body
- [ ] author, speaker, or organisation where known
- [ ] publication date or date claimed
- [ ] collection timestamp
- [ ] archive URL where available
- [ ] local copy path where appropriate
- [ ] source record ID
- [ ] claim record ID
- [ ] evidence item record ID
- [ ] exact excerpt or transcript reference
- [ ] page number or audio/video timestamp where relevant
- [ ] evidence grade
- [ ] context notes
- [ ] risk notes
- [ ] human review status

A proof trail is not ready if it only contains:

- a screenshot without a source chain
- a clipped video without a full context link
- a quote without a source record
- a claim without a date
- an archive link without the original source
- an evidence item that does not connect back to a claim

Before publication use, the brief must clearly separate:

- what is proven
- what is interpretation
- what still needs checking
- what must not be overstated

Rule:

> A proof trail is useful only when another person can follow it without trusting the collector.

---

## 12. Example proof-trail fixture shape

A minimal proof-trail fixture should show how one source, one claim, one evidence item, and one brief connect by ID.

The example does not need to prove a real political claim. It only needs to demonstrate the file shape and proof chain.

Minimum example files:

- evidence/sources/source-0001.json
- evidence/claims/claim-0001.json
- evidence/evidence-items/evidence-item-0001.json
- evidence/briefs/brief-0001.md
- evidence/archives/source-0001.html

Minimum ID links:

- claim-0001.json must contain source_id: source-0001.
- evidence-item-0001.json must contain claim_id: claim-0001.
- evidence-item-0001.json must contain source_id: source-0001.
- brief-0001.md must name the source record, claim record, and evidence item record.

Minimum source fields:

- id
- title
- url
- publisher
- source_type
- publication_date
- collected_at
- archive_url or local_copy_path

Minimum claim fields:

- id
- source_id
- claim_text
- plain_meaning
- date_claimed
- confidence
- human_checked

Minimum evidence item fields:

- id
- claim_id
- source_id
- excerpt
- archive_url or local_copy_path
- evidence_grade
- context_notes
- risk_notes
- human_checked

Fixture rule:

> The example fixture should prove that the proof chain can be followed, not that the claim is politically important.

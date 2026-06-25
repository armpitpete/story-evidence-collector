# Power Profile System Model v0.1

## Status

Locked direction.

This document records the agreed architecture for using Story Evidence Collector to support TWIS Power Profiles and related evidence-led political research.

## Core decision

Story Evidence Collector should use one shared Evidence Pack system with a small number of pack templates underneath it.

The user-facing intake must remain simple.

The internal structure can be strict.

## User-facing intake

The person using the system should not have to choose schemas, templates, filenames, or validation rules manually.

The front door should ask only:

1. What are you researching?
2. What sources or links do you already have?
3. What output do you want?
4. How sensitive is this research?

Example intake:

```text
Subject: Andy Burnham
Research question: Does his public-control image match the interests around his political operation?
Known sources: Guardian article, Parliament profile, Flint Global profile
Wanted output: article, evidence table, connection chart
Sensitivity: sensitive
```

The system then chooses the correct internal pack type.

## First pack type

Start with one template only:

```text
power_profile
```

Do not build multiple templates yet.

A Power Profile is used for politicians, MPs, mayors, ministers, party leaders, and other public political figures.

## Power Profile purpose

A Power Profile asks:

> What does this politician say they stand for, and what interests sit close to their power?

It should analyse public power networks, not private lives.

## Power Profile outputs

Each Power Profile should support:

- article
- evidence table
- source links
- visual connection chart
- what is proven / not proven
- careful TWIS judgement

## Required Power Profile files

A Power Profile Evidence Pack should use:

```text
manifest.json
sources.jsonl
claims.jsonl
people.jsonl
organisations.jsonl
relationships.jsonl
chart_nodes.jsonl
chart_edges.jsonl
notes.md
```

Optional later files may include:

```text
declared_interests.jsonl
appointments.jsonl
risk_register.jsonl
timeline.jsonl
```

## Visual chart rule

Every public chart edge must have a source link.

No low-confidence relationship may appear on the public chart.

A chart should show documented public relationships such as:

- appointed
- advised by
- funded by
- worked for
- former role
- board member
- donor
- campaign support
- public ally
- shared organisation
- client relationship
- policy interest
- lobbying link
- public appointment

Avoid vague or loaded wording.

Do not use:

- puppet
- controlled by
- bought by
- crony
- corrupt
- linked to, unless the link is clearly defined elsewhere

## Evidence rule

AI can help guide research.

AI cannot make evidence true.

AI may:

- suggest search terms
- identify likely source categories
- extract candidate claims
- suggest possible relationships
- flag missing evidence
- mark confidence
- warn about risky wording
- organise sources into pack files

AI must not:

- invent connections
- treat weak associations as evidence
- make unsourced links publishable
- create gossip profiles
- upgrade low-confidence material into public chart material
- imply corruption without proof

Core rule:

> AI can guide the search and organise the evidence. It cannot make an unsourced connection publishable.

## Search-point AI model

Use a bounded two-stage AI process.

### Stage 1 — Research planner

Input:

```text
subject
research question
known links
wanted output
sensitivity
```

Output:

```text
research-plan.md
source-targets.jsonl
search-queries.jsonl
exclusion-rules.md
```

### Stage 2 — Evidence extractor

Input:

```text
approved sources
```

Output:

```text
claims.jsonl
people.jsonl
organisations.jsonl
relationships.jsonl
chart_nodes.jsonl
chart_edges.jsonl
risk notes
```

The two stages must stay separate.

The planner suggests what to look for.

The extractor organises what has been found.

Neither stage makes unsourced claims publishable.

## Political safety rules

Power Profiles must exclude:

- private family material
- gossip
- rumours
- unevidenced friendships
- psychological claims
- private relationships
- guilt-by-association claims

Power Profiles may include:

- public roles
- voting records
- declared interests
- donors
- advisers
- appointments
- public allies
- public employers
- consultancies
- think tanks
- lobbying links
- companies
- unions
- public bodies
- policy conflicts

## Safe wording

Allowed:

```text
This raises a public-interest question.
```

Allowed:

```text
This creates a transparency problem.
```

Allowed:

```text
This relationship deserves scrutiny.
```

Avoid unless legally proven:

```text
This proves corruption.
```

Avoid:

```text
They are bought.
```

Avoid:

```text
They are controlled by X.
```

## Validator direction

For `pack_type: "power_profile"`, the validator should eventually check:

- required files exist
- every claim has a source
- every relationship has a source
- every chart edge has a source
- every public chart edge has confidence `high` or `medium`
- no low-confidence edge is marked for public chart use
- every risky claim has a risk note
- every interpretation is marked as interpretation
- every public chart edge has plain wording allowed
- every public chart edge has wording to avoid

## First implementation step

Do not build a crawler first.

Do not build all templates first.

The first implementation should be:

```text
Add simple new-pack intake for Power Profile packs
```

Minimum behaviour:

- ask for subject
- ask for research question
- ask for known source links
- ask for wanted output
- ask for sensitivity
- set `pack_type` to `power_profile`
- create starter files
- create `notes.md`
- run validation

## Locked principle

Simple at the front.

Structured underneath.

Human-checkable proof trail throughout.

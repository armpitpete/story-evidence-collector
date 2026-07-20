# Complete MP Portfolio View v1

## Status

Bounded local-interface vertical slice for Complete MP Report v1.

This view proves that one validated Complete MP Report can be displayed inside the existing Streamlit application. It does not complete the MP research, change evidence, approve claims or authorise publication.

## Open the view

From the repository folder:

```powershell
py -m streamlit run .\twis_source_engine_ui_v24.py
```

In the sidebar, choose:

```text
MP Portfolio
```

The existing `Simple` and `Advanced` source-check views remain available and unchanged.

## Current proof input

The view reads the committed fixture:

```text
fixtures/complete-mp-reports/jeremy-corbyn-fixture-v1.json
```

Before anything is displayed, the fixture is checked by the canonical Complete MP Report v1 validator in:

```text
scripts/generate_complete_mp_report.py
```

The fixture remains deliberately:

- `fixture_unverified`;
- `not_ready`;
- incomplete across most research lanes;
- subject to human review;
- unauthorised for public output.

## What the view shows

The portfolio page shows:

- report and MP identity;
- publication and human-review state;
- declared scope;
- all 13 canonical report sections in canonical order;
- the explicit coverage status and summary for every section;
- section-linked facts, claims, interpretations, relationships and coverage gaps;
- resolved source titles, locations, authority levels and limitations;
- the complete source register;
- the five canonical output filenames.

Empty and incomplete sections are not hidden. A section remains visible when it is `partial`, `not_available`, `not_researched` or `human_review_required`.

## Disposable generator proof

The page includes a button labelled:

```text
Run disposable generator proof
```

This button:

1. validates the fixture again;
2. creates an operating-system temporary directory outside the repository;
3. runs the canonical Complete MP Report generator;
4. records each output filename, byte size and SHA-256 hash;
5. deletes the files and temporary directory before returning the result.

It does not write generated portfolio files into the repository.

The five expected outputs are:

```text
corbyn-jeremy-full-profile.json
corbyn-jeremy-full-profile.md
corbyn-jeremy-source-register.md
corbyn-jeremy-coverage-report.md
corbyn-jeremy-human-review.md
```

The displayed table is sorted by filename, so the coverage report may appear first in the table.

## Safety boundary

The view is read-only. It cannot:

- browse or research the web;
- access the private server;
- read or write SQLite;
- edit facts, claims, sources or gaps;
- create review decisions;
- resolve contradictions;
- infer political meaning;
- mark the report publishable;
- authorise public output;
- commit or upload generated files.

Invalid structure, unresolved references or generator validation errors stop the portfolio view rather than displaying a partial result.

## Regression command

Run:

```bash
python scripts/test_complete_mp_portfolio_view.py
```

The regression proves:

- the fixture validates;
- exactly 13 canonical sections are shown in canonical order;
- source references resolve;
- incomplete-state wording remains visible;
- the canonical five-file output set is unchanged;
- repeated disposable generation produces identical filenames, sizes and hashes;
- temporary output directories are removed;
- the Streamlit application still exposes `Simple`, `MP Portfolio` and `Advanced` routes.

## Next product boundary

This vertical slice proves the software path:

```text
validated structured MP records
        ↓
read-only portfolio display
        ↓
disposable canonical report generation
```

It does not start the next lane. Real MP research, evidence import, human review controls and persistent private portfolio storage require separately authorised work.

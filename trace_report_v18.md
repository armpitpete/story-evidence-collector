# Story Evidence Collector Trace Report v1.8

Generated: `2026-06-08T05:32:05.284464+00:00`

## Plain-English summary

This report explains what happened to each URL already present in the saved pipeline files. It does not fetch any pages and it does not make any network requests.

The report now separates final status from history. Final status answers: `Where did this URL end up?` History answers: `What happened to it along the way?`

A URL can be fetched earlier and then skipped later as `already_known`. That is not a contradiction. It means the collector avoided fetching the same URL again.

`Seed URLs seen` means URLs that appeared in the original seed file. A seed URL can later become fetched, so this count is separate from final status.

## Summary counts

| Metric | Count |
| --- | --- |
| Unique URLs traced | 51 |
| Fetched URLs final status | 5 |
| Skipped URLs final status | 46 |
| Candidate URLs final status | 0 |
| Pending URLs final status | 0 |
| Seed URLs seen | 1 |
| Fetched earlier, later skipped as already known | 3 |


## Status wording

| Wording | Meaning |
| --- | --- |
| Final status | The best plain-English status after all saved pipeline files are read. |
| History | The stages and events seen before the final status was decided. |
| Seed URLs seen | URLs from seed_urls.json, even if they later became fetched URLs. |
| Fetched earlier, later skipped as already known | The URL was fetched once, then skipped later to avoid duplication. |


## Pipeline stage summary

| Stage | File | Loaded | Items | Status |
| --- | --- | --- | --- | --- |
| v1.1 seed URLs | seed_urls.json | True | 1 | loaded |
| v1.3 source records | sources_raw_v13.json | True | 1 | loaded |
| v1.3 pending link queue | link_queue_v13.json | True | 49 | loaded |
| v1.4 filtered link queue | link_queue_filtered_v14.json | True | 49 | loaded |
| v1.5 fetched candidate sources | candidate_sources_raw_v15.json | True | 3 | loaded |
| v1.5 candidate fetch report | candidate_fetch_report_v15.json | True | 1 | loaded |
| v1.6 followed source records | followed_sources_raw_v16.json | True | 0 | loaded |
| v1.6 followed fetch report | followed_fetch_report_v16.json | True | 1 | loaded |


## Final URL status

| URL | Final status | Plain-English note |
| --- | --- | --- |
| http://quotes.toscrape.com/author/Albert-Einstein/ | fetched | Fetched successfully. |
| http://quotes.toscrape.com/author/J-K-Rowling/ | fetched | Fetched successfully. |
| https://quotes.toscrape.com/ | fetched | Fetched earlier. Seen again later and skipped as already known. |
| https://quotes.toscrape.com/author/Albert-Einstein | fetched | Fetched earlier. Seen again later and skipped as already known. |
| https://quotes.toscrape.com/author/Andre-Gide | skipped | Skipped. Reason: already_known. |
| https://quotes.toscrape.com/author/Eleanor-Roosevelt | skipped | Skipped. Reason: already_known. |
| https://quotes.toscrape.com/author/J-K-Rowling | fetched | Fetched earlier. Seen again later and skipped as already known. |
| https://quotes.toscrape.com/author/Jane-Austen | skipped | Skipped. Reason: already_known. |
| https://quotes.toscrape.com/author/Marilyn-Monroe | skipped | Skipped. Reason: already_known. |
| https://quotes.toscrape.com/author/Steve-Martin | skipped | Skipped. Reason: already_known. |
| https://quotes.toscrape.com/author/Thomas-A-Edison | skipped | Skipped. Reason: already_known. |
| https://quotes.toscrape.com/login | skipped | Skipped. Reason: login_account_or_admin_link. |
| https://quotes.toscrape.com/page/2/ | skipped | Skipped. Reason: already_known. |
| https://quotes.toscrape.com/tag/abilities/page/1/ | skipped | Skipped. Reason: navigation_or_tag_link. |
| https://quotes.toscrape.com/tag/adulthood/page/1/ | skipped | Skipped. Reason: navigation_or_tag_link. |
| https://quotes.toscrape.com/tag/aliteracy/page/1/ | skipped | Skipped. Reason: navigation_or_tag_link. |
| https://quotes.toscrape.com/tag/be-yourself/page/1/ | skipped | Skipped. Reason: navigation_or_tag_link. |
| https://quotes.toscrape.com/tag/books/ | skipped | Skipped. Reason: navigation_or_tag_link. |
| https://quotes.toscrape.com/tag/books/page/1/ | skipped | Skipped. Reason: navigation_or_tag_link. |
| https://quotes.toscrape.com/tag/change/page/1/ | skipped | Skipped. Reason: navigation_or_tag_link. |
| https://quotes.toscrape.com/tag/choices/page/1/ | skipped | Skipped. Reason: navigation_or_tag_link. |
| https://quotes.toscrape.com/tag/classic/page/1/ | skipped | Skipped. Reason: navigation_or_tag_link. |
| https://quotes.toscrape.com/tag/deep-thoughts/page/1/ | skipped | Skipped. Reason: navigation_or_tag_link. |
| https://quotes.toscrape.com/tag/edison/page/1/ | skipped | Skipped. Reason: navigation_or_tag_link. |
| https://quotes.toscrape.com/tag/failure/page/1/ | skipped | Skipped. Reason: navigation_or_tag_link. |
| https://quotes.toscrape.com/tag/friends/ | skipped | Skipped. Reason: navigation_or_tag_link. |
| https://quotes.toscrape.com/tag/friendship/ | skipped | Skipped. Reason: navigation_or_tag_link. |
| https://quotes.toscrape.com/tag/humor/ | skipped | Skipped. Reason: navigation_or_tag_link. |
| https://quotes.toscrape.com/tag/humor/page/1/ | skipped | Skipped. Reason: navigation_or_tag_link. |
| https://quotes.toscrape.com/tag/inspirational/ | skipped | Skipped. Reason: navigation_or_tag_link. |
| https://quotes.toscrape.com/tag/inspirational/page/1/ | skipped | Skipped. Reason: navigation_or_tag_link. |
| https://quotes.toscrape.com/tag/life/ | skipped | Skipped. Reason: navigation_or_tag_link. |
| https://quotes.toscrape.com/tag/life/page/1/ | skipped | Skipped. Reason: navigation_or_tag_link. |
| https://quotes.toscrape.com/tag/live/page/1/ | skipped | Skipped. Reason: navigation_or_tag_link. |
| https://quotes.toscrape.com/tag/love/ | skipped | Skipped. Reason: navigation_or_tag_link. |
| https://quotes.toscrape.com/tag/love/page/1/ | skipped | Skipped. Reason: navigation_or_tag_link. |
| https://quotes.toscrape.com/tag/miracle/page/1/ | skipped | Skipped. Reason: navigation_or_tag_link. |
| https://quotes.toscrape.com/tag/miracles/page/1/ | skipped | Skipped. Reason: navigation_or_tag_link. |
| https://quotes.toscrape.com/tag/misattributed-eleanor-roosevelt/page/1/ | skipped | Skipped. Reason: navigation_or_tag_link. |
| https://quotes.toscrape.com/tag/obvious/page/1/ | skipped | Skipped. Reason: navigation_or_tag_link. |
| https://quotes.toscrape.com/tag/paraphrased/page/1/ | skipped | Skipped. Reason: navigation_or_tag_link. |
| https://quotes.toscrape.com/tag/reading/ | skipped | Skipped. Reason: navigation_or_tag_link. |
| https://quotes.toscrape.com/tag/simile/ | skipped | Skipped. Reason: navigation_or_tag_link. |
| https://quotes.toscrape.com/tag/simile/page/1/ | skipped | Skipped. Reason: navigation_or_tag_link. |
| https://quotes.toscrape.com/tag/success/page/1/ | skipped | Skipped. Reason: navigation_or_tag_link. |
| https://quotes.toscrape.com/tag/thinking/page/1/ | skipped | Skipped. Reason: navigation_or_tag_link. |
| https://quotes.toscrape.com/tag/truth/ | skipped | Skipped. Reason: navigation_or_tag_link. |
| https://quotes.toscrape.com/tag/value/page/1/ | skipped | Skipped. Reason: navigation_or_tag_link. |
| https://quotes.toscrape.com/tag/world/page/1/ | skipped | Skipped. Reason: navigation_or_tag_link. |
| https://www.goodreads.com/quotes | skipped | Skipped. Reason: external_domain. |
| https://www.zyte.com/ | skipped | Skipped. Reason: external_domain. |


## Fetched earlier, skipped later as already known

| URL | Final status | History | Plain-English note |
| --- | --- | --- | --- |
| https://quotes.toscrape.com/ | fetched | seed URL → queued → kept as candidate → fetched → later skipped as already known | Fetched earlier. Seen again later and skipped as already known. |
| https://quotes.toscrape.com/author/Albert-Einstein | fetched | queued → kept as candidate → fetched → later skipped as already known | Fetched earlier. Seen again later and skipped as already known. |
| https://quotes.toscrape.com/author/J-K-Rowling | fetched | queued → kept as candidate → fetched → later skipped as already known | Fetched earlier. Seen again later and skipped as already known. |


## Fetched source table

| URL | Final URL | Title | Robots | Plain-English note |
| --- | --- | --- | --- | --- |
| http://quotes.toscrape.com/author/Albert-Einstein/ | http://quotes.toscrape.com/author/Albert-Einstein/ | Quotes to Scrape | not_found_treated_as_allowed | Fetched successfully. |
| http://quotes.toscrape.com/author/J-K-Rowling/ | http://quotes.toscrape.com/author/J-K-Rowling/ | Quotes to Scrape | not_found_treated_as_allowed | Fetched successfully. |
| https://quotes.toscrape.com/ | https://quotes.toscrape.com/ | Quotes to Scrape | not_found_treated_as_allowed | Fetched earlier. Seen again later and skipped as already known. |
| https://quotes.toscrape.com/author/Albert-Einstein | http://quotes.toscrape.com/author/Albert-Einstein/ | Quotes to Scrape | not_found_treated_as_allowed | Fetched earlier. Seen again later and skipped as already known. |
| https://quotes.toscrape.com/author/J-K-Rowling | http://quotes.toscrape.com/author/J-K-Rowling/ | Quotes to Scrape | not_found_treated_as_allowed | Fetched earlier. Seen again later and skipped as already known. |


## Skipped URL table

| URL | Final status | Skip reason | Plain-English note |
| --- | --- | --- | --- |
| https://quotes.toscrape.com/ | fetched | already_known | Fetched earlier. Seen again later and skipped as already known. |
| https://quotes.toscrape.com/author/Albert-Einstein | fetched | already_known | Fetched earlier. Seen again later and skipped as already known. |
| https://quotes.toscrape.com/author/Andre-Gide | skipped | already_known | Skipped. Reason: already_known. |
| https://quotes.toscrape.com/author/Eleanor-Roosevelt | skipped | already_known | Skipped. Reason: already_known. |
| https://quotes.toscrape.com/author/J-K-Rowling | fetched | already_known | Fetched earlier. Seen again later and skipped as already known. |
| https://quotes.toscrape.com/author/Jane-Austen | skipped | already_known | Skipped. Reason: already_known. |
| https://quotes.toscrape.com/author/Marilyn-Monroe | skipped | already_known | Skipped. Reason: already_known. |
| https://quotes.toscrape.com/author/Steve-Martin | skipped | already_known | Skipped. Reason: already_known. |
| https://quotes.toscrape.com/author/Thomas-A-Edison | skipped | already_known | Skipped. Reason: already_known. |
| https://quotes.toscrape.com/login | skipped | login_account_or_admin_link | Skipped. Reason: login_account_or_admin_link. |
| https://quotes.toscrape.com/page/2/ | skipped | already_known | Skipped. Reason: already_known. |
| https://quotes.toscrape.com/tag/abilities/page/1/ | skipped | navigation_or_tag_link | Skipped. Reason: navigation_or_tag_link. |
| https://quotes.toscrape.com/tag/adulthood/page/1/ | skipped | navigation_or_tag_link | Skipped. Reason: navigation_or_tag_link. |
| https://quotes.toscrape.com/tag/aliteracy/page/1/ | skipped | navigation_or_tag_link | Skipped. Reason: navigation_or_tag_link. |
| https://quotes.toscrape.com/tag/be-yourself/page/1/ | skipped | navigation_or_tag_link | Skipped. Reason: navigation_or_tag_link. |
| https://quotes.toscrape.com/tag/books/ | skipped | navigation_or_tag_link | Skipped. Reason: navigation_or_tag_link. |
| https://quotes.toscrape.com/tag/books/page/1/ | skipped | navigation_or_tag_link | Skipped. Reason: navigation_or_tag_link. |
| https://quotes.toscrape.com/tag/change/page/1/ | skipped | navigation_or_tag_link | Skipped. Reason: navigation_or_tag_link. |
| https://quotes.toscrape.com/tag/choices/page/1/ | skipped | navigation_or_tag_link | Skipped. Reason: navigation_or_tag_link. |
| https://quotes.toscrape.com/tag/classic/page/1/ | skipped | navigation_or_tag_link | Skipped. Reason: navigation_or_tag_link. |
| https://quotes.toscrape.com/tag/deep-thoughts/page/1/ | skipped | navigation_or_tag_link | Skipped. Reason: navigation_or_tag_link. |
| https://quotes.toscrape.com/tag/edison/page/1/ | skipped | navigation_or_tag_link | Skipped. Reason: navigation_or_tag_link. |
| https://quotes.toscrape.com/tag/failure/page/1/ | skipped | navigation_or_tag_link | Skipped. Reason: navigation_or_tag_link. |
| https://quotes.toscrape.com/tag/friends/ | skipped | navigation_or_tag_link | Skipped. Reason: navigation_or_tag_link. |
| https://quotes.toscrape.com/tag/friendship/ | skipped | navigation_or_tag_link | Skipped. Reason: navigation_or_tag_link. |
| https://quotes.toscrape.com/tag/humor/ | skipped | navigation_or_tag_link | Skipped. Reason: navigation_or_tag_link. |
| https://quotes.toscrape.com/tag/humor/page/1/ | skipped | navigation_or_tag_link | Skipped. Reason: navigation_or_tag_link. |
| https://quotes.toscrape.com/tag/inspirational/ | skipped | navigation_or_tag_link | Skipped. Reason: navigation_or_tag_link. |
| https://quotes.toscrape.com/tag/inspirational/page/1/ | skipped | navigation_or_tag_link | Skipped. Reason: navigation_or_tag_link. |
| https://quotes.toscrape.com/tag/life/ | skipped | navigation_or_tag_link | Skipped. Reason: navigation_or_tag_link. |
| https://quotes.toscrape.com/tag/life/page/1/ | skipped | navigation_or_tag_link | Skipped. Reason: navigation_or_tag_link. |
| https://quotes.toscrape.com/tag/live/page/1/ | skipped | navigation_or_tag_link | Skipped. Reason: navigation_or_tag_link. |
| https://quotes.toscrape.com/tag/love/ | skipped | navigation_or_tag_link | Skipped. Reason: navigation_or_tag_link. |
| https://quotes.toscrape.com/tag/love/page/1/ | skipped | navigation_or_tag_link | Skipped. Reason: navigation_or_tag_link. |
| https://quotes.toscrape.com/tag/miracle/page/1/ | skipped | navigation_or_tag_link | Skipped. Reason: navigation_or_tag_link. |
| https://quotes.toscrape.com/tag/miracles/page/1/ | skipped | navigation_or_tag_link | Skipped. Reason: navigation_or_tag_link. |
| https://quotes.toscrape.com/tag/misattributed-eleanor-roosevelt/page/1/ | skipped | navigation_or_tag_link | Skipped. Reason: navigation_or_tag_link. |
| https://quotes.toscrape.com/tag/obvious/page/1/ | skipped | navigation_or_tag_link | Skipped. Reason: navigation_or_tag_link. |
| https://quotes.toscrape.com/tag/paraphrased/page/1/ | skipped | navigation_or_tag_link | Skipped. Reason: navigation_or_tag_link. |
| https://quotes.toscrape.com/tag/reading/ | skipped | navigation_or_tag_link | Skipped. Reason: navigation_or_tag_link. |
| https://quotes.toscrape.com/tag/simile/ | skipped | navigation_or_tag_link | Skipped. Reason: navigation_or_tag_link. |
| https://quotes.toscrape.com/tag/simile/page/1/ | skipped | navigation_or_tag_link | Skipped. Reason: navigation_or_tag_link. |
| https://quotes.toscrape.com/tag/success/page/1/ | skipped | navigation_or_tag_link | Skipped. Reason: navigation_or_tag_link. |
| https://quotes.toscrape.com/tag/thinking/page/1/ | skipped | navigation_or_tag_link | Skipped. Reason: navigation_or_tag_link. |
| https://quotes.toscrape.com/tag/truth/ | skipped | navigation_or_tag_link | Skipped. Reason: navigation_or_tag_link. |
| https://quotes.toscrape.com/tag/value/page/1/ | skipped | navigation_or_tag_link | Skipped. Reason: navigation_or_tag_link. |
| https://quotes.toscrape.com/tag/world/page/1/ | skipped | navigation_or_tag_link | Skipped. Reason: navigation_or_tag_link. |
| https://www.goodreads.com/quotes | skipped | external_domain | Skipped. Reason: external_domain. |
| https://www.zyte.com/ | skipped | external_domain | Skipped. Reason: external_domain. |


## Historical events

| URL | Final status | History | Stages |
| --- | --- | --- | --- |
| http://quotes.toscrape.com/author/Albert-Einstein/ | fetched | fetched | v1.5 fetched candidate sources |
| http://quotes.toscrape.com/author/J-K-Rowling/ | fetched | fetched | v1.5 fetched candidate sources |
| https://quotes.toscrape.com/ | fetched | seed URL → queued → kept as candidate → fetched → later skipped as already known | v1.1 seed URLs → v1.3 source records → v1.3 pending link queue → v1.4 filtered link queue → v1.5 fetched candidate sources → v1.5 candidate fetch report → v1.6 followed fetch report |
| https://quotes.toscrape.com/author/Albert-Einstein | fetched | queued → kept as candidate → fetched → later skipped as already known | v1.3 pending link queue → v1.4 filtered link queue → v1.5 fetched candidate sources → v1.5 candidate fetch report → v1.6 followed fetch report |
| https://quotes.toscrape.com/author/Andre-Gide | skipped | queued → kept as candidate → later skipped as already known | v1.3 pending link queue → v1.4 filtered link queue → v1.6 followed fetch report |
| https://quotes.toscrape.com/author/Eleanor-Roosevelt | skipped | queued → kept as candidate → later skipped as already known | v1.3 pending link queue → v1.4 filtered link queue → v1.6 followed fetch report |
| https://quotes.toscrape.com/author/J-K-Rowling | fetched | queued → kept as candidate → fetched → later skipped as already known | v1.3 pending link queue → v1.4 filtered link queue → v1.5 fetched candidate sources → v1.5 candidate fetch report → v1.6 followed fetch report |
| https://quotes.toscrape.com/author/Jane-Austen | skipped | queued → kept as candidate → later skipped as already known | v1.3 pending link queue → v1.4 filtered link queue → v1.6 followed fetch report |
| https://quotes.toscrape.com/author/Marilyn-Monroe | skipped | queued → kept as candidate → later skipped as already known | v1.3 pending link queue → v1.4 filtered link queue → v1.6 followed fetch report |
| https://quotes.toscrape.com/author/Steve-Martin | skipped | queued → kept as candidate → later skipped as already known | v1.3 pending link queue → v1.4 filtered link queue → v1.6 followed fetch report |
| https://quotes.toscrape.com/author/Thomas-A-Edison | skipped | queued → kept as candidate → later skipped as already known | v1.3 pending link queue → v1.4 filtered link queue → v1.6 followed fetch report |
| https://quotes.toscrape.com/login | skipped | queued → skipped: login_account_or_admin_link | v1.3 pending link queue → v1.4 filtered link queue → v1.6 followed fetch report |
| https://quotes.toscrape.com/page/2/ | skipped | queued → kept as candidate → later skipped as already known | v1.3 pending link queue → v1.4 filtered link queue → v1.6 followed fetch report |
| https://quotes.toscrape.com/tag/abilities/page/1/ | skipped | queued → skipped: navigation_or_tag_link | v1.3 pending link queue → v1.4 filtered link queue → v1.6 followed fetch report |
| https://quotes.toscrape.com/tag/adulthood/page/1/ | skipped | queued → skipped: navigation_or_tag_link | v1.3 pending link queue → v1.4 filtered link queue → v1.6 followed fetch report |
| https://quotes.toscrape.com/tag/aliteracy/page/1/ | skipped | queued → skipped: navigation_or_tag_link | v1.3 pending link queue → v1.4 filtered link queue → v1.6 followed fetch report |
| https://quotes.toscrape.com/tag/be-yourself/page/1/ | skipped | queued → skipped: navigation_or_tag_link | v1.3 pending link queue → v1.4 filtered link queue → v1.6 followed fetch report |
| https://quotes.toscrape.com/tag/books/ | skipped | queued → skipped: navigation_or_tag_link | v1.3 pending link queue → v1.4 filtered link queue → v1.6 followed fetch report |
| https://quotes.toscrape.com/tag/books/page/1/ | skipped | queued → skipped: navigation_or_tag_link | v1.3 pending link queue → v1.4 filtered link queue → v1.6 followed fetch report |
| https://quotes.toscrape.com/tag/change/page/1/ | skipped | queued → skipped: navigation_or_tag_link | v1.3 pending link queue → v1.4 filtered link queue → v1.6 followed fetch report |
| https://quotes.toscrape.com/tag/choices/page/1/ | skipped | queued → skipped: navigation_or_tag_link | v1.3 pending link queue → v1.4 filtered link queue → v1.6 followed fetch report |
| https://quotes.toscrape.com/tag/classic/page/1/ | skipped | queued → skipped: navigation_or_tag_link | v1.3 pending link queue → v1.4 filtered link queue → v1.6 followed fetch report |
| https://quotes.toscrape.com/tag/deep-thoughts/page/1/ | skipped | queued → skipped: navigation_or_tag_link | v1.3 pending link queue → v1.4 filtered link queue → v1.6 followed fetch report |
| https://quotes.toscrape.com/tag/edison/page/1/ | skipped | queued → skipped: navigation_or_tag_link | v1.3 pending link queue → v1.4 filtered link queue → v1.6 followed fetch report |
| https://quotes.toscrape.com/tag/failure/page/1/ | skipped | queued → skipped: navigation_or_tag_link | v1.3 pending link queue → v1.4 filtered link queue → v1.6 followed fetch report |
| https://quotes.toscrape.com/tag/friends/ | skipped | queued → skipped: navigation_or_tag_link | v1.3 pending link queue → v1.4 filtered link queue → v1.6 followed fetch report |
| https://quotes.toscrape.com/tag/friendship/ | skipped | queued → skipped: navigation_or_tag_link | v1.3 pending link queue → v1.4 filtered link queue → v1.6 followed fetch report |
| https://quotes.toscrape.com/tag/humor/ | skipped | queued → skipped: navigation_or_tag_link | v1.3 pending link queue → v1.4 filtered link queue → v1.6 followed fetch report |
| https://quotes.toscrape.com/tag/humor/page/1/ | skipped | queued → skipped: navigation_or_tag_link | v1.3 pending link queue → v1.4 filtered link queue → v1.6 followed fetch report |
| https://quotes.toscrape.com/tag/inspirational/ | skipped | queued → skipped: navigation_or_tag_link | v1.3 pending link queue → v1.4 filtered link queue → v1.6 followed fetch report |
| https://quotes.toscrape.com/tag/inspirational/page/1/ | skipped | queued → skipped: navigation_or_tag_link | v1.3 pending link queue → v1.4 filtered link queue → v1.6 followed fetch report |
| https://quotes.toscrape.com/tag/life/ | skipped | queued → skipped: navigation_or_tag_link | v1.3 pending link queue → v1.4 filtered link queue → v1.6 followed fetch report |
| https://quotes.toscrape.com/tag/life/page/1/ | skipped | queued → skipped: navigation_or_tag_link | v1.3 pending link queue → v1.4 filtered link queue → v1.6 followed fetch report |
| https://quotes.toscrape.com/tag/live/page/1/ | skipped | queued → skipped: navigation_or_tag_link | v1.3 pending link queue → v1.4 filtered link queue → v1.6 followed fetch report |
| https://quotes.toscrape.com/tag/love/ | skipped | queued → skipped: navigation_or_tag_link | v1.3 pending link queue → v1.4 filtered link queue → v1.6 followed fetch report |
| https://quotes.toscrape.com/tag/love/page/1/ | skipped | queued → skipped: navigation_or_tag_link | v1.3 pending link queue → v1.4 filtered link queue → v1.6 followed fetch report |
| https://quotes.toscrape.com/tag/miracle/page/1/ | skipped | queued → skipped: navigation_or_tag_link | v1.3 pending link queue → v1.4 filtered link queue → v1.6 followed fetch report |
| https://quotes.toscrape.com/tag/miracles/page/1/ | skipped | queued → skipped: navigation_or_tag_link | v1.3 pending link queue → v1.4 filtered link queue → v1.6 followed fetch report |
| https://quotes.toscrape.com/tag/misattributed-eleanor-roosevelt/page/1/ | skipped | queued → skipped: navigation_or_tag_link | v1.3 pending link queue → v1.4 filtered link queue → v1.6 followed fetch report |
| https://quotes.toscrape.com/tag/obvious/page/1/ | skipped | queued → skipped: navigation_or_tag_link | v1.3 pending link queue → v1.4 filtered link queue → v1.6 followed fetch report |
| https://quotes.toscrape.com/tag/paraphrased/page/1/ | skipped | queued → skipped: navigation_or_tag_link | v1.3 pending link queue → v1.4 filtered link queue → v1.6 followed fetch report |
| https://quotes.toscrape.com/tag/reading/ | skipped | queued → skipped: navigation_or_tag_link | v1.3 pending link queue → v1.4 filtered link queue → v1.6 followed fetch report |
| https://quotes.toscrape.com/tag/simile/ | skipped | queued → skipped: navigation_or_tag_link | v1.3 pending link queue → v1.4 filtered link queue → v1.6 followed fetch report |
| https://quotes.toscrape.com/tag/simile/page/1/ | skipped | queued → skipped: navigation_or_tag_link | v1.3 pending link queue → v1.4 filtered link queue → v1.6 followed fetch report |
| https://quotes.toscrape.com/tag/success/page/1/ | skipped | queued → skipped: navigation_or_tag_link | v1.3 pending link queue → v1.4 filtered link queue → v1.6 followed fetch report |
| https://quotes.toscrape.com/tag/thinking/page/1/ | skipped | queued → skipped: navigation_or_tag_link | v1.3 pending link queue → v1.4 filtered link queue → v1.6 followed fetch report |
| https://quotes.toscrape.com/tag/truth/ | skipped | queued → skipped: navigation_or_tag_link | v1.3 pending link queue → v1.4 filtered link queue → v1.6 followed fetch report |
| https://quotes.toscrape.com/tag/value/page/1/ | skipped | queued → skipped: navigation_or_tag_link | v1.3 pending link queue → v1.4 filtered link queue → v1.6 followed fetch report |
| https://quotes.toscrape.com/tag/world/page/1/ | skipped | queued → skipped: navigation_or_tag_link | v1.3 pending link queue → v1.4 filtered link queue → v1.6 followed fetch report |
| https://www.goodreads.com/quotes | skipped | queued → skipped: external_domain | v1.3 pending link queue → v1.4 filtered link queue → v1.6 followed fetch report |
| https://www.zyte.com/ | skipped | queued → skipped: external_domain | v1.3 pending link queue → v1.4 filtered link queue → v1.6 followed fetch report |


## Trace chains

| URL | Final status | Trace |
| --- | --- | --- |
| http://quotes.toscrape.com/author/Albert-Einstein/ | fetched | http://quotes.toscrape.com/author/Albert-Einstein/ |
| http://quotes.toscrape.com/author/J-K-Rowling/ | fetched | http://quotes.toscrape.com/author/J-K-Rowling/ |
| https://quotes.toscrape.com/ | fetched | https://quotes.toscrape.com/ → https://quotes.toscrape.com/; http://quotes.toscrape.com/author/Albert-Einstein/ → https://quotes.toscrape.com/; http://quotes.toscrape.com/author/J-K-Rowling/ → https://quotes.toscrape.com/ |
| https://quotes.toscrape.com/author/Albert-Einstein | fetched | https://quotes.toscrape.com/ → https://quotes.toscrape.com/author/Albert-Einstein |
| https://quotes.toscrape.com/author/Andre-Gide | skipped | https://quotes.toscrape.com/ → https://quotes.toscrape.com/author/Andre-Gide |
| https://quotes.toscrape.com/author/Eleanor-Roosevelt | skipped | https://quotes.toscrape.com/ → https://quotes.toscrape.com/author/Eleanor-Roosevelt |
| https://quotes.toscrape.com/author/J-K-Rowling | fetched | https://quotes.toscrape.com/ → https://quotes.toscrape.com/author/J-K-Rowling |
| https://quotes.toscrape.com/author/Jane-Austen | skipped | https://quotes.toscrape.com/ → https://quotes.toscrape.com/author/Jane-Austen |
| https://quotes.toscrape.com/author/Marilyn-Monroe | skipped | https://quotes.toscrape.com/ → https://quotes.toscrape.com/author/Marilyn-Monroe |
| https://quotes.toscrape.com/author/Steve-Martin | skipped | https://quotes.toscrape.com/ → https://quotes.toscrape.com/author/Steve-Martin |
| https://quotes.toscrape.com/author/Thomas-A-Edison | skipped | https://quotes.toscrape.com/ → https://quotes.toscrape.com/author/Thomas-A-Edison |
| https://quotes.toscrape.com/login | skipped | https://quotes.toscrape.com/ → https://quotes.toscrape.com/login; http://quotes.toscrape.com/author/Albert-Einstein/ → https://quotes.toscrape.com/login; http://quotes.toscrape.com/author/J-K-Rowling/ → https://quotes.toscrape.com/login |
| https://quotes.toscrape.com/page/2/ | skipped | https://quotes.toscrape.com/ → https://quotes.toscrape.com/page/2/ |
| https://quotes.toscrape.com/tag/abilities/page/1/ | skipped | https://quotes.toscrape.com/ → https://quotes.toscrape.com/tag/abilities/page/1/ |
| https://quotes.toscrape.com/tag/adulthood/page/1/ | skipped | https://quotes.toscrape.com/ → https://quotes.toscrape.com/tag/adulthood/page/1/ |
| https://quotes.toscrape.com/tag/aliteracy/page/1/ | skipped | https://quotes.toscrape.com/ → https://quotes.toscrape.com/tag/aliteracy/page/1/ |
| https://quotes.toscrape.com/tag/be-yourself/page/1/ | skipped | https://quotes.toscrape.com/ → https://quotes.toscrape.com/tag/be-yourself/page/1/ |
| https://quotes.toscrape.com/tag/books/ | skipped | https://quotes.toscrape.com/ → https://quotes.toscrape.com/tag/books/ |
| https://quotes.toscrape.com/tag/books/page/1/ | skipped | https://quotes.toscrape.com/ → https://quotes.toscrape.com/tag/books/page/1/ |
| https://quotes.toscrape.com/tag/change/page/1/ | skipped | https://quotes.toscrape.com/ → https://quotes.toscrape.com/tag/change/page/1/ |
| https://quotes.toscrape.com/tag/choices/page/1/ | skipped | https://quotes.toscrape.com/ → https://quotes.toscrape.com/tag/choices/page/1/ |
| https://quotes.toscrape.com/tag/classic/page/1/ | skipped | https://quotes.toscrape.com/ → https://quotes.toscrape.com/tag/classic/page/1/ |
| https://quotes.toscrape.com/tag/deep-thoughts/page/1/ | skipped | https://quotes.toscrape.com/ → https://quotes.toscrape.com/tag/deep-thoughts/page/1/ |
| https://quotes.toscrape.com/tag/edison/page/1/ | skipped | https://quotes.toscrape.com/ → https://quotes.toscrape.com/tag/edison/page/1/ |
| https://quotes.toscrape.com/tag/failure/page/1/ | skipped | https://quotes.toscrape.com/ → https://quotes.toscrape.com/tag/failure/page/1/ |
| https://quotes.toscrape.com/tag/friends/ | skipped | https://quotes.toscrape.com/ → https://quotes.toscrape.com/tag/friends/ |
| https://quotes.toscrape.com/tag/friendship/ | skipped | https://quotes.toscrape.com/ → https://quotes.toscrape.com/tag/friendship/ |
| https://quotes.toscrape.com/tag/humor/ | skipped | https://quotes.toscrape.com/ → https://quotes.toscrape.com/tag/humor/ |
| https://quotes.toscrape.com/tag/humor/page/1/ | skipped | https://quotes.toscrape.com/ → https://quotes.toscrape.com/tag/humor/page/1/ |
| https://quotes.toscrape.com/tag/inspirational/ | skipped | https://quotes.toscrape.com/ → https://quotes.toscrape.com/tag/inspirational/ |
| https://quotes.toscrape.com/tag/inspirational/page/1/ | skipped | https://quotes.toscrape.com/ → https://quotes.toscrape.com/tag/inspirational/page/1/ |
| https://quotes.toscrape.com/tag/life/ | skipped | https://quotes.toscrape.com/ → https://quotes.toscrape.com/tag/life/ |
| https://quotes.toscrape.com/tag/life/page/1/ | skipped | https://quotes.toscrape.com/ → https://quotes.toscrape.com/tag/life/page/1/ |
| https://quotes.toscrape.com/tag/live/page/1/ | skipped | https://quotes.toscrape.com/ → https://quotes.toscrape.com/tag/live/page/1/ |
| https://quotes.toscrape.com/tag/love/ | skipped | https://quotes.toscrape.com/ → https://quotes.toscrape.com/tag/love/ |
| https://quotes.toscrape.com/tag/love/page/1/ | skipped | https://quotes.toscrape.com/ → https://quotes.toscrape.com/tag/love/page/1/ |
| https://quotes.toscrape.com/tag/miracle/page/1/ | skipped | https://quotes.toscrape.com/ → https://quotes.toscrape.com/tag/miracle/page/1/ |
| https://quotes.toscrape.com/tag/miracles/page/1/ | skipped | https://quotes.toscrape.com/ → https://quotes.toscrape.com/tag/miracles/page/1/ |
| https://quotes.toscrape.com/tag/misattributed-eleanor-roosevelt/page/1/ | skipped | https://quotes.toscrape.com/ → https://quotes.toscrape.com/tag/misattributed-eleanor-roosevelt/page/1/ |
| https://quotes.toscrape.com/tag/obvious/page/1/ | skipped | https://quotes.toscrape.com/ → https://quotes.toscrape.com/tag/obvious/page/1/ |
| https://quotes.toscrape.com/tag/paraphrased/page/1/ | skipped | https://quotes.toscrape.com/ → https://quotes.toscrape.com/tag/paraphrased/page/1/ |
| https://quotes.toscrape.com/tag/reading/ | skipped | https://quotes.toscrape.com/ → https://quotes.toscrape.com/tag/reading/ |
| https://quotes.toscrape.com/tag/simile/ | skipped | https://quotes.toscrape.com/ → https://quotes.toscrape.com/tag/simile/ |
| https://quotes.toscrape.com/tag/simile/page/1/ | skipped | https://quotes.toscrape.com/ → https://quotes.toscrape.com/tag/simile/page/1/ |
| https://quotes.toscrape.com/tag/success/page/1/ | skipped | https://quotes.toscrape.com/ → https://quotes.toscrape.com/tag/success/page/1/ |
| https://quotes.toscrape.com/tag/thinking/page/1/ | skipped | https://quotes.toscrape.com/ → https://quotes.toscrape.com/tag/thinking/page/1/ |
| https://quotes.toscrape.com/tag/truth/ | skipped | https://quotes.toscrape.com/ → https://quotes.toscrape.com/tag/truth/ |
| https://quotes.toscrape.com/tag/value/page/1/ | skipped | https://quotes.toscrape.com/ → https://quotes.toscrape.com/tag/value/page/1/ |
| https://quotes.toscrape.com/tag/world/page/1/ | skipped | https://quotes.toscrape.com/ → https://quotes.toscrape.com/tag/world/page/1/ |
| https://www.goodreads.com/quotes | skipped | https://quotes.toscrape.com/ → https://www.goodreads.com/quotes; http://quotes.toscrape.com/author/Albert-Einstein/ → https://www.goodreads.com/quotes; http://quotes.toscrape.com/author/J-K-Rowling/ → https://www.goodreads.com/quotes |
| https://www.zyte.com/ | skipped | https://quotes.toscrape.com/ → https://www.zyte.com/; http://quotes.toscrape.com/author/Albert-Einstein/ → https://www.zyte.com/; http://quotes.toscrape.com/author/J-K-Rowling/ → https://www.zyte.com/ |


## Validation

| Check | Result |
| --- | --- |
| Validation passed | True |
| Network requests made | False |
| Warnings | None |


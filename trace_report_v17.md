# Story Evidence Collector Trace Report v1.7

Generated: `2026-06-17T09:35:50.321221+00:00`

## Summary counts

| Metric | Count |
| --- | --- |
| Unique URLs traced | 52 |
| Fetched URLs | 5 |
| Skipped URLs | 49 |
| Candidate URLs | 0 |
| Pending URLs | 0 |
| Seed URLs | 1 |


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


## Fetched source table

| URL | Final URL | Title | Robots | Found on |
| --- | --- | --- | --- | --- |
| http://quotes.toscrape.com/author/Albert-Einstein/ | http://quotes.toscrape.com/author/Albert-Einstein/ | Quotes to Scrape | not_found_treated_as_allowed |  |
| http://quotes.toscrape.com/author/J-K-Rowling/ | http://quotes.toscrape.com/author/J-K-Rowling/ | Quotes to Scrape | not_found_treated_as_allowed |  |
| https://quotes.toscrape.com/ | https://quotes.toscrape.com/ | Quotes to Scrape | not_found_treated_as_allowed | https://quotes.toscrape.com/, http://quotes.toscrape.com/author/Albert-Einstein/, http://quotes.toscrape.com/author/J-K-Rowling/ |
| https://quotes.toscrape.com/author/Albert-Einstein | http://quotes.toscrape.com/author/Albert-Einstein/ | Quotes to Scrape | not_found_treated_as_allowed | https://quotes.toscrape.com/ |
| https://quotes.toscrape.com/author/J-K-Rowling | http://quotes.toscrape.com/author/J-K-Rowling/ | Quotes to Scrape | not_found_treated_as_allowed | https://quotes.toscrape.com/ |


## Skipped URL table

| URL | Skip reason | Found on |
| --- | --- | --- |
| https://quotes.toscrape.com/ | already_known | https://quotes.toscrape.com/, http://quotes.toscrape.com/author/Albert-Einstein/, http://quotes.toscrape.com/author/J-K-Rowling/ |
| https://quotes.toscrape.com/author/Albert-Einstein | already_known | https://quotes.toscrape.com/ |
| https://quotes.toscrape.com/author/Andre-Gide | already_known | https://quotes.toscrape.com/ |
| https://quotes.toscrape.com/author/Eleanor-Roosevelt | already_known | https://quotes.toscrape.com/ |
| https://quotes.toscrape.com/author/J-K-Rowling | already_known | https://quotes.toscrape.com/ |
| https://quotes.toscrape.com/author/Jane-Austen | already_known | https://quotes.toscrape.com/ |
| https://quotes.toscrape.com/author/Marilyn-Monroe | already_known | https://quotes.toscrape.com/ |
| https://quotes.toscrape.com/author/Steve-Martin | already_known | https://quotes.toscrape.com/ |
| https://quotes.toscrape.com/author/Thomas-A-Edison | already_known | https://quotes.toscrape.com/ |
| https://quotes.toscrape.com/login | login_account_or_admin_link | https://quotes.toscrape.com/, http://quotes.toscrape.com/author/Albert-Einstein/, http://quotes.toscrape.com/author/J-K-Rowling/ |
| https://quotes.toscrape.com/page/2/ | already_known | https://quotes.toscrape.com/ |
| https://quotes.toscrape.com/tag/abilities/page/1/ | navigation_or_tag_link | https://quotes.toscrape.com/ |
| https://quotes.toscrape.com/tag/adulthood/page/1/ | navigation_or_tag_link | https://quotes.toscrape.com/ |
| https://quotes.toscrape.com/tag/aliteracy/page/1/ | navigation_or_tag_link | https://quotes.toscrape.com/ |
| https://quotes.toscrape.com/tag/be-yourself/page/1/ | navigation_or_tag_link | https://quotes.toscrape.com/ |
| https://quotes.toscrape.com/tag/books/ | navigation_or_tag_link | https://quotes.toscrape.com/ |
| https://quotes.toscrape.com/tag/books/page/1/ | navigation_or_tag_link | https://quotes.toscrape.com/ |
| https://quotes.toscrape.com/tag/change/page/1/ | navigation_or_tag_link | https://quotes.toscrape.com/ |
| https://quotes.toscrape.com/tag/choices/page/1/ | navigation_or_tag_link | https://quotes.toscrape.com/ |
| https://quotes.toscrape.com/tag/classic/page/1/ | navigation_or_tag_link | https://quotes.toscrape.com/ |
| https://quotes.toscrape.com/tag/deep-thoughts/page/1/ | navigation_or_tag_link | https://quotes.toscrape.com/ |
| https://quotes.toscrape.com/tag/edison/page/1/ | navigation_or_tag_link | https://quotes.toscrape.com/ |
| https://quotes.toscrape.com/tag/failure/page/1/ | navigation_or_tag_link | https://quotes.toscrape.com/ |
| https://quotes.toscrape.com/tag/friends/ | navigation_or_tag_link | https://quotes.toscrape.com/ |
| https://quotes.toscrape.com/tag/friendship/ | navigation_or_tag_link | https://quotes.toscrape.com/ |
| https://quotes.toscrape.com/tag/humor/ | navigation_or_tag_link | https://quotes.toscrape.com/ |
| https://quotes.toscrape.com/tag/humor/page/1/ | navigation_or_tag_link | https://quotes.toscrape.com/ |
| https://quotes.toscrape.com/tag/inspirational/ | navigation_or_tag_link | https://quotes.toscrape.com/ |
| https://quotes.toscrape.com/tag/inspirational/page/1/ | navigation_or_tag_link | https://quotes.toscrape.com/ |
| https://quotes.toscrape.com/tag/life/ | navigation_or_tag_link | https://quotes.toscrape.com/ |
| https://quotes.toscrape.com/tag/life/page/1/ | navigation_or_tag_link | https://quotes.toscrape.com/ |
| https://quotes.toscrape.com/tag/live/page/1/ | navigation_or_tag_link | https://quotes.toscrape.com/ |
| https://quotes.toscrape.com/tag/love/ | navigation_or_tag_link | https://quotes.toscrape.com/ |
| https://quotes.toscrape.com/tag/love/page/1/ | navigation_or_tag_link | https://quotes.toscrape.com/ |
| https://quotes.toscrape.com/tag/miracle/page/1/ | navigation_or_tag_link | https://quotes.toscrape.com/ |
| https://quotes.toscrape.com/tag/miracles/page/1/ | navigation_or_tag_link | https://quotes.toscrape.com/ |
| https://quotes.toscrape.com/tag/misattributed-eleanor-roosevelt/page/1/ | navigation_or_tag_link | https://quotes.toscrape.com/ |
| https://quotes.toscrape.com/tag/obvious/page/1/ | navigation_or_tag_link | https://quotes.toscrape.com/ |
| https://quotes.toscrape.com/tag/paraphrased/page/1/ | navigation_or_tag_link | https://quotes.toscrape.com/ |
| https://quotes.toscrape.com/tag/reading/ | navigation_or_tag_link | https://quotes.toscrape.com/ |
| https://quotes.toscrape.com/tag/simile/ | navigation_or_tag_link | https://quotes.toscrape.com/ |
| https://quotes.toscrape.com/tag/simile/page/1/ | navigation_or_tag_link | https://quotes.toscrape.com/ |
| https://quotes.toscrape.com/tag/success/page/1/ | navigation_or_tag_link | https://quotes.toscrape.com/ |
| https://quotes.toscrape.com/tag/thinking/page/1/ | navigation_or_tag_link | https://quotes.toscrape.com/ |
| https://quotes.toscrape.com/tag/truth/ | navigation_or_tag_link | https://quotes.toscrape.com/ |
| https://quotes.toscrape.com/tag/value/page/1/ | navigation_or_tag_link | https://quotes.toscrape.com/ |
| https://quotes.toscrape.com/tag/world/page/1/ | navigation_or_tag_link | https://quotes.toscrape.com/ |
| https://www.goodreads.com/quotes | external_domain | https://quotes.toscrape.com/, http://quotes.toscrape.com/author/Albert-Einstein/, http://quotes.toscrape.com/author/J-K-Rowling/ |
| https://www.zyte.com/ | external_domain | https://quotes.toscrape.com/, http://quotes.toscrape.com/author/Albert-Einstein/, http://quotes.toscrape.com/author/J-K-Rowling/ |


## Trace chains

| URL | Current status | Stages | Trace |
| --- | --- | --- | --- |
| http://quotes.toscrape.com/author/Albert-Einstein/ | fetched | v1.5 fetched candidate sources | http://quotes.toscrape.com/author/Albert-Einstein/ |
| http://quotes.toscrape.com/author/J-K-Rowling/ | fetched | v1.5 fetched candidate sources | http://quotes.toscrape.com/author/J-K-Rowling/ |
| https://quotes.toscrape.com/ | fetched | v1.3 source records → v1.3 pending link queue → v1.4 filtered link queue → v1.5 fetched candidate sources → v1.5 candidate fetch report → v1.6 followed fetch report | https://quotes.toscrape.com/ → https://quotes.toscrape.com/; http://quotes.toscrape.com/author/Albert-Einstein/ → https://quotes.toscrape.com/; http://quotes.toscrape.com/author/J-K-Rowling/ → https://quotes.toscrape.com/ |
| https://quotes.toscrape.com/author/Albert-Einstein | fetched | v1.3 pending link queue → v1.4 filtered link queue → v1.5 fetched candidate sources → v1.5 candidate fetch report → v1.6 followed fetch report | https://quotes.toscrape.com/ → https://quotes.toscrape.com/author/Albert-Einstein |
| https://quotes.toscrape.com/author/Andre-Gide | skipped | v1.3 pending link queue → v1.4 filtered link queue → v1.6 followed fetch report | https://quotes.toscrape.com/ → https://quotes.toscrape.com/author/Andre-Gide |
| https://quotes.toscrape.com/author/Eleanor-Roosevelt | skipped | v1.3 pending link queue → v1.4 filtered link queue → v1.6 followed fetch report | https://quotes.toscrape.com/ → https://quotes.toscrape.com/author/Eleanor-Roosevelt |
| https://quotes.toscrape.com/author/J-K-Rowling | fetched | v1.3 pending link queue → v1.4 filtered link queue → v1.5 fetched candidate sources → v1.5 candidate fetch report → v1.6 followed fetch report | https://quotes.toscrape.com/ → https://quotes.toscrape.com/author/J-K-Rowling |
| https://quotes.toscrape.com/author/Jane-Austen | skipped | v1.3 pending link queue → v1.4 filtered link queue → v1.6 followed fetch report | https://quotes.toscrape.com/ → https://quotes.toscrape.com/author/Jane-Austen |
| https://quotes.toscrape.com/author/Marilyn-Monroe | skipped | v1.3 pending link queue → v1.4 filtered link queue → v1.6 followed fetch report | https://quotes.toscrape.com/ → https://quotes.toscrape.com/author/Marilyn-Monroe |
| https://quotes.toscrape.com/author/Steve-Martin | skipped | v1.3 pending link queue → v1.4 filtered link queue → v1.6 followed fetch report | https://quotes.toscrape.com/ → https://quotes.toscrape.com/author/Steve-Martin |
| https://quotes.toscrape.com/author/Thomas-A-Edison | skipped | v1.3 pending link queue → v1.4 filtered link queue → v1.6 followed fetch report | https://quotes.toscrape.com/ → https://quotes.toscrape.com/author/Thomas-A-Edison |
| https://quotes.toscrape.com/login | skipped | v1.3 pending link queue → v1.4 filtered link queue → v1.6 followed fetch report | https://quotes.toscrape.com/ → https://quotes.toscrape.com/login; http://quotes.toscrape.com/author/Albert-Einstein/ → https://quotes.toscrape.com/login; http://quotes.toscrape.com/author/J-K-Rowling/ → https://quotes.toscrape.com/login |
| https://quotes.toscrape.com/page/2/ | skipped | v1.3 pending link queue → v1.4 filtered link queue → v1.6 followed fetch report | https://quotes.toscrape.com/ → https://quotes.toscrape.com/page/2/ |
| https://quotes.toscrape.com/tag/abilities/page/1/ | skipped | v1.3 pending link queue → v1.4 filtered link queue → v1.6 followed fetch report | https://quotes.toscrape.com/ → https://quotes.toscrape.com/tag/abilities/page/1/ |
| https://quotes.toscrape.com/tag/adulthood/page/1/ | skipped | v1.3 pending link queue → v1.4 filtered link queue → v1.6 followed fetch report | https://quotes.toscrape.com/ → https://quotes.toscrape.com/tag/adulthood/page/1/ |
| https://quotes.toscrape.com/tag/aliteracy/page/1/ | skipped | v1.3 pending link queue → v1.4 filtered link queue → v1.6 followed fetch report | https://quotes.toscrape.com/ → https://quotes.toscrape.com/tag/aliteracy/page/1/ |
| https://quotes.toscrape.com/tag/be-yourself/page/1/ | skipped | v1.3 pending link queue → v1.4 filtered link queue → v1.6 followed fetch report | https://quotes.toscrape.com/ → https://quotes.toscrape.com/tag/be-yourself/page/1/ |
| https://quotes.toscrape.com/tag/books/ | skipped | v1.3 pending link queue → v1.4 filtered link queue → v1.6 followed fetch report | https://quotes.toscrape.com/ → https://quotes.toscrape.com/tag/books/ |
| https://quotes.toscrape.com/tag/books/page/1/ | skipped | v1.3 pending link queue → v1.4 filtered link queue → v1.6 followed fetch report | https://quotes.toscrape.com/ → https://quotes.toscrape.com/tag/books/page/1/ |
| https://quotes.toscrape.com/tag/change/page/1/ | skipped | v1.3 pending link queue → v1.4 filtered link queue → v1.6 followed fetch report | https://quotes.toscrape.com/ → https://quotes.toscrape.com/tag/change/page/1/ |
| https://quotes.toscrape.com/tag/choices/page/1/ | skipped | v1.3 pending link queue → v1.4 filtered link queue → v1.6 followed fetch report | https://quotes.toscrape.com/ → https://quotes.toscrape.com/tag/choices/page/1/ |
| https://quotes.toscrape.com/tag/classic/page/1/ | skipped | v1.3 pending link queue → v1.4 filtered link queue → v1.6 followed fetch report | https://quotes.toscrape.com/ → https://quotes.toscrape.com/tag/classic/page/1/ |
| https://quotes.toscrape.com/tag/deep-thoughts/page/1/ | skipped | v1.3 pending link queue → v1.4 filtered link queue → v1.6 followed fetch report | https://quotes.toscrape.com/ → https://quotes.toscrape.com/tag/deep-thoughts/page/1/ |
| https://quotes.toscrape.com/tag/edison/page/1/ | skipped | v1.3 pending link queue → v1.4 filtered link queue → v1.6 followed fetch report | https://quotes.toscrape.com/ → https://quotes.toscrape.com/tag/edison/page/1/ |
| https://quotes.toscrape.com/tag/failure/page/1/ | skipped | v1.3 pending link queue → v1.4 filtered link queue → v1.6 followed fetch report | https://quotes.toscrape.com/ → https://quotes.toscrape.com/tag/failure/page/1/ |
| https://quotes.toscrape.com/tag/friends/ | skipped | v1.3 pending link queue → v1.4 filtered link queue → v1.6 followed fetch report | https://quotes.toscrape.com/ → https://quotes.toscrape.com/tag/friends/ |
| https://quotes.toscrape.com/tag/friendship/ | skipped | v1.3 pending link queue → v1.4 filtered link queue → v1.6 followed fetch report | https://quotes.toscrape.com/ → https://quotes.toscrape.com/tag/friendship/ |
| https://quotes.toscrape.com/tag/humor/ | skipped | v1.3 pending link queue → v1.4 filtered link queue → v1.6 followed fetch report | https://quotes.toscrape.com/ → https://quotes.toscrape.com/tag/humor/ |
| https://quotes.toscrape.com/tag/humor/page/1/ | skipped | v1.3 pending link queue → v1.4 filtered link queue → v1.6 followed fetch report | https://quotes.toscrape.com/ → https://quotes.toscrape.com/tag/humor/page/1/ |
| https://quotes.toscrape.com/tag/inspirational/ | skipped | v1.3 pending link queue → v1.4 filtered link queue → v1.6 followed fetch report | https://quotes.toscrape.com/ → https://quotes.toscrape.com/tag/inspirational/ |
| https://quotes.toscrape.com/tag/inspirational/page/1/ | skipped | v1.3 pending link queue → v1.4 filtered link queue → v1.6 followed fetch report | https://quotes.toscrape.com/ → https://quotes.toscrape.com/tag/inspirational/page/1/ |
| https://quotes.toscrape.com/tag/life/ | skipped | v1.3 pending link queue → v1.4 filtered link queue → v1.6 followed fetch report | https://quotes.toscrape.com/ → https://quotes.toscrape.com/tag/life/ |
| https://quotes.toscrape.com/tag/life/page/1/ | skipped | v1.3 pending link queue → v1.4 filtered link queue → v1.6 followed fetch report | https://quotes.toscrape.com/ → https://quotes.toscrape.com/tag/life/page/1/ |
| https://quotes.toscrape.com/tag/live/page/1/ | skipped | v1.3 pending link queue → v1.4 filtered link queue → v1.6 followed fetch report | https://quotes.toscrape.com/ → https://quotes.toscrape.com/tag/live/page/1/ |
| https://quotes.toscrape.com/tag/love/ | skipped | v1.3 pending link queue → v1.4 filtered link queue → v1.6 followed fetch report | https://quotes.toscrape.com/ → https://quotes.toscrape.com/tag/love/ |
| https://quotes.toscrape.com/tag/love/page/1/ | skipped | v1.3 pending link queue → v1.4 filtered link queue → v1.6 followed fetch report | https://quotes.toscrape.com/ → https://quotes.toscrape.com/tag/love/page/1/ |
| https://quotes.toscrape.com/tag/miracle/page/1/ | skipped | v1.3 pending link queue → v1.4 filtered link queue → v1.6 followed fetch report | https://quotes.toscrape.com/ → https://quotes.toscrape.com/tag/miracle/page/1/ |
| https://quotes.toscrape.com/tag/miracles/page/1/ | skipped | v1.3 pending link queue → v1.4 filtered link queue → v1.6 followed fetch report | https://quotes.toscrape.com/ → https://quotes.toscrape.com/tag/miracles/page/1/ |
| https://quotes.toscrape.com/tag/misattributed-eleanor-roosevelt/page/1/ | skipped | v1.3 pending link queue → v1.4 filtered link queue → v1.6 followed fetch report | https://quotes.toscrape.com/ → https://quotes.toscrape.com/tag/misattributed-eleanor-roosevelt/page/1/ |
| https://quotes.toscrape.com/tag/obvious/page/1/ | skipped | v1.3 pending link queue → v1.4 filtered link queue → v1.6 followed fetch report | https://quotes.toscrape.com/ → https://quotes.toscrape.com/tag/obvious/page/1/ |
| https://quotes.toscrape.com/tag/paraphrased/page/1/ | skipped | v1.3 pending link queue → v1.4 filtered link queue → v1.6 followed fetch report | https://quotes.toscrape.com/ → https://quotes.toscrape.com/tag/paraphrased/page/1/ |
| https://quotes.toscrape.com/tag/reading/ | skipped | v1.3 pending link queue → v1.4 filtered link queue → v1.6 followed fetch report | https://quotes.toscrape.com/ → https://quotes.toscrape.com/tag/reading/ |
| https://quotes.toscrape.com/tag/simile/ | skipped | v1.3 pending link queue → v1.4 filtered link queue → v1.6 followed fetch report | https://quotes.toscrape.com/ → https://quotes.toscrape.com/tag/simile/ |
| https://quotes.toscrape.com/tag/simile/page/1/ | skipped | v1.3 pending link queue → v1.4 filtered link queue → v1.6 followed fetch report | https://quotes.toscrape.com/ → https://quotes.toscrape.com/tag/simile/page/1/ |
| https://quotes.toscrape.com/tag/success/page/1/ | skipped | v1.3 pending link queue → v1.4 filtered link queue → v1.6 followed fetch report | https://quotes.toscrape.com/ → https://quotes.toscrape.com/tag/success/page/1/ |
| https://quotes.toscrape.com/tag/thinking/page/1/ | skipped | v1.3 pending link queue → v1.4 filtered link queue → v1.6 followed fetch report | https://quotes.toscrape.com/ → https://quotes.toscrape.com/tag/thinking/page/1/ |
| https://quotes.toscrape.com/tag/truth/ | skipped | v1.3 pending link queue → v1.4 filtered link queue → v1.6 followed fetch report | https://quotes.toscrape.com/ → https://quotes.toscrape.com/tag/truth/ |
| https://quotes.toscrape.com/tag/value/page/1/ | skipped | v1.3 pending link queue → v1.4 filtered link queue → v1.6 followed fetch report | https://quotes.toscrape.com/ → https://quotes.toscrape.com/tag/value/page/1/ |
| https://quotes.toscrape.com/tag/world/page/1/ | skipped | v1.3 pending link queue → v1.4 filtered link queue → v1.6 followed fetch report | https://quotes.toscrape.com/ → https://quotes.toscrape.com/tag/world/page/1/ |
| https://thisweekinsmoke.uk/ | seed | v1.1 seed URLs | https://thisweekinsmoke.uk/ |
| https://www.goodreads.com/quotes | skipped | v1.3 pending link queue → v1.4 filtered link queue → v1.6 followed fetch report | https://quotes.toscrape.com/ → https://www.goodreads.com/quotes; http://quotes.toscrape.com/author/Albert-Einstein/ → https://www.goodreads.com/quotes; http://quotes.toscrape.com/author/J-K-Rowling/ → https://www.goodreads.com/quotes |
| https://www.zyte.com/ | skipped | v1.3 pending link queue → v1.4 filtered link queue → v1.6 followed fetch report | https://quotes.toscrape.com/ → https://www.zyte.com/; http://quotes.toscrape.com/author/Albert-Einstein/ → https://www.zyte.com/; http://quotes.toscrape.com/author/J-K-Rowling/ → https://www.zyte.com/ |


## Validation

| Check | Result |
| --- | --- |
| Validation passed | True |
| Network requests made | False |
| Warnings | None |


# Seed URLs from website source candidates v2.6

This report lists seed URLs created from TWIS website source candidate records. It does not prove that the pages are relevant evidence.

## Scope

- No live crawl was run.
- No public pages were fetched.
- Nutch was not called.
- `seed_urls.json` was not overwritten.
- A separate seed file was created for review.

## Files

- Input: `website_source_candidates_v25.json`
- JSON output: `seed_urls_from_website_candidates_v26.json`

## Summary

- Roles included: url
- Seed URLs written: 39
- Included candidate records: 39
- Skipped candidate records: 46

## Included seed URLs

| # | Source | Role | URL | Tag |
|---:|---|---|---|---|
| 1 | GOV.UK News and communications | url | https://www.gov.uk/search/news-and-communications | Government line |
| 2 | UK Parliament Bills | url | https://bills.parliament.uk/ | Law in motion |
| 3 | Office for National Statistics | url | https://www.ons.gov.uk/publications | Evidence layer |
| 4 | Ofcom Broadcasting Code | url | https://www.ofcom.org.uk/tv-radio-and-on-demand/broadcast-standards/broadcast-code/ | Broadcast standards |
| 5 | Reuters World News | url | https://www.reuters.com/world/ | Wire baseline |
| 6 | Associated Press World News | url | https://apnews.com/hub/world-news | Wire baseline |
| 7 | BBC News | url | https://www.bbc.co.uk/news | Mainstream baseline |
| 8 | Sky News | url | https://news.sky.com/ | Rolling news |
| 9 | Channel 4 News | url | https://www.channel4.com/news/ | Broadcast comparison |
| 10 | The Guardian Politics | url | https://www.theguardian.com/politics | Newspaper lens |
| 11 | Financial Times UK politics | url | https://www.ft.com/uk-politics | Business-policy lens |
| 12 | Met Office UK weather warnings | url | https://weather.metoffice.gov.uk/warnings-and-advice/uk-warnings | Weather risk |
| 13 | Food Standards Agency news and alerts | url | https://www.food.gov.uk/news-alerts | Food safety |
| 14 | Bank of England statistics and reports | url | https://www.bankofengland.co.uk/statistics | Economic pressure |
| 15 | BBC World Service | url | https://www.bbc.co.uk/worldserviceradio | UK international public media |
| 16 | France 24 English | url | https://www.france24.com/en/ | French / European lens |
| 17 | Deutsche Welle English | url | https://www.dw.com/en/top-stories/s-9097 | German public-broadcast lens |
| 18 | Al Jazeera English | url | https://www.aljazeera.com/ | Middle East / Global South lens |
| 19 | Euronews | url | https://www.euronews.com/ | European headline mix |
| 20 | CBC News World | url | https://www.cbc.ca/news/world | Canadian public-broadcast lens |
| 21 | PBS NewsHour | url | https://www.pbs.org/newshour/ | US public-media lens |
| 22 | NPR World | url | https://www.npr.org/sections/world/ | US public-radio lens |
| 23 | NHK World-Japan | url | https://www3.nhk.or.jp/nhkworld/en/news/ | Japan / Asia-Pacific lens |
| 24 | Politico Europe | url | https://www.politico.eu/ | EU politics lens |
| 25 | TASS | url | https://tass.com/ | Russian state agency |
| 26 | RIA Novosti | url | https://ria.ru/ | Russian state agency |
| 27 | RT | url | https://www.rt.com/ | Russian state media |
| 28 | Sputnik | url | https://sputnikglobe.com/ | Russian state media |
| 29 | Xinhua | url | https://english.news.cn/ | Chinese state agency |
| 30 | CGTN | url | https://www.cgtn.com/ | Chinese state media |
| 31 | Global Times | url | https://www.globaltimes.cn/ | Chinese state-aligned newspaper |
| 32 | People’s Daily | url | http://en.people.cn/ | Chinese Communist Party paper |
| 33 | China Daily | url | https://www.chinadaily.com.cn/ | Chinese state media |
| 34 | Full Fact | url | https://fullfact.org/ | Claim checking |
| 35 | Chatham House analysis | url | https://www.chathamhouse.org/analysis | International context |
| 36 | Institute for Fiscal Studies | url | https://ifs.org.uk/ | Fiscal evidence |
| 37 | Resolution Foundation | url | https://www.resolutionfoundation.org/ | Living standards |
| 38 | Carbon Brief | url | https://www.carbonbrief.org/ | Climate evidence |
| 39 | United Nations News | url | https://news.un.org/en/ | International body |

## Skipped candidates

| Candidate index | Source | Role | URL | Reason |
|---:|---|---|---|---|
| 2 | GOV.UK News and communications | rssUrl | https://www.gov.uk/search/news-and-communications.atom | url_role rssUrl not selected |
| 4 | UK Parliament Bills | rssUrl | https://www.parliament.uk/site-information/rss-feeds/ | url_role rssUrl not selected |
| 6 | Office for National Statistics | rssUrl | https://www.ons.gov.uk/releasecalendar | url_role rssUrl not selected |
| 7 | Office for National Statistics | secondaryUrl | https://www.ons.gov.uk/releasecalendar | url_role secondaryUrl not selected |
| 9 | Ofcom Broadcasting Code | rssUrl | https://www.ofcom.org.uk/news-centre/ | url_role rssUrl not selected |
| 10 | Ofcom Broadcasting Code | secondaryUrl | https://www.ofcom.org.uk/tv-radio-and-on-demand/broadcast-standards/section-five-due-impartiality-accuracy/ | url_role secondaryUrl not selected |
| 12 | Reuters World News | rssUrl | https://www.reutersagency.com/feed/ | url_role rssUrl not selected |
| 13 | Reuters World News | secondaryUrl | https://www.reutersagency.com/en/about/about-us/ | url_role secondaryUrl not selected |
| 15 | Associated Press World News | rssUrl | https://apnews.com/hub/world-news?output=rss | url_role rssUrl not selected |
| 16 | Associated Press World News | secondaryUrl | https://www.ap.org/about/news-values-and-principles/ | url_role secondaryUrl not selected |
| 18 | BBC News | rssUrl | https://feeds.bbci.co.uk/news/rss.xml | url_role rssUrl not selected |
| 20 | Sky News | rssUrl | https://news.sky.com/feeds/rss/home.xml | url_role rssUrl not selected |
| 22 | Channel 4 News | rssUrl | https://www.channel4.com/news/rss | url_role rssUrl not selected |
| 24 | The Guardian Politics | rssUrl | https://www.theguardian.com/politics/rss | url_role rssUrl not selected |
| 26 | Financial Times UK politics | rssUrl | https://www.ft.com/rss/home/uk | url_role rssUrl not selected |
| 28 | Met Office UK weather warnings | rssUrl | https://weather.metoffice.gov.uk/guides/rss | url_role rssUrl not selected |
| 30 | Food Standards Agency news and alerts | rssUrl | https://www.food.gov.uk/other/rss-feeds | url_role rssUrl not selected |
| 32 | Bank of England statistics and reports | rssUrl | https://www.bankofengland.co.uk/news | url_role rssUrl not selected |
| 33 | Bank of England statistics and reports | secondaryUrl | https://www.bankofengland.co.uk/monetary-policy-report | url_role secondaryUrl not selected |
| 35 | BBC World Service | rssUrl | https://feeds.bbci.co.uk/news/world/rss.xml | url_role rssUrl not selected |
| 36 | BBC World Service | secondaryUrl | https://www.bbc.co.uk/news/world | url_role secondaryUrl not selected |
| 38 | France 24 English | rssUrl | https://www.france24.com/en/rss | url_role rssUrl not selected |
| 40 | Deutsche Welle English | rssUrl | https://rss.dw.com/rdf/rss-en-all | url_role rssUrl not selected |
| 42 | Al Jazeera English | rssUrl | https://www.aljazeera.com/xml/rss/all.xml | url_role rssUrl not selected |
| 44 | Euronews | rssUrl | https://www.euronews.com/rss | url_role rssUrl not selected |
| 46 | CBC News World | rssUrl | https://www.cbc.ca/webfeed/rss/rss-world | url_role rssUrl not selected |
| 48 | PBS NewsHour | rssUrl | https://www.pbs.org/newshour/feeds/rss/headlines | url_role rssUrl not selected |
| 50 | NPR World | rssUrl | https://feeds.npr.org/1004/rss.xml | url_role rssUrl not selected |
| 52 | NHK World-Japan | rssUrl | https://www3.nhk.or.jp/rss/news/cat0.xml | url_role rssUrl not selected |
| 54 | Politico Europe | rssUrl | https://www.politico.eu/feed/ | url_role rssUrl not selected |
| 55 | Politico Europe | secondaryUrl | https://www.politico.eu/rss/ | url_role secondaryUrl not selected |
| 57 | TASS | rssUrl | https://tass.com/rss/v2.xml | url_role rssUrl not selected |
| 59 | RIA Novosti | rssUrl | https://ria.ru/export/rss2/archive/index.xml | url_role rssUrl not selected |
| 61 | RT | rssUrl | https://www.rt.com/rss/ | url_role rssUrl not selected |
| 63 | Sputnik | rssUrl | https://sputnikglobe.com/export/rss2/archive/index.xml | url_role rssUrl not selected |
| 65 | Xinhua | rssUrl | https://english.news.cn/rss.xml | url_role rssUrl not selected |
| 67 | CGTN | rssUrl | https://www.cgtn.com/subscribe/rss | url_role rssUrl not selected |
| 69 | Global Times | rssUrl | https://www.globaltimes.cn/rss/ | url_role rssUrl not selected |
| 71 | People’s Daily | rssUrl | http://en.people.cn/rss/ | url_role rssUrl not selected |
| 73 | China Daily | rssUrl | https://www.chinadaily.com.cn/rss/ | url_role rssUrl not selected |
| 75 | Full Fact | rssUrl | https://fullfact.org/rss/ | url_role rssUrl not selected |
| 77 | Chatham House analysis | rssUrl | https://www.chathamhouse.org/rss-feeds | url_role rssUrl not selected |
| 79 | Institute for Fiscal Studies | rssUrl | https://ifs.org.uk/rss.xml | url_role rssUrl not selected |
| 81 | Resolution Foundation | rssUrl | https://www.resolutionfoundation.org/feed/ | url_role rssUrl not selected |
| 83 | Carbon Brief | rssUrl | https://www.carbonbrief.org/feed/ | url_role rssUrl not selected |
| 85 | United Nations News | rssUrl | https://news.un.org/feed/subscribe/en/news/all/rss.xml | url_role rssUrl not selected |

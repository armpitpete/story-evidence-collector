# How to Use Story Evidence Collector in Simple Mode

Version: v1
Audience: TWIS / Story Evidence Collector users
Status: short user guide

## What Simple Mode is

Simple Mode is the normal, safe way to use the TWIS Source Engine.

It helps you check a small number of public source pages without needing to understand the internal scripts.

Simple Mode shows:

- what source files already exist.
- how many possible sources were found.
- how many websites are ready to check.
- how many public pages were checked.
- where the local review files are saved.

Simple Mode does not publish anything.

It does not commit anything to GitHub.

It does not fetch websites when the page first opens.

## How to open it

From the project folder, run these commands:

    cd "I:\ORDER\GitHub\story-evidence-collector"
    python -m streamlit run twis_source_engine_ui_v24.py

A browser window should open.

The page title should be:

    TWIS Source Engine

The left sidebar should show:

    View
    - Simple
    - Advanced

Simple should be selected by default.

## What Simple Mode shows

### TWIS list

This means the tool found the TWIS source-list page on your computer.

Expected result:

    TWIS list: Found

### Possible sources

This means the tool has found source organisations from the TWIS source list.

Example:

    Possible sources: 85

### Websites to check

This means the tool has built a smaller list of website addresses that can be checked.

Example:

    Websites to check: 39

### Pages checked

This means a small safe sample of public pages has already been checked.

Example:

    Pages checked: 5

### Links saved, not checked

This means the tool found links on checked pages but did not open them.

This is intentional.

The tool saves queued links for review. It does not automatically follow them.

## The main review files

Simple Mode shows three main files.

| Plain name | File name | Meaning |
|---|---|---|
| Review report | source_report_v27.json | Summary of what worked and what failed. |
| Pages checked | sources_raw_v27.json | Public pages that were checked. |
| Links saved, not checked | link_queue_v27.json | Links found on pages. These were saved only, not opened. |

These files are local working files.

They are not automatically added to GitHub.

## When to press Refresh

Only press Refresh safe source check when you want to update the local review files.

Refresh runs three hidden steps:

1. Find sources from the TWIS source list.
2. Make the website check list.
3. Check five public pages safely.

The page check follows robots.txt first.

It checks only the seed pages.

It does not fetch queued links.

## When not to press Refresh

Do not press Refresh if:

- you only want to read the existing report.
- you are not ready to update local files.
- you are working on an article and do not want source files changed.
- you are unsure what changed last time.

Reading the page is safe.

Refreshing changes local output files.

## Advanced Mode

Advanced Mode is for technical use.

It shows script names, paths, and internal controls.

Use Advanced Mode only when you know which script and file you are working with.

Most users should stay in Simple Mode.

## Safe stopping point

After opening Simple Mode, a good stop point is:

- Simple Mode loaded.
- TWIS list says Found.
- Review report exists.
- No page-load error appears.
- You did not press Refresh unless you meant to.

Then close the browser tab.

In PowerShell, stop Streamlit with:

    Ctrl + C

## What Simple Mode does not do

Simple Mode does not:

- publish articles.
- create Evidence Packs automatically.
- decide whether a claim is true.
- replace human review.
- follow queued links automatically.
- run a live crawler.
- bypass robots.txt.
- change GitHub by itself.

## Basic rule

Use Simple Mode to see what has already been collected.

Press Refresh only when you deliberately want to update the local source-check files.

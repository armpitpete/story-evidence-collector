param(
    [string]$Subject,
    [string]$ResearchQuestion,
    [string[]]$KnownSource = @(),
    [string[]]$WantedOutput = @(),
    [ValidateSet("normal", "sensitive", "high-risk")]
    [string]$Sensitivity = "sensitive",
    [string]$Root = "fixtures/evidence-packs",
    [string]$PackId
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Assert-RepoRoot {
    if (-not (Test-Path ".git")) {
        throw "Run this script from the repository root."
    }

    if (-not (Test-Path "scripts\validate_evidence_pack.py")) {
        throw "Cannot find scripts\validate_evidence_pack.py. Run this script from the repository root."
    }
}

function Read-RequiredValue {
    param(
        [string]$CurrentValue,
        [string]$Prompt
    )

    $value = $CurrentValue

    while ([string]::IsNullOrWhiteSpace($value)) {
        $value = Read-Host $Prompt
    }

    return $value.Trim()
}

function Split-InputList {
    param([string]$RawValue)

    if ([string]::IsNullOrWhiteSpace($RawValue)) {
        return @()
    }

    return @(
        $RawValue -split "[,;]" |
            ForEach-Object { $_.Trim() } |
            Where-Object { -not [string]::IsNullOrWhiteSpace($_) }
    )
}

function ConvertTo-PackSlug {
    param([string]$Value)

    $slug = $Value.ToLowerInvariant()
    $slug = $slug -replace "[^a-z0-9]+", "-"
    $slug = $slug.Trim("-")
    $slug = $slug -replace "-+", "-"

    if ([string]::IsNullOrWhiteSpace($slug)) {
        throw "Could not create a pack slug from subject."
    }

    return $slug
}

function Write-Utf8NoBom {
    param(
        [string]$Path,
        [string]$Text
    )

    $encoding = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($Path, $Text, $encoding)
}

function Write-JsonFile {
    param(
        [string]$Path,
        [object]$Data
    )

    $json = $Data | ConvertTo-Json -Depth 10
    Write-Utf8NoBom -Path $Path -Text ($json + "`n")
}

function Write-JsonLine {
    param(
        [string]$Path,
        [object]$Data
    )

    $json = $Data | ConvertTo-Json -Depth 10 -Compress
    Write-Utf8NoBom -Path $Path -Text ($json + "`n")
}

function Get-EditorialRisk {
    param([string]$SensitivityValue)

    switch ($SensitivityValue) {
        "normal" { return "low" }
        "sensitive" { return "medium" }
        "high-risk" { return "high" }
        default { throw "Unsupported sensitivity: $SensitivityValue" }
    }
}

Assert-RepoRoot

$Subject = Read-RequiredValue -CurrentValue $Subject -Prompt "What are you researching?"
$ResearchQuestion = Read-RequiredValue -CurrentValue $ResearchQuestion -Prompt "What question are you trying to answer?"

if ($KnownSource.Count -eq 0) {
    $rawKnownSources = Read-Host "What sources or links do you already have? Separate multiple links with commas. Leave blank if none"
    $KnownSource = @(Split-InputList -RawValue $rawKnownSources)
}

if ($WantedOutput.Count -eq 0) {
    $rawWantedOutput = Read-Host "What output do you want? Default: article, evidence table, connection chart"
    $WantedOutput = @(Split-InputList -RawValue $rawWantedOutput)

    if ($WantedOutput.Count -eq 0) {
        $WantedOutput = @("article", "evidence table", "connection chart")
    }
}

if ([string]::IsNullOrWhiteSpace($PackId)) {
    $today = (Get-Date).ToUniversalTime().ToString("yyyy-MM-dd")
    $PackId = "$today-$(ConvertTo-PackSlug -Value $Subject)"
}

if ($PackId -notmatch "^[0-9]{4}-[0-9]{2}-[0-9]{2}-[a-z0-9]+(?:-[a-z0-9]+)*$") {
    throw "PackId must match YYYY-MM-DD-topic-name using lowercase letters, numbers, and hyphens. Got: $PackId"
}

$packDir = Join-Path $Root $PackId

if (Test-Path $packDir) {
    throw "Pack already exists: $packDir"
}

$createdAt = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
$editorialRisk = Get-EditorialRisk -SensitivityValue $Sensitivity

$folders = @(
    $packDir,
    (Join-Path $packDir "sources"),
    (Join-Path $packDir "claims"),
    (Join-Path $packDir "evidence"),
    (Join-Path $packDir "search"),
    (Join-Path $packDir "timeline"),
    (Join-Path $packDir "review"),
    (Join-Path $packDir "output")
)

foreach ($folder in $folders) {
    New-Item -ItemType Directory -Force $folder | Out-Null
}

$packManifest = [ordered]@{
    pack_schema_version = "1"
    pack_id = $PackId
    title = "Power Profile: $Subject"
    status = "draft"
    created_at = $createdAt
    updated_at = $createdAt
    research_question = $ResearchQuestion
    scope = "Power Profile starter pack created from simple intake. Public power network research only; private-life material, gossip, rumours, and unevidenced associations are out of scope."
    editorial_risk = $editorialRisk
    publishability = "not_ready"
    human_review_required = $true
    records = [ordered]@{
        source_records = "sources/source-records.jsonl"
        source_authority_map = "sources/source-authority-map.jsonl"
        claim_records = "claims/claim-records.jsonl"
        evidence_items = "evidence/evidence-items.jsonl"
        search_diary = "search/search-diary.jsonl"
        negative_evidence_log = "search/negative-evidence-log.jsonl"
        public_record_timeline = "timeline/public-record-timeline.jsonl"
        denial_checks = "timeline/denial-checks.jsonl"
        human_review = "review/human-review.jsonl"
    }
    outputs = [ordered]@{
        final_brief = "output/final-brief.md"
        evidence_summary = "output/evidence-summary.md"
        contradiction_brief = "output/contradiction-brief.md"
    }
    notes = "Created by tools/new-pack.ps1 as a power_profile starter pack. Power Profile intake metadata is stored in manifest.json until pack_type is added to Evidence Pack v1 pack.json."
}

$profileManifest = [ordered]@{
    pack_type = "power_profile"
    pack_id = $PackId
    subject = $Subject
    research_question = $ResearchQuestion
    known_sources = $KnownSource
    wanted_output = $WantedOutput
    sensitivity = $Sensitivity
    status = "draft"
    created_at = $createdAt
    safety_rule = "Simple at the front. Structured underneath. Human-checkable proof trail throughout."
}

Write-JsonFile -Path (Join-Path $packDir "pack.json") -Data $packManifest
Write-JsonFile -Path (Join-Path $packDir "manifest.json") -Data $profileManifest

Write-JsonLine -Path (Join-Path $packDir "sources\source-records.jsonl") -Data ([ordered]@{
    id = "source-001"
    note = "Starter source record. Replace with full public source details."
    known_sources_from_intake = $KnownSource
})

Write-JsonLine -Path (Join-Path $packDir "sources\source-authority-map.jsonl") -Data ([ordered]@{
    id = "authority-001"
    source_id = "source-001"
    related_claim_id = "claim-001"
    note = "Starter source authority note. Replace with source role, weight, and limits."
})

Write-JsonLine -Path (Join-Path $packDir "claims\claim-records.jsonl") -Data ([ordered]@{
    id = "claim-001"
    supported_by = @("evidence-001")
    note = "Starter claim record. Replace with the specific public-interest claim being checked."
})

Write-JsonLine -Path (Join-Path $packDir "evidence\evidence-items.jsonl") -Data ([ordered]@{
    id = "evidence-001"
    source_id = "source-001"
    claim_id = "claim-001"
    note = "Starter evidence item. Replace with a checkable proof fragment."
})

Write-JsonLine -Path (Join-Path $packDir "search\search-diary.jsonl") -Data ([ordered]@{
    id = "search-001"
    note = "Starter search diary entry. Replace with search terms, dates, and sources checked."
})

Write-JsonLine -Path (Join-Path $packDir "search\negative-evidence-log.jsonl") -Data ([ordered]@{
    id = "negative-001"
    note = "Starter negative evidence entry. Replace with what was searched for but not found."
})

Write-JsonLine -Path (Join-Path $packDir "timeline\public-record-timeline.jsonl") -Data ([ordered]@{
    id = "timeline-001"
    source_id = "source-001"
    note = "Starter timeline entry. Replace with a dated public record event."
})

Write-JsonLine -Path (Join-Path $packDir "timeline\denial-checks.jsonl") -Data ([ordered]@{
    id = "denial-001"
    related_claim_id = "claim-001"
    note = "Starter denial check. Replace with a denial, correction, softening, or explanation check."
})

Write-JsonLine -Path (Join-Path $packDir "review\human-review.jsonl") -Data ([ordered]@{
    id = "review-001"
    note = "Starter human review note. Replace with review decision, risk, or unresolved check."
})

Write-JsonLine -Path (Join-Path $packDir "people.jsonl") -Data ([ordered]@{
    id = "person-001"
    name = $Subject
    role = "Profile subject"
    note = "Starter person record. Replace with official public role details and source IDs."
})

Write-JsonLine -Path (Join-Path $packDir "organisations.jsonl") -Data ([ordered]@{
    id = "organisation-001"
    name = "Organisation to check"
    note = "Starter organisation record. Replace with public organisation details and source IDs."
})

Write-JsonLine -Path (Join-Path $packDir "relationships.jsonl") -Data ([ordered]@{
    id = "relationship-001"
    from = "person-001"
    to = "organisation-001"
    relationship_type = "to-check"
    source_id = "source-001"
    confidence = "low"
    public_chart = $false
    note = "Starter relationship record. Low-confidence records must not appear on public charts."
})

Write-JsonLine -Path (Join-Path $packDir "chart_nodes.jsonl") -Data ([ordered]@{
    id = "chart-node-001"
    entity_id = "person-001"
    label = $Subject
    node_type = "person"
    public_chart = $true
    note = "Starter chart node."
})

Write-JsonLine -Path (Join-Path $packDir "chart_edges.jsonl") -Data ([ordered]@{
    id = "chart-edge-001"
    relationship_id = "relationship-001"
    from = "chart-node-001"
    to = "chart-node-002"
    label = "to-check"
    source_id = "source-001"
    confidence = "low"
    public_chart = $false
    note = "Starter chart edge. Public chart edges need a source link and medium or high confidence."
})

$notes = @"
# Power Profile notes

## Subject

$Subject

## Research question

$ResearchQuestion

## Known sources from intake

$($KnownSource | ForEach-Object { "- $_" } | Out-String)
## Wanted output

$($WantedOutput | ForEach-Object { "- $_" } | Out-String)
## Sensitivity

$Sensitivity

## Safety rule

Simple at the front.

Structured underneath.

Human-checkable proof trail throughout.

## Do not include

- private family material
- gossip
- rumours
- unevidenced friendships
- psychological claims
- private relationships
- guilt-by-association claims

## Public chart rule

Every public chart edge must have a source link.

Low-confidence relationships must stay off public charts.
"@

Write-Utf8NoBom -Path (Join-Path $packDir "notes.md") -Text $notes

Write-Utf8NoBom -Path (Join-Path $packDir "README.md") -Text "# Power Profile: $Subject`n`nDraft Power Profile Evidence Pack created by tools/new-pack.ps1.`n"
Write-Utf8NoBom -Path (Join-Path $packDir "output\final-brief.md") -Text "# Final brief`n`nDraft placeholder. Replace after evidence review.`n"
Write-Utf8NoBom -Path (Join-Path $packDir "output\evidence-summary.md") -Text "# Evidence summary`n`nDraft placeholder. Replace after source and evidence records are checked.`n"
Write-Utf8NoBom -Path (Join-Path $packDir "output\contradiction-brief.md") -Text "# Contradiction brief`n`nDraft placeholder. Replace after timeline and denial checks are reviewed.`n"

& python scripts\validate_evidence_pack.py $packDir

if ($LASTEXITCODE -ne 0) {
    throw "Generated evidence pack did not validate: $packDir"
}

Write-Host "Created Power Profile pack: $packDir"
Write-Host "Pack ID: $PackId"

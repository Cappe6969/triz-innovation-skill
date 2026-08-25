#!/usr/bin/env pwsh
<#
.SYNOPSIS
    GAUNTLET - the full quality sweep for triz-innovation-skill.

.DESCRIPTION
    One command that runs everything CI runs, plus hygiene scans CI does not:
      HARD gates (fail = exit 1):
        1. unittest suite            (python -m unittest discover)
        2. branch registry check     (triz.py branches check)
        3. MCP server self-test
        4. syntax compile of every skill script (compileall)
        5. clean worktree            (commit or stash before looping; bypass: -AllowDirty)
      SOFT warnings (reported, never fail):
        6. broken relative .md links in navigation docs
        7. TODO/FIXME/HACK/XXX markers in triz-innovation scripts

    Appends one line per run to .gauntlet/journal.log (gitignored).

.PARAMETER AllowDirty
    Skip the clean-worktree requirement (interactive use only).

.EXAMPLE
    pwsh scripts/gauntlet.ps1
.EXAMPLE
    $env:PYTHON = "C:\path\to\python.exe"; pwsh scripts/gauntlet.ps1
#>
[CmdletBinding()]
param(
    [switch]$AllowDirty
)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
Push-Location $root
try {
    $python = if ($env:PYTHON) { $env:PYTHON } else { 'python' }

    $hardFails = [System.Collections.Generic.List[string]]::new()
    $softWarns = [System.Collections.Generic.List[string]]::new()

    # ── 1-3. The official gate (mirrors ci.yml / check_all.cmd) ──────────
    Write-Host "== [1/7] unittest suite" -ForegroundColor Cyan
    & $python -m unittest discover -s tests -p "test_*.py"
    if ($LASTEXITCODE -ne 0) { $hardFails.Add("unittest suite failed") }

    Write-Host "== [2/7] branch registry" -ForegroundColor Cyan
    & $python .claude/skills/triz-innovation/scripts/triz.py branches check
    if ($LASTEXITCODE -ne 0) { $hardFails.Add("branches check failed") }

    Write-Host "== [3/7] MCP self-test" -ForegroundColor Cyan
    & $python .claude/skills/triz-innovation/mcp/triz_mcp_server.py --self-test | Select-Object -Last 1
    if ($LASTEXITCODE -ne 0) { $hardFails.Add("MCP self-test failed") }

    # ── 4. Syntax compile of all skill scripts ────────────────────────────
    Write-Host "== [4/7] compileall (.claude/skills)" -ForegroundColor Cyan
    & $python -m compileall -q .claude/skills
    if ($LASTEXITCODE -ne 0) { $hardFails.Add("compileall found a syntax error") }

    # ── 5. Clean worktree ────────────────────────────────────────────────
    Write-Host "== [5/7] clean worktree" -ForegroundColor Cyan
    $dirty = @(git status --porcelain | Where-Object { $_ -notmatch '\.gauntlet/' })
    if ($dirty.Count -gt 0 -and -not $AllowDirty) {
        $detail = (($dirty | ForEach-Object { "    $_" }) -join "`n")
        $hardFails.Add("worktree not clean - commit or stash first:`n$detail")
    } elseif ($dirty.Count -gt 0) {
        $softWarns.Add("worktree dirty but -AllowDirty given")
    }

    # ── 6. Relative .md links in navigation docs (soft) ──────────────────
    Write-Host "== [6/7] doc links (soft)" -ForegroundColor Cyan
    $docFiles = @('README.md', 'CONTRIBUTING.md', 'CLAUDE.md', 'BACKLOG.md',
        'cases/README.md') + @(
        Get-ChildItem '.claude/skills/triz-innovation/docs' -Filter '*.md' |
            ForEach-Object { $_.FullName.Substring($root.Length + 1) })
    $broken = [System.Collections.Generic.List[string]]::new()
    foreach ($doc in $docFiles) {
        if (-not (Test-Path $doc)) { continue }
        $dir = Split-Path -Parent $doc
        $text = Get-Content $doc -Raw -Encoding UTF8
        foreach ($m in [regex]::Matches($text, '\]\(([^)\s]+)\)')) {
            $target = $m.Groups[1].Value
            if ($target -match '^(https?:|mailto:|#)' ) { continue }
            $pathPart = ($target -split '#')[0]
            if (-not $pathPart) { continue }
            $resolved = if ($dir) { Join-Path $dir $pathPart } else { $pathPart }
            if (-not (Test-Path $resolved)) {
                $broken.Add("$doc -> $target")
            }
        }
    }
    if ($broken.Count -gt 0) {
        $softWarns.Add(("broken relative md links:`n" +
            (($broken | ForEach-Object { "    $_" }) -join "`n")))
    }

    # ── 7. Marker scan in triz-innovation scripts (soft) ─────────────────
    Write-Host "== [7/7] TODO/FIXME markers (soft)" -ForegroundColor Cyan
    $scriptFiles = Get-ChildItem '.claude/skills/triz-innovation/scripts' -Filter '*.py' |
        ForEach-Object { $_.FullName }
    $markers = @(Select-String -Path $scriptFiles -Pattern '\b(TODO|FIXME|HACK|XXX)\b')
    if ($markers.Count -gt 0) {
        $softWarns.Add("$($markers.Count) marker(s): " +
            (($markers | Select-Object -First 5 |
                ForEach-Object { "$(Split-Path -Leaf $_.Path):$($_.LineNumber)" }) -join ', '))
    }

    # ── Verdict + journal ─────────────────────────────────────────────────
    Write-Host ""
    if ($softWarns.Count -gt 0) {
        Write-Host "Soft warnings:" -ForegroundColor Yellow
        $softWarns | ForEach-Object { Write-Host "  ~ $_" -ForegroundColor Yellow }
    }
    if ($hardFails.Count -gt 0) {
        Write-Host "gauntlet: FAILED" -ForegroundColor Red
        $hardFails | ForEach-Object { Write-Host "  x $_" -ForegroundColor Red }
        New-Item -ItemType Directory -Force '.gauntlet' | Out-Null
        Add-Content '.gauntlet/journal.log' ("{0} FAIL ({1})" -f (Get-Date -Format s), ($hardFails -join '; '))
        exit 1
    }
    Write-Host "gauntlet: PASS" -ForegroundColor Green
    New-Item -ItemType Directory -Force '.gauntlet' | Out-Null
    Add-Content '.gauntlet/journal.log' ("{0} PASS" -f (Get-Date -Format s))
    exit 0
}
finally {
    Pop-Location
}

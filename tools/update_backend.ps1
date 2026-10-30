param(
    [string]$Ref = 'main',
    [string]$Destination = (Split-Path -Parent $PSScriptRoot)
)
$ErrorActionPreference = 'Stop'
$targetPath = (Resolve-Path -LiteralPath $Destination).Path
if (-not (Test-Path -LiteralPath (Join-Path $targetPath 'backend.py'))) {
    throw 'Destination must be an existing zShop folder containing backend.py.'
}
if ($Ref -eq 'main') {
    $branchInfo = Invoke-RestMethod 'https://api.github.com/repos/domyno6773/zShop/git/ref/heads/main'
    $Ref = $branchInfo.object.sha
}
if ($Ref -notmatch '^[0-9a-f]{40}$') { throw 'Use main or a full 40-character commit SHA.' }
$suffix = (Get-Date -Format 'yyyyMMdd-HHmmss') + '-' + [guid]::NewGuid().ToString('N').Substring(0, 6)
$stagingPath = Join-Path $targetPath ('.zshop-update-' + $suffix)
$backupPath = Join-Path $targetPath ('zshop-code-backup-' + $suffix)
$files = @('backend.py', 'geisha_archive.py', 'geisha_preview_renderer.py',
           'geisha_diagnostics.py', 'zshop_bridge.js')
New-Item -ItemType Directory -Path $stagingPath | Out-Null
foreach ($name in $files) {
    $url = "https://raw.githubusercontent.com/domyno6773/zShop/$Ref/$name"
    Invoke-WebRequest $url -OutFile (Join-Path $stagingPath $name) -UseBasicParsing
}
# Parse every Python file before replacing anything. No source is executed.
$pythonFiles = @($files | Where-Object { $_.EndsWith('.py') } | ForEach-Object { Join-Path $stagingPath $_ })
& python -c "import ast,sys; from pathlib import Path; [ast.parse(Path(p).read_text(encoding='utf-8-sig'), filename=p) for p in sys.argv[1:]]" @pythonFiles
if ($LASTEXITCODE -ne 0) { throw 'Staged Python code failed validation; current files were not changed.' }
if ((Get-Item -LiteralPath (Join-Path $stagingPath 'zshop_bridge.js')).Length -lt 100) {
    throw 'Incomplete bridge download; current files were not changed.'
}
New-Item -ItemType Directory -Path $backupPath | Out-Null
foreach ($name in $files) {
    $existingPath = Join-Path $targetPath $name
    if (Test-Path -LiteralPath $existingPath) {
        Copy-Item -LiteralPath $existingPath -Destination (Join-Path $backupPath $name)
    }
}
foreach ($name in $files) {
    Copy-Item -LiteralPath (Join-Path $stagingPath $name) -Destination (Join-Path $targetPath $name) -Force
}
Write-Host "Updated five backend files from commit $Ref"
Write-Host "Previous code saved in $backupPath"
Write-Host 'Geisha archive untouched. Restart Python to load the new code.'

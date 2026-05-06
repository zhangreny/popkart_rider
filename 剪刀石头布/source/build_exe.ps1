$ErrorActionPreference = "Stop"

$SourceDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $SourceDir
$EntryScript = Join-Path $SourceDir "play_caiquan.py"

$Templates = @(
    "entry.png",
    "yes.png",
    "no.png",
    "jiandao.png",
    "shitou.png",
    "bu.png",
    "user-jiandao.png",
    "user-shitou.png",
    "user-bu.png"
)

foreach ($Template in $Templates) {
    $Path = Join-Path $SourceDir $Template
    if (-not (Test-Path -LiteralPath $Path)) {
        throw "Missing template: $Path"
    }
}

$OldErrorActionPreference = $ErrorActionPreference
$ErrorActionPreference = "Continue"
py -m pip show pyinstaller *> $null
$PyInstallerStatus = $LASTEXITCODE
$ErrorActionPreference = $OldErrorActionPreference

if ($PyInstallerStatus -ne 0) {
    py -m pip install --user pyinstaller
}

$AddDataArgs = @()
foreach ($Template in $Templates) {
    $Path = Join-Path $SourceDir $Template
    $AddDataArgs += @("--add-data", "$Path;.")
}

py -m PyInstaller `
    --clean `
    --noconfirm `
    --onefile `
    --console `
    --uac-admin `
    --name play_caiquan `
    --distpath $RepoRoot `
    --workpath (Join-Path $RepoRoot "build") `
    --specpath $SourceDir `
    @AddDataArgs `
    $EntryScript

Write-Host ""
Write-Host "Built: $(Join-Path $RepoRoot 'play_caiquan.exe')"
Write-Host "This exe requests administrator permission when launched."

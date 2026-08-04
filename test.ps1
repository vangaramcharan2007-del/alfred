param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$PytestArgs
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$VenvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $VenvPython)) {
    Write-Error "Project virtual environment not found. Run .\install.ps1 first."
    exit 1
}

if (-not $PytestArgs -or $PytestArgs.Count -eq 0) {
    $PytestArgs = @("tests", "-v", "--cov=src/jarvisx")
}

$env:PYTHONPATH = Join-Path $ProjectRoot "src"
& $VenvPython -m pytest @PytestArgs
exit $LASTEXITCODE

param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$BootstrapArgs
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$BootstrapScript = Join-Path $ProjectRoot "scripts\bootstrap.py"

function Test-PythonCandidate {
    param(
        [string]$Executable,
        [string[]]$Arguments = @()
    )

    if ([string]::IsNullOrWhiteSpace($Executable)) {
        return $false
    }

    try {
        & $Executable @Arguments -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)" *> $null
        return $LASTEXITCODE -eq 0
    }
    catch {
        return $false
    }
}

$VenvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
if (Test-Path $VenvPython) {
    & $VenvPython $BootstrapScript @BootstrapArgs
    exit $LASTEXITCODE
}

$Candidates = @(
    @{ Executable = $env:PYTHON; Arguments = @() },
    @{ Executable = "py"; Arguments = @("-3.12") },
    @{ Executable = "py"; Arguments = @("-3.11") },
    @{ Executable = "python"; Arguments = @() }
)

foreach ($Candidate in $Candidates) {
    if (Test-PythonCandidate -Executable $Candidate.Executable -Arguments $Candidate.Arguments) {
        & $Candidate.Executable @($Candidate.Arguments + @($BootstrapScript) + $BootstrapArgs)
        exit $LASTEXITCODE
    }
}

Write-Error "No Python 3.11+ interpreter found. Install Python 3.11+ or set the PYTHON environment variable to a valid python.exe."
exit 1

$pythonw = "C:\Users\vanga\AppData\Local\Programs\Python\Python311\pythonw.exe"
$script = "c:\Users\vanga\Documents\Codex\2026-07-11\files-mentioned-by-the-user-you\outputs\project-jarvis-x\scripts\auto_wake_sentinel.py"

Write-Host "Launching sentinel with Start-Process..."
$proc = Start-Process -FilePath $pythonw -ArgumentList "`"$script`"" -PassThru
Write-Host "Launched process ID: $($proc.Id)"

Start-Sleep -Seconds 2
$check = Get-Process -Id $proc.Id -ErrorAction SilentlyContinue
if ($check) {
    Write-Host "[SUCCESS] Auto-Wake Sentinel is actively running in background! PID: $($check.Id)"
} else {
    Write-Host "[ERROR] Process terminated immediately."
}

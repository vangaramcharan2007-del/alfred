$startupDir = [System.Environment]::GetFolderPath('Startup')
$lnkPath = Join-Path $startupDir "NarutoAutoWakeSentinel.lnk"
$pythonw = "C:\Users\vanga\AppData\Local\Programs\Python\Python311\pythonw.exe"
$script = "c:\Users\vanga\Documents\Codex\2026-07-11\files-mentioned-by-the-user-you\outputs\project-jarvis-x\scripts\auto_wake_sentinel.py"
$workingDir = "c:\Users\vanga\Documents\Codex\2026-07-11\files-mentioned-by-the-user-you\outputs\project-jarvis-x"

$ws = New-Object -ComObject WScript.Shell
$shortcut = $ws.CreateShortcut($lnkPath)
$shortcut.TargetPath = $pythonw
$shortcut.Arguments = "`"$script`""
$shortcut.WorkingDirectory = $workingDir
$shortcut.Description = "Naruto 4K Live Lock Screen Auto-Wake Sentinel"
$shortcut.WindowStyle = 7 # Minimized/Hidden
$shortcut.Save()

Write-Host "[SUCCESS] Windows Startup shortcut verified at: $lnkPath"
Write-Host "Target: $($shortcut.TargetPath)"
Write-Host "Arguments: $($shortcut.Arguments)"

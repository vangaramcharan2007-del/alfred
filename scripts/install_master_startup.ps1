# ==============================================================================
# JARVIS X: Master Node 24/7 Background System Tray Installer
# ==============================================================================
# Run once on your laptop to enable 24/7 background system tray voice core.
# ==============================================================================

$startupPath = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\JarvisMasterTray.vbs"
$projectDir = "C:\Users\vanga\Documents\Codex\2026-07-11\files-mentioned-by-the-user-you\outputs\project-jarvis-x"

$vbsContent = @"
Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "$projectDir"
WshShell.Run "python -m jarvisx.runtime.tray_daemon", 0, False
"@

Set-Content -Path $startupPath -Value $vbsContent

Write-Host "`n========================================================" -ForegroundColor Cyan
Write-Host "  👑 JARVIS X: 24/7 BACKGROUND TRAY DAEMON INSTALLED" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "  ✅ Auto-starts on boot in your Windows System Tray" -ForegroundColor Green
Write-Host "  🎙️ Listens for voice and handles mesh requests 24/7" -ForegroundColor Green
Write-Host "========================================================`n" -ForegroundColor Cyan

# Start it now in background
Start-Process "wscript.exe" -ArgumentList "`"$startupPath`""

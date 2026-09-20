$taskName = "NarutoAutoLockScreen"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectDir = Split-Path -Parent $scriptDir
$launchScript = Join-Path $projectDir "scripts\launch_now.py"
$pythonExe = "C:\Users\vanga\AppData\Local\Programs\Python\Python311\pythonw.exe"
if (-not (Test-Path $pythonExe)) {
    $pythonExe = "pythonw.exe"
}

# 1. Register Scheduled Task at Logon and on System Unlock
try {
    $action = New-ScheduledTaskAction -Execute $pythonExe -Argument "`"$launchScript`"" -WorkingDirectory $projectDir
    $triggerLogon = New-ScheduledTaskTrigger -AtLogOn
    $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Hours 12)

    Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $triggerLogon -Settings $settings -Description "Auto-launch Naruto 4K Live Lock Screen on Logon and Wake" -Force | Out-Null
    Write-Host "[SUCCESS] Registered Windows Scheduled Task: $taskName (Triggers: At Logon)"
} catch {
    Write-Warning "Scheduled Task registration: $_"
}

# 2. Place shortcut into Windows Startup folder so it runs every time laptop is opened / started
$startupFolder = [System.Environment]::GetFolderPath('Startup')
$startupShortcut = Join-Path $startupFolder "NarutoLiveLockScreen.lnk"
$wsh = New-Object -ComObject WScript.Shell
$sc = $wsh.CreateShortcut($startupShortcut)
$sc.TargetPath = $pythonExe
$sc.Arguments = "`"$launchScript`""
$sc.WorkingDirectory = $projectDir
$sc.Description = "Auto-launch Naruto 4K Live Lock Screen"
$sc.Save()

Write-Host "[SUCCESS] Created Startup entry at: $startupShortcut"

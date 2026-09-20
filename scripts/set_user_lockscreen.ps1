param(
    [string]$ImagePath = "$PSScriptRoot\..\assets\wallpapers\naruto_4k_lockscreen.jpg"
)

try {
    # Resolve absolute path
    $resolvedPath = [System.IO.Path]::GetFullPath($ImagePath)
    Write-Host "Target Image: $resolvedPath"

    if (-not (Test-Path $resolvedPath)) {
        Write-Error "Image does not exist at $resolvedPath"
        exit 1
    }

    # Load Windows Runtime types
    [Windows.System.UserProfile.LockScreen,Windows.System.UserProfile,ContentType=WindowsRuntime] | Out-Null
    [Windows.Storage.StorageFile,Windows.Storage,ContentType=WindowsRuntime] | Out-Null
    Add-Type -AssemblyName System.Runtime.WindowsRuntime

    # Find the AsTask generic method
    $asTaskGeneric = ([System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object { 
        $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1' 
    })[0]

    if ($null -eq $asTaskGeneric) {
        Write-Error "Could not find AsTask generic method."
        exit 1
    }

    function Await-WinRtTask($WinRtTask, $ResultType) {
        $asTask = $asTaskGeneric.MakeGenericMethod($ResultType)
        $netTask = $asTask.Invoke($null, @($WinRtTask))
        $netTask.Wait(-1) | Out-Null
        return $netTask.Result
    }

    function Await-WinRtAction($WinRtAction) {
        $actionTask = ([System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object { 
            $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and -not $_.IsGenericMethod 
        })[0]
        $netTask = $actionTask.Invoke($null, @($WinRtAction))
        $netTask.Wait(-1) | Out-Null
    }

    # Fetch file and set lockscreen
    Write-Host "Accessing StorageFile..."
    $storageFile = Await-WinRtTask ([Windows.Storage.StorageFile]::GetFileFromPathAsync($resolvedPath)) ([Windows.Storage.StorageFile])

    Write-Host "Setting LockScreen Image..."
    Await-WinRtAction ([Windows.System.UserProfile.LockScreen]::SetImageFileAsync($storageFile))

    Write-Host "[SUCCESS] Windows Lock Screen image successfully set via official WinRT UserProfile API!"
} catch {
    Write-Error "Failed to set lock screen: $_"
    exit 1
}

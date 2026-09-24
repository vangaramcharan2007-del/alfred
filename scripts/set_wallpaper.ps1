param(
    [string]$ImagePath = "C:\Users\vanga\Documents\Codex\2026-07-11\files-mentioned-by-the-user-you\outputs\project-jarvis-x\assets\wallpapers\naruto_4k_lockscreen.jpg"
)

Add-Type @"
using System;
using System.Runtime.InteropServices;

public class WallpaperHelper {
    [DllImport("user32.dll", CharSet = CharSet.Auto)]
    public static extern int SystemParametersInfo(int uAction, int uParam, string lpvParam, int fuWinIni);
}
"@

# Remove stale binary TranscodedImageCache
Remove-ItemProperty -Path "HKCU:\Control Panel\Desktop" -Name "TranscodedImageCache" -ErrorAction SilentlyContinue
Set-ItemProperty -Path "HKCU:\Control Panel\Desktop" -Name "WallPaper" -Value $ImagePath
Set-ItemProperty -Path "HKCU:\Control Panel\Desktop" -Name "WallpaperStyle" -Value "10"

# Overwrite TranscodedWallpaper cache in AppData
$transcoded = "$env:APPDATA\Microsoft\Windows\Themes\TranscodedWallpaper"
if (Test-Path $transcoded) {
    Copy-Item -Path $ImagePath -Destination $transcoded -Force
}

# Call SystemParametersInfo SPI_SETDESKWALLPAPER
$res = [WallpaperHelper]::SystemParametersInfo(0x0014, 0, $ImagePath, 3)
Write-Output "Wallpaper set result: $res"

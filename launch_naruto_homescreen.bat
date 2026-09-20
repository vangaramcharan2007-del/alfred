@echo off
if exist "C:\Users\vanga\AppData\Local\BraveSoftware\Brave-Browser\Application\brave.exe" (
    start "" "C:\Users\vanga\AppData\Local\BraveSoftware\Brave-Browser\Application\brave.exe" --app="file:///%~dp0newtab\index.html" --start-maximized
) else if exist "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" (
    start "" "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --app="file:///%~dp0newtab\index.html" --start-maximized
) else (
    start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" --app="file:///%~dp0newtab\index.html" --start-maximized
)
exit

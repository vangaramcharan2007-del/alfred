@echo off
echo ===============================================
echo   Compiling & Launching NEXUS V8 (Apex Edition)
echo ===============================================

powershell -ExecutionPolicy Bypass -File compile_nexus.ps1
if %ERRORLEVEL% NEQ 0 (
    echo Compilation Failed!
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo Launching NEXUS V8...
java -cp "bin;lib/flatlaf.jar;lib/sqlite-jdbc.jar;lib/slf4j-api.jar;lib/slf4j-nop.jar;lib/jsoup.jar" nexus.Main
pause

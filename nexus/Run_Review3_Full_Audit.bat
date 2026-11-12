@echo off
setlocal enabledelayedexpansion
title NEXUS V25.0 - Review 3 Full System Audit and Live Verification
color 0A

echo ===============================================================================
echo     NEXUS V25.0 REVIEW 3 FULL SYSTEM AUDIT AND VERIFICATION RUNNER
echo       Candidate : Ram Charan Vanga (Reg No: RA2511027010164)
echo       Department: B.Tech CSE (Big Data Analytics), SRMIST Kattankulathur
echo       Evaluation: Review 3 (Software Application Development - 20 Marks)
echo ===============================================================================
echo.

cd /d "%~dp0"

if not exist "bin" mkdir "bin"

echo [1/2] Compiling Complete NEXUS V25 Architecture...
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "$files = Get-ChildItem -Path 'src' -Filter '*.java' -Recurse | Select-Object -ExpandProperty FullName; " ^
    "$files | Out-File -Encoding ascii 'sources.txt'; " ^
    "$cp = 'lib/flatlaf.jar;lib/sqlite-jdbc.jar;lib/slf4j-api.jar;lib/slf4j-nop.jar;lib/jsoup.jar;bin'; " ^
    "& javac -cp $cp -d bin '@sources.txt'; " ^
    "$code = $LASTEXITCODE; " ^
    "if (Test-Path 'sources.txt') { Remove-Item 'sources.txt' }; " ^
    "exit $code"

if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Compilation failed!
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo [2/2] Running 15-Subsystem End-to-End Audit and Headless GUI Demonstration...
echo.

java -cp "bin;lib/flatlaf.jar;lib/sqlite-jdbc.jar;lib/slf4j-api.jar;lib/slf4j-nop.jar;lib/jsoup.jar" nexus.Review3VerificationRunner

echo.
echo ===============================================================================
echo   Audit Complete! Live verification screenshot saved to project directory.
echo ===============================================================================
pause

@echo off
setlocal enabledelayedexpansion
title NEXUS Enterprise Platform - V25.0 Review 3 Final Edition
color 0B

echo ===============================================================================
echo     NEXUS ENTERPRISE PLATFORM - V25.0 REVIEW 3 FINAL MASTER EDITION
echo       Candidate : Ram Charan Vanga (Reg No: RA2511027010164)
echo       Department: B.Tech CSE (Big Data Analytics), SRMIST Kattankulathur
echo       Evaluation: Review 3 (Software Application Development - 20 Marks)
echo ===============================================================================
echo.

cd /d "%~dp0"

if not exist "bin" mkdir "bin"

echo [1/2] Verifying Source Compilation...
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "$files = Get-ChildItem -Path 'src' -Filter '*.java' -Recurse | Select-Object -ExpandProperty FullName; " ^
    "$files | Out-File -Encoding ascii 'sources.txt'; " ^
    "$cp = 'lib/flatlaf.jar;lib/sqlite-jdbc.jar;lib/slf4j-api.jar;lib/slf4j-nop.jar;lib/jsoup.jar;bin'; " ^
    "& javac -cp $cp -d bin '@sources.txt'; " ^
    "$code = $LASTEXITCODE; " ^
    "if (Test-Path 'sources.txt') { Remove-Item 'sources.txt' }; " ^
    "exit $code"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Compilation failed with exit code %ERRORLEVEL%!
    pause
    exit /b %ERRORLEVEL%
)

echo   [OK] Compilation verified. 150+ enterprise classes loaded.
echo.
echo [2/2] Launching NEXUS V25.0 Production Suite (18 Integrated Modules)...
echo.

java -XX:+UseG1GC -Xms256m -Xmx1024m -cp "bin;lib/flatlaf.jar;lib/sqlite-jdbc.jar;lib/slf4j-api.jar;lib/slf4j-nop.jar;lib/jsoup.jar" nexus.Main

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Application exited with error code %ERRORLEVEL%.
    pause
)

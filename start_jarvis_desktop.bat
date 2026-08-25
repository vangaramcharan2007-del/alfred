@echo off
title JARVIS X // SOVEREIGN AI DESKTOP
color 0B
echo ===============================================================================
echo  [JARVIS X] STARTING NATIVE DESKTOP HUD WITH ACOUSTIC CLAP ^& WAKEWORD ENGINE
echo ===============================================================================
echo.

cd /d "%~dp0"
"friday-tony-stark-demo\.venv\Scripts\python.exe" "src\jarvisx\voice\desktop_gui_app.py"

if errorlevel 1 (
    echo.
    echo [!] Falling back to system python...
    python "src\jarvisx\voice\desktop_gui_app.py"
)

pause

@echo off
title Launch Chrome with Alfred OS Companion
echo ======================================================================
echo    LAUNCHING ALFRED BRIDGE SERVER & GOOGLE CHROME
echo ======================================================================
echo.

:: 1. Start Python Extension Bridge Daemon in background
start /B "" .venv\Scripts\python.exe src\jarvisx\runtime\extension_server.py

:: 2. Launch Chrome with Alfred Extension pre-loaded
set EXT_PATH=%~dp0extensions\alfred-chrome-companion
start chrome --load-extension="%EXT_PATH%" "chrome://extensions"

echo [OK] Alfred Bridge Server is active at http://127.0.0.1:8765
echo [OK] Chrome launched with Alfred Companion pre-loaded.

@echo off
setlocal
cd /d "%~dp0"
title Naruto 4K Live Lock Screen

echo ======================================================================
echo    NARUTO ENDLESS SKY // 4K LIVE WALLPAPER LOCK SCREEN
echo ======================================================================
echo.

:: Detect Python Environment
if exist ".venv\Scripts\python.exe" (
    set "PY_EXE=.venv\Scripts\python.exe"
) else (
    set "PY_EXE=python.exe"
)

echo [1/3] Synchronizing Windows Native Lock Screen (Win + L)...
powershell -ExecutionPolicy Bypass -File "scripts\set_user_lockscreen.ps1"

echo.
echo [2/3] Checking 4K Video Source (E:\naruto-endless-sky.3840x2160.mp4)...
echo [3/3] Launching Fullscreen Live Lock Screen with Clock & Date...
echo.

%PY_EXE% src\jarvisx\gui\naruto_live_lockscreen.py

echo.
echo [INFO] Lock Screen session completed. Welcome back!
pause

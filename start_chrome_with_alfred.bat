@echo off
title Launch Chrome with Alfred OS Companion
echo ======================================================================
echo    LAUNCHING CHROME WITH ALFRED OS COMPANION PRE-LOADED
echo ======================================================================
echo.
set EXT_PATH=%~dp0extensions\alfred-chrome-companion
start chrome --load-extension="%EXT_PATH%" "chrome://extensions"
echo [OK] Chrome launched with Alfred Companion pre-loaded.

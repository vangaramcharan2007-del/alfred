@echo off
title Alfred Sovereign Master OS & Situation Room HUD
cd /d "%~dp0"
echo =======================================================
echo   ALFRED SOVEREIGN MASTER OS & SITUATION ROOM HUD
echo =======================================================
echo Initializing Groq LPU Brain, Autonomous Sentinels and HUD...
.venv\Scripts\python.exe src\jarvisx\runtime\alfred_situation_room_hud.py
pause

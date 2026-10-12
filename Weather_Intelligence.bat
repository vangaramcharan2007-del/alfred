@echo off
title Weather Intelligence ^& Monitoring System
chcp 65001 >nul
cd /d "%~dp0weather-intelligence"
echo Starting Weather Intelligence Desktop Application...
start "" javaw -jar "weather-frontend\target\weather-frontend-1.0.0.jar"

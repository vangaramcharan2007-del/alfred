@echo off
echo Starting Weather Intelligence ^& Monitoring System (Desktop Swing App)...
echo Mode: Standalone Normal Java (No Localhost Required)
cd /d "%~dp0"
java -jar "weather-frontend\target\weather-frontend-1.0.0.jar"

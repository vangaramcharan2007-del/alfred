@echo off
echo Running Weather Intelligence ^& Monitoring System Live Demonstration...
echo Mode: Standalone Normal Java (No Localhost Required)
cd /d "%~dp0"
java -cp "weather-frontend\target\weather-frontend-1.0.0.jar;weather-frontend\target\lib\*" com.weatherintel.ui.StandaloneDemo

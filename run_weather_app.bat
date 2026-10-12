@echo off
title Weather Intelligence ^& Monitoring System
chcp 65001 >nul
cls

echo ===============================================================================
echo     WEATHER INTELLIGENCE ^& MONITORING SYSTEM
echo     Advanced Object-Oriented Programming (AOOP)
echo     Mode: Standalone Normal Java (No Localhost Required)
echo ===============================================================================
echo.

:: Detect Java runtime
set "JAVA_CMD=java"
where java >nul 2>&1
if %ERRORLEVEL% neq 0 (
    if exist "C:\Program Files\Java\jdk-21\bin\java.exe" (
        set "JAVA_CMD=C:\Program Files\Java\jdk-21\bin\java.exe"
    ) else (
        echo [ERROR] Java runtime not found! Please install Java 21 LTS or add it to PATH.
        pause
        exit /b 1
    )
)

:: Set project directories
set "ROOT_DIR=%~dp0"
set "PROJECT_DIR=%ROOT_DIR%weather-intelligence"
set "FRONTEND_JAR=%PROJECT_DIR%\weather-frontend\target\weather-frontend-1.0.0.jar"
set "LIB_DIR=%PROJECT_DIR%\weather-frontend\target\lib\*"

:: Verify if JAR exists, build if missing
if not exist "%FRONTEND_JAR%" (
    echo [BUILD] Application JAR not found. Building project with Maven...
    set "PATH=C:\tools\apache-maven-3.9.6\bin;%PATH%"
    cd /d "%PROJECT_DIR%"
    call mvn clean package -DskipTests
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] Maven build failed.
        pause
        exit /b 1
    )
    cd /d "%ROOT_DIR%"
)

echo [1] Launch Weather Intelligence Desktop App (Java Swing UI)
echo [2] Run Live Console Demonstration (Full End-to-End Metrics)
echo [3] Rebuild Project with Maven
echo [4] Exit
echo.
choice /c 1234 /t 3 /d 1 /m "Select an option (defaults to 1 in 3 seconds): "

if errorlevel 4 goto exit_script
if errorlevel 3 goto build_project
if errorlevel 2 goto run_demo
if errorlevel 1 goto run_app

:run_app
echo.
echo [LAUNCH] Starting Java Swing Desktop Application...
cd /d "%PROJECT_DIR%"
"%JAVA_CMD%" -jar "%FRONTEND_JAR%"
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Application exited with error code %ERRORLEVEL%.
    pause
)
goto end

:run_demo
echo.
echo [DEMO] Executing Live System Demonstration...
cd /d "%PROJECT_DIR%"
"%JAVA_CMD%" -cp "%FRONTEND_JAR%;%LIB_DIR%" com.weatherintel.ui.StandaloneDemo
echo.
pause
goto end

:build_project
echo.
echo [BUILD] Rebuilding Weather Intelligence System...
set "PATH=C:\tools\apache-maven-3.9.6\bin;%PATH%"
cd /d "%PROJECT_DIR%"
call mvn clean package -DskipTests
echo.
echo Build complete.
pause
goto end

:exit_script
exit /b 0

:end
cd /d "%ROOT_DIR%"

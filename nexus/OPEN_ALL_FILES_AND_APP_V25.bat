@echo off
setlocal enabledelayedexpansion
title NEXUS V25.0 Review 3 - Full Evaluation Workspace Launcher
color 0B

echo ===============================================================================
echo     SRM B.Tech CSE - NEXUS V25.0 REVIEW 3 MASTER EVALUATION WORKSPACE
echo       Candidate : Ram Charan Vanga (Reg No: RA2511027010164)
echo       Target    : Review 3 (Software Application Development - 20 Marks)
echo ===============================================================================
echo.

set "PROJ=%~dp0"
if "%PROJ:~-1%"=="\" set "PROJ=%PROJ:~0,-1%"

echo [1/4] Launching NEXUS V25.0 Production Suite (18 Enterprise Modules)...
start "NEXUS V25 Platform" "%PROJ%\Launch_V25_Review3.bat"

echo.
echo [2/4] Opening All Review 3 Architecture and Implementation Files in VS Code...
set "CODE_EXE=C:\Users\vanga\AppData\Local\Programs\Microsoft VS Code\Code.exe"
if not exist "%CODE_EXE%" set "CODE_EXE=Code.exe"

start "" "%CODE_EXE%" "%PROJ%" ^
    "%PROJ%\src\nexus\NexusApplication.java" ^
    "%PROJ%\src\nexus\Review3VerificationRunner.java" ^
    "%PROJ%\src\nexus\common\exceptions\ExceptionLabPanel.java" ^
    "%PROJ%\src\nexus\cloud\CloudMeshPanel.java" ^
    "%PROJ%\src\nexus\copilot\AiCopilotPanel.java" ^
    "%PROJ%\src\nexus\mobile\MobilePassPanel.java" ^
    "%PROJ%\src\nexus\resilience\ResiliencePanel.java" ^
    "%PROJ%\src\nexus\tenant\TenantPanel.java" ^
    "%PROJ%\src\nexus\vault\VaultAuditPanel.java" ^
    "%PROJ%\src\nexus\web3\Web3ProtocolPanel.java" ^
    "%PROJ%\src\nexus\dashboard\NeuralVisualizerPanel.java" ^
    "%PROJ%\src\nexus\media\MediaPanel.java" ^
    "%PROJ%\src\nexus\media\LiveDistrictCinemaService.java" ^
    "%PROJ%\src\nexus\finance\FinancePanel.java" ^
    "%PROJ%\src\nexus\database\DatabaseService.java" ^
    "%PROJ%\src\nexus\realtime\BookMyShowScraper.java" ^
    "%PROJ%\src\nexus\Main.java"

echo.
echo [3/4] Opening Architecture and Subsystem Directories in Windows Explorer...
start "" explorer.exe "%PROJ%\src\nexus"
start "" explorer.exe "%PROJ%\src\nexus\cloud"
start "" explorer.exe "%PROJ%\src\nexus\vault"

echo.
echo [4/4] Locating Academic Deliverables and Verification Proofs...
if exist "%PROJ%\nexus_v25_review3_dashboard.png" (
    echo   [OK] Found Live Audit Screenshot: %PROJ%\nexus_v25_review3_dashboard.png
)

echo.
echo ===============================================================================
echo   [SUCCESS] All Review 3 Architecture Files Loaded in VS Code Tabs!
echo   NEXUS V25.0 Enterprise Platform is Active.
echo ===============================================================================
timeout /t 3 >nul
exit /b 0

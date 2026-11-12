@echo off
title NEXUS V13 and SRM Evaluation Workspace Launcher
color 0A

echo =====================================================================
echo   SRM B.Tech CSE - NEXUS V13 Evaluation Workspace Launcher
echo   Candidate : Ram Charan Vanga (RA2511027010164)
echo   Target    : V13 Real-Time Exception Lab and Evaluation Suite
echo =====================================================================
echo.

set "PROJ=C:\Users\vanga\Desktop\NEXUS_Java_V7_Startup_Edition"
set "DESK=C:\Users\vanga\Desktop"

echo [1/4] Launching NEXUS V13.0 Exception Lab Application...
start "NEXUS V13 Platform" "%PROJ%\Launch_V13_Exception_Lab.bat"

echo [2/4] Opening All Rubric Architecture and Exception Files in VS Code Tabs...
set "CODE_EXE=C:\Users\vanga\AppData\Local\Programs\Microsoft VS Code\Code.exe"
if not exist "%CODE_EXE%" set "CODE_EXE=Code.exe"

start "" "%CODE_EXE%" "%PROJ%" "%PROJ%\src\nexus\common\exceptions\ExceptionLabPanel.java" "%PROJ%\src\nexus\common\exceptions\NexusException.java" "%PROJ%\src\nexus\common\exceptions\InsufficientFundsException.java" "%PROJ%\src\nexus\common\exceptions\SeatAlreadyBookedException.java" "%PROJ%\src\nexus\common\exceptions\AuthenticationFailedException.java" "%PROJ%\src\nexus\common\exceptions\DatabaseTransactionException.java" "%PROJ%\src\nexus\common\exceptions\GatewayTimeoutException.java" "%PROJ%\src\nexus\common\exceptions\VaultSecurityException.java" "%PROJ%\src\nexus\NexusApplication.java" "%PROJ%\src\nexus\database\DatabaseService.java" "%PROJ%\src\nexus\tasks\JdbcTaskRepository.java" "%PROJ%\src\nexus\finance\JdbcTransactionRepository.java" "%PROJ%\src\nexus\database\IRepository.java" "%PROJ%\src\nexus\tasks\ITaskRepository.java" "%PROJ%\src\nexus\finance\IFinanceEngine.java" "%PROJ%\src\nexus\media\ICinemaGateway.java" "%PROJ%\src\nexus\realtime\BookMyShowScraper.java" "%PROJ%\src\nexus\Review2VerificationRunner.java" "%PROJ%\src\nexus\media\LiveDistrictCinemaService.java" "%PROJ%\src\nexus\media\MediaPanel.java" "%PROJ%\src\nexus\media\InAppCinemaPlayerDialog.java" "%PROJ%\src\nexus\analytics\NexusScore.java" "%PROJ%\src\nexus\Main.java" "%DESK%\NEXUS_Presentation_Script.md" "%DESK%\NEXUS_QnA_CheatSheet.md" "%DESK%\NEXUS_Master_Documentation.md"

echo [3/4] Opening Rubric Project Folders in Windows Explorer...
start "" explorer.exe "%PROJ%\src\nexus\common\exceptions"
start "" explorer.exe "%PROJ%\src\nexus\database"
start "" explorer.exe "%PROJ%\src\nexus"

echo [4/4] Opening Academic Deliverables (Set A PDF Report)...
if exist "%DESK%\SET_A_Data_Visualization_Ram_Charan_Vanga_RA2511027010164.pdf" (
    start "" "%DESK%\SET_A_Data_Visualization_Ram_Charan_Vanga_RA2511027010164.pdf"
)
if exist "%DESK%\SET_A_Data_Visualization_Ram_Charan_Vanga_RA2511027010164.docx" (
    start "" "%DESK%\SET_A_Data_Visualization_Ram_Charan_Vanga_RA2511027010164.docx"
)

echo.
echo =====================================================================
echo  [SUCCESS] All exception files opened in VS Code and NEXUS V13 is active!
echo =====================================================================
ping 127.0.0.1 -n 3 >nul
exit

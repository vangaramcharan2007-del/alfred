@echo off
echo ===================================
echo   Compiling NEXUS Application...
echo ===================================

if not exist bin mkdir bin

:: Find all .java files in the src directory and save paths to a text file
dir /s /B src\*.java > sources.txt

:: Compile all files listed in sources.txt
javac -cp "lib/flatlaf.jar;lib/sqlite-jdbc.jar;lib/slf4j-api.jar;lib/slf4j-nop.jar;lib/jsoup.jar" -d bin @sources.txt

:: Clean up the temporary text file
del sources.txt

echo.
echo Compilation Complete!
pause

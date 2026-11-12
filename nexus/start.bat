@echo off
echo ===================================
echo   Building NEXUS Application...
echo ===================================

if not exist bin mkdir bin
dir /s /B src\*.java > sources.txt
javac -cp "lib/flatlaf.jar;lib/sqlite-jdbc.jar;lib/slf4j-api.jar;lib/slf4j-nop.jar" -d bin @sources.txt
del sources.txt

echo.
echo ===================================
echo   Starting NEXUS Application...
echo ===================================

java -cp "bin;lib/flatlaf.jar;lib/sqlite-jdbc.jar;lib/slf4j-api.jar;lib/slf4j-nop.jar" nexus.Main

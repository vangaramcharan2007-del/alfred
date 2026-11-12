@echo off
echo Compiling NEXUS V3 MAXED...
mkdir src\out 2>nul
dir /s /b src\nexus\*.java > sources.txt
javac -cp "lib/*" -d src\out @sources.txt
del sources.txt

if %errorlevel% neq 0 (
    echo Compilation failed.
    pause
    exit /b %errorlevel%
)

echo Running NEXUS V3 MAXED...
java -cp "src\out;lib/*" nexus.Main
pause

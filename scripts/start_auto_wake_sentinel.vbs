' Robust, location-independent silent launcher for Naruto Auto-Wake Sentinel
Option Explicit
Dim fso, WshShell, vbsDir, projectDir, scriptPath, pythonw

Set fso = CreateObject("Scripting.FileSystemObject")
Set WshShell = CreateObject("WScript.Shell")

' Resolve exact directory of this VBS script
vbsDir = fso.GetParentFolderName(WScript.ScriptFullName)
' Project root is parent of scripts/ folder
projectDir = fso.GetParentFolderName(vbsDir)

scriptPath = projectDir & "\scripts\auto_wake_sentinel.py"
pythonw = "C:\Users\vanga\AppData\Local\Programs\Python\Python311\pythonw.exe"

' Set working directory to project root and run silently (0 = hide window)
WshShell.CurrentDirectory = projectDir
WshShell.Run """" & pythonw & """ """ & scriptPath & """", 0, False

Set WshShell = Nothing
Set fso = Nothing

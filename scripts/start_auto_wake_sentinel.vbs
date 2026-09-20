' Silent background launcher for Naruto Auto-Wake Sentinel
Set WshShell = CreateObject("WScript.Shell")
scriptPath = WshShell.CurrentDirectory & "\scripts\auto_wake_sentinel.py"
pythonw = "C:\Users\vanga\AppData\Local\Programs\Python\Python311\pythonw.exe"

WshShell.Run """" & pythonw & """ """ & scriptPath & """", 0, False
Set WshShell = Nothing

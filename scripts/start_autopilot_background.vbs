Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)
rootDir = fso.GetParentFolderName(scriptDir)

' Launch Dashboard and Continuous Autonomous Daemon silently without pop-up terminal
WshShell.CurrentDirectory = rootDir
WshShell.Run "python run_autopilot.py dashboard --port 8501", 0, False
WshShell.Run "python run_autopilot.py daemon --interval 1800", 0, False

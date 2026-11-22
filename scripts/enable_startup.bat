@echo off
setlocal
echo ========================================================
echo   MONEY GLITCH STUDIO - WINDOWS AUTO-START INSTALLER
echo ========================================================

set "STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "TARGET_VBS=%~dp0start_autopilot_background.vbs"
set "SHORTCUT=%STARTUP_FOLDER%\MoneyGlitchAutopilot.lnk"

echo Target: %TARGET_VBS%
echo Startup Folder: %STARTUP_FOLDER%

powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%SHORTCUT%'); $s.TargetPath = 'wscript.exe'; $s.Arguments = '\"%TARGET_VBS%\"'; $s.WorkingDirectory = '%~dp0..'; $s.Save()"

if exist "%SHORTCUT%" (
    echo [OK] Auto-Start shortcut installed successfully!
    echo Money Glitch will run silently whenever your PC boots up.
) else (
    echo [ERROR] Failed to create startup shortcut.
)

echo ========================================================
pause

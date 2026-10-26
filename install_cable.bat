@echo off
title Install Dedicated Discord Virtual Cable
cd /d "%~dp0"

echo ================================================================
echo  Installing Dedicated Virtual Cable for Discord (VB-CABLE)
echo ================================================================
echo.
echo This will open the official VB-CABLE driver installer.
echo 1. Click "Yes" on the Windows Administrator prompt.
echo 2. Click "Install Driver" on the installer window.
echo.
pause

powershell -Command "Start-Process -FilePath '%~dp0vbcable_extracted\VBCABLE_Setup_x64.exe' -Verb RunAs"

echo.
echo Once installed, restart Discord (or QuickTTS) to see 'CABLE Output'!
pause

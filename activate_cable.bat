@echo off
:: Self-elevate to Administrator
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"
if '%errorlevel%' NEQ '0' (
    echo Requesting Administrator privileges to activate VB-CABLE...
    powershell -Command "Start-Process cmd.exe -ArgumentList '/c \"%~f0\"' -Verb RunAs"
    exit /b
)

title Activating VB-CABLE Without Rebooting...
echo ================================================================
echo  Activating VB-CABLE Virtual Audio Device (No Reboot Required)
echo ================================================================
echo.

echo [1/3] Starting VBAudioVACMME driver service...
net start VBAudioVACMME
echo.

echo [2/3] Restarting Windows Audio Endpoint Builder...
net stop Audiosrv /y
net stop AudioEndpointBuilder /y
net start AudioEndpointBuilder
net start Audiosrv
echo.

echo [3/3] Scanning for audio device endpoints...
pnputil /scan-devices
echo.

echo ================================================================
echo  DONE! VB-CABLE is now running!
echo.
echo  1. Restart Discord (or fully quit Discord and reopen it).
echo  2. Look for 'CABLE Output (VB-Audio Virtual Cable)'.
echo ================================================================
echo.
pause

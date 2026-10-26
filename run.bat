@echo off
title QuickTTS - Mic TTS Bot
cd /d "%~dp0"

if not exist "venv\Scripts\python.exe" (
    echo [QuickTTS] Setting up virtual environment...
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate.bat
)

echo [QuickTTS] Starting QuickTTS...
python main.py
pause

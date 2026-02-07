@echo off
title Attendance System Pro - Launcher

echo ==========================================
echo   COLLEGE ATTENDANCE SYSTEM - AUTO START
echo ==========================================
echo.

:: Ensure script runs from its own folder
cd /d "%~dp0"

echo [1/3] Activating virtual environment...
call venv\Scripts\activate

echo.
echo [2/3] Installing required AI libraries...
pip install -r requirements.txt

echo.
echo [3/3] Starting Face Recognition System...
python main.py

echo.
echo Attendance system closed.

echo.
echo Starting Email Automation...
python email_attendance.py

echo.
echo All processes completed successfully.
pause

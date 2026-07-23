@echo off
REM Launcher for SimpleBrowser 3.0 Web App

cd /d "%~dp0"

echo ==========================================
echo   SimpleBrowser 3.0 - Web Edition
echo ==========================================
echo.

REM Check if dependencies are installed
python -c "import flask" 2>nul
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
)

echo Starting web server...
echo Opening browser automatically...
echo.
echo Press Ctrl+C to stop
echo.

REM Start the web server in background
start /b python webapp.py

REM Wait for server to start
timeout /t 2 /nobreak >nul

REM Open browser automatically
start http://localhost:5000

echo Browser opened. Server is running.
echo.

REM Keep window alive
:keepalive
timeout /t 1 /nobreak >nul
goto keepalive

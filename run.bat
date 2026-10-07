@echo off
echo ================================================
echo   SmartBank AI - Smart Decision System
echo   Banking and Finance ML Platform
echo ================================================
echo.
echo Starting Flask server...
echo Open your browser at: http://127.0.0.1:5000
echo.
echo Default Admin Login:
echo   Username: admin
echo   Password: admin123
echo.
cd /d "%~dp0"
python app.py
pause

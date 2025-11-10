@echo off
cd /d "%~dp0campus_resource_hub"
echo ============================================
echo Campus Resource Hub - Server Startup
echo ============================================
echo.
echo Seeding database...
"C:\Users\molly\OneDrive\Desktop\aidd_t4\.venv\Scripts\python.exe" seed_database.py
echo.
echo Starting server on http://127.0.0.1:5000
echo Press CTRL+C to stop
echo.
"C:\Users\molly\OneDrive\Desktop\aidd_t4\.venv\Scripts\python.exe" -m flask run --host 127.0.0.1 --port 5000
pause

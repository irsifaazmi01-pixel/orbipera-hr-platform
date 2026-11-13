@echo off
cd /d "%~dp0"
echo Menjalankan website ORBIPERA. Buka http://127.0.0.1:8765
start "" cmd /c "timeout /t 3 >nul & start http://127.0.0.1:8765"
where py >nul 2>nul
if %errorlevel%==0 (
  py -3 server.py
) else (
  python server.py
)
pause

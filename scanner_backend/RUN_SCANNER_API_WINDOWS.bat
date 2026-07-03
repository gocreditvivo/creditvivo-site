@echo off
cd /d "%~dp0"
echo Starting Credit Vivo Scanner API...
if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" -m uvicorn main:app --host 127.0.0.1 --port 8081 --reload
) else (
  py -3.12 -m uvicorn main:app --host 127.0.0.1 --port 8081 --reload
)
pause

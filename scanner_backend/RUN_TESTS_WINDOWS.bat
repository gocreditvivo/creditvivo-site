@echo off
cd /d "%~dp0"
echo Running Credit Vivo proprietary parser tests...
python -m pip install pytest
python -m pytest tests
pause

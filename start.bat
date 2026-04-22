@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  echo [CrocDrop] Creating virtual environment...
  python -m venv .venv
)

call ".venv\Scripts\activate.bat"

if exist "requirements.txt" (
  echo [CrocDrop] Installing requirements...
  python -m pip install -r requirements.txt
)

echo [CrocDrop] Starting app...
python main.py

endlocal

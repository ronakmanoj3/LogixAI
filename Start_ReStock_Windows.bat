@echo off
cd /d "%~dp0"
python serve.py --open
if errorlevel 1 (
  echo.
  echo If Python is installed via the Windows launcher, try: py serve.py --open
  pause
)

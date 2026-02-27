@echo off
setlocal

title Cosmetz Python Launcher
color 0D

where python >nul 2>&1
if %errorlevel% neq 0 (
  echo Python is required to run Cosmetz 3.0.
  echo Install Python 3.10+ from https://www.python.org/downloads/windows/
  pause
  exit /b 1
)

python "%~dp0cosmetz.py"
if %errorlevel% neq 0 (
  echo.
  echo Cosmetz exited with an error. Check Cosmetz.log for details.
  pause
)

endlocal

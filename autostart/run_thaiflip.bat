@echo off
set BASE=%~dp0
cd /d "%BASE%\.."
cd app
if exist "..\.venv\Scripts\activate.bat" (
  call "..\.venv\Scripts\activate.bat"
)
start "" /min python main.py

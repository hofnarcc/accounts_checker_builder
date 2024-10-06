@echo off

echo Checking for existing Python installations...

for /f "tokens=*" %%a in ('dir /b /s "%ProgramFiles%\Python*"') do (
  echo Found old Python installation: %%a
  echo Removing...
  rd /s /q "%%a"
)

echo Downloading Python installer...
curl -o python-3.11.8-amd64.exe "https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe"

echo Installing Python...
start /wait /min "" python-3.11.8-amd64.exe
echo Python installation complete.

echo Restarting system for Python to take effect...
echo This will close all applications and restart your system.
timeout /t 5 /nobreak >nul
shutdown /r /t 0

@echo off
setlocal
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\git\sync_to_github.ps1"
set EXITCODE=%ERRORLEVEL%
echo.
if "%EXITCODE%"=="0" (
  echo Sync complete.
) else (
  echo Sync failed with exit code %EXITCODE%.
)
pause
exit /b %EXITCODE%

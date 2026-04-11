@echo off
setlocal
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\git\pull_from_github.ps1"
set EXITCODE=%ERRORLEVEL%
echo.
if "%EXITCODE%"=="0" (
  echo Pull complete.
) else (
  echo Pull failed with exit code %EXITCODE%.
)
pause
exit /b %EXITCODE%

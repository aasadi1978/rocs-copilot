@echo off
if not defined in_subprocess (cmd /k set in_subprocess=y ^& %0 %*) & exit )  

set currPath=%~dp0

echo ======================================================================
echo    Activating any existing virtual environment ...
echo ======================================================================

@REM tasklist /fi "ImageName eq Python.exe" /fo csv 2>NUL | find /I "python.exe">NUL
@REM if "%ERRORLEVEL%"=="0" (
@REM 	taskkill /IM python.exe /F
@REM )

call .venv\Scripts\deactivate 2>NUL
call .venv\Scripts\activate
if errorlevel 1 (
    echo Failed to activate virtual environment!
    exit /b 1
)

call cls
exit /b 0
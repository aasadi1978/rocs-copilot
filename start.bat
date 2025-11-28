@echo off
setlocal enabledelayedexpansion
:: Add the following line to prevent the app from crashing in event of error
if not defined in_subprocess (cmd /k set in_subprocess=y ^& %0 %*) & exit )  

call cls

echo ======================================================================
echo    FenixBot: A private AI-powered chatbot for private use
echo ======================================================================

tasklist /fi "ImageName eq python.exe" /fo csv 2>NUL | find /I "python.exe">NUL
if "%ERRORLEVEL%"=="0" taskkill /IM python.exe /F >NUL

call .venv\Scripts\activate
waitress-serve --host=127.0.0.1 --port=5000 backend.app:app
if "%ERRORLEVEL%" NEQ "0" (
    echo #####################################################################################
    echo Failed to start the FenixBot application. Please check the error messages above.
    echo #####################################################################################
    exit /b 1
)

endlocal
exit /b !ERRORLEVEL!

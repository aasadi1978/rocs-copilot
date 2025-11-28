setlocal enabledelayedexpansion
@echo off

set APP_NAME=fenix

call .venv/Scripts/activate
echo ------------------------------------------------------------
echo Updating app version on pyproject.toml ...
rem Run Python once, capture both output and exit code
for /f "delims=" %%v in ('python auto_version.py 2^>^&1') do set "APP_VERSION=%%v"
set "EXITCODE=%ERRORLEVEL%"
if %EXITCODE% neq 0 (
    echo Failed to run auto_version.py. Please check the error messages above.
    exit /b %EXITCODE%
)
echo ------------------------------------------------------------
git init
echo ------------------------------------------------------------

@REM echo Set secret OPENAI_API_KEY before running this script.
@REM gh secret set OPENAI_API_KEY --body "%OPENAI_API_KEY%" 
@REM gh secret set LANGCHAIN_API_KEY --body "%LANGCHAIN_API_KEY%" 
@REM gh secret set GROQ_API_KEY --body "%GROQ_API_KEY%" 

@REM if errorlevel 1 (
@REM     echo Failed to set GitHub secret. Please check the error messages above.
@REM     exit /b 1
@REM ) else (
@REM     echo Successfully set GitHub secret OPENAI_API_KEY.
@REM )
@REM echo ------------------------------------------------------------

git status

set /p commit_message=Enter commit message:
if "%commit_message%" neq "" (
    git add .
    git commit -m "%commit_message%"
    if errorlevel 1 (
        echo Commit failed. Please check the error messages above.
        exit /b 1
    ) else (
        echo Commit successful.
    )
) else (
    echo %commit_message%
    echo Commit message cannot be empty. Aborting commit.
    exit /b 1
)

:tagging
echo Managing tags ...
echo Top 5 tags:
echo Make sure the version in pyproject.toml is updated if applicable.
echo To delete a tag, use git tag -d tagname
echo ------------------------------------------------------------

set "tag=%APP_NAME%-py3-%APP_VERSION%"
if "%tag%" neq "" (

    git tag -d "%tag%" 2>nul
    git push --delete origin "%tag%" 2>nul
    @REM git push --delete origin_private "%tag%" 2>nul
    if errorlevel 1 (
        echo No existing tag named "%tag%" to delete.
    ) else (
        echo Deleted existing tag named "%tag%".
    )

    git tag "%tag%"
    if errorlevel 1 (
        tag=""
        echo Tagging failed. Please check the error messages above.
        goto tagging
    ) else (
        echo Tagging successful.
        goto committing_done
    )
) else (
    echo Skipping tagging.
)

:committing_done
echo ------------------------------------------------------------
echo Recent commit history:
@REM git log: Shows the commit history.
@REM --oneline: Each commit is shown as a single line (short hash + message).
@REM --decorate: Shows branch and tag names next to commits.
@REM --graph: Adds an ASCII graph showing branch and merge structure.
@REM --all: Includes all branches, not just the current one.
git log --oneline --decorate --graph --all -10
echo ------------------------------------------------------------

echo You can now push your changes using 'git push' command.
echo The following remotes are available:
git remote -v

echo ------------------------------------------------------------
echo Pushing to remote repository origin
git push origin master --force
if errorlevel 1 (
    echo Push failed. Please check the error messages above.
    exit /b 1
) else (
    echo Push successful.
)

echo ------------------------------------------------------------
if "%tag%" neq "" (
    echo Pushing tags to remote repositories origin
    echo Pushing tag %tag% to origin
    git push origin tag %tag%
    if errorlevel 1 (
        echo Push tags to origin failed. Please check the error messages above.
    ) else (
        echo Push tags to origin successful.
    )
)

endlocal
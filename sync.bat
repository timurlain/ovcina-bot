@echo off
REM Sync OneDrive content -> repo, commit, push -> cloud bot redeploys (~30s)

cd /d "%~dp0"

py -3.14 scripts\sync-content.py
if errorlevel 1 goto :error

git add -A content
git diff --cached --quiet content
if %errorlevel%==0 (
    echo No content changes — nothing to push.
    goto :eof
)

for /f %%i in ('powershell -NoProfile -Command "Get-Date -Format yyyy-MM-dd_HH-mm"') do set TS=%%i
git commit -m "Content sync %TS%"
if errorlevel 1 goto :error
git push
if errorlevel 1 goto :error

echo.
echo Pushed. Cloud bot will pick up changes in ~30 seconds.
echo Watch: gh run list --repo timurlain/ovcina-bot --limit 1
goto :eof

:error
echo.
echo Sync failed.
exit /b 1

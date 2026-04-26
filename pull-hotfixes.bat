@echo off
REM One-shot post-event sync: pull hotfixes from Azure File Share -> OneDrive
REM Run this AFTER the event to merge the hotfixes into the canonical pravidla repo.

set DEST=C:\Users\TomášPajonk\OneDrive - SolverTech s.r.o\Bridge\Ovčina\pravidla\_hotfixy

if not exist "%DEST%" mkdir "%DEST%"

echo Fetching storage key...
for /f "tokens=*" %%i in ('az storage account keys list -g ovcina -n ovcinahrastorage --query "[0].value" -o tsv') do set STORAGE_KEY=%%i

if "%STORAGE_KEY%"=="" (
    echo ERROR: failed to fetch storage key. Are you logged in via 'az login'?
    exit /b 1
)

echo Downloading hotfixes -^> %DEST%
az storage file download-batch ^
  --account-name ovcinahrastorage ^
  --account-key "%STORAGE_KEY%" ^
  --source bot-data ^
  --destination "%DEST%" ^
  --pattern "hotfixes/*.md" ^
  --output table

echo.
echo Done. Hotfixes are in: %DEST%\hotfixes\
echo.
echo Next: review each HOT-*.md and either:
echo   - Promote to a permanent rule in pravidla/rozhodnuti/ (rename to ROZ-NNN)
echo   - Archive to pravidla/_archiv/ if no longer needed
echo   - Delete if it was a typo / experimental

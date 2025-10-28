@echo off
cd /d D:\Personal\Project\work-progress

echo ======================================
echo Push started: %date% %time%
echo ======================================
echo.

git push

echo.
if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] Push completed
) else (
    echo [FAILED] Push failed with error code: %ERRORLEVEL%
)
echo.
echo ======================================
echo Finished: %date% %time%
echo ======================================
echo.
pause

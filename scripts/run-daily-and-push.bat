@echo off
REM 執行每日報告生成並確保推送
cd /d D:\Personal\Project\work-progress

echo ======================================
echo Daily Report Generation Started
echo %date% %time%
echo ======================================
echo.

REM 先同步最新的變更
echo Pulling latest changes from remote...
git pull origin main >> logs\daily-report.log 2>&1
if %errorlevel% neq 0 (
    echo WARNING: Git pull failed, continuing anyway...
)
echo.

REM 執行 Python 腳本
python scripts\auto-daily-report.py >> logs\daily-report.log 2>&1

echo.
echo ======================================
echo Ensuring all commits are pushed
echo ======================================
echo.

REM 保險機制：再次確保所有變更都被推送
git push >> logs\daily-report.log 2>&1

echo.
echo ======================================
echo Completed: %date% %time%
echo ======================================
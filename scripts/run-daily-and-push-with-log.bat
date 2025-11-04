@echo off
REM 執行每日報告生成並確保推送（含完整 log）
cd /d D:\Personal\Project\work-progress

REM 確保 logs 目錄存在
if not exist logs mkdir logs

REM 設定日誌檔案（使用日期命名，避免檔案過大）
set LOGFILE=logs\daily-report-%date:~0,4%-%date:~5,2%-%date:~8,2%.log

REM 開始記錄
echo. >> %LOGFILE%
echo ====================================== >> %LOGFILE%
echo Daily Report Generation Started >> %LOGFILE%
echo %date% %time% >> %LOGFILE%
echo ====================================== >> %LOGFILE%
echo. >> %LOGFILE%

echo ======================================
echo Daily Report Generation Started
echo %date% %time%
echo Log: %LOGFILE%
echo ======================================
echo.

REM 先同步最新的變更
echo Pulling latest changes from remote...
echo [GIT PULL] Starting... >> %LOGFILE%
git pull origin main >> %LOGFILE% 2>&1
set PULL_EXIT=%errorlevel%
echo [GIT PULL] Exit code: %PULL_EXIT% >> %LOGFILE%
if %PULL_EXIT% neq 0 (
    echo WARNING: Git pull failed, continuing anyway... >> %LOGFILE%
    echo WARNING: Git pull failed, continuing anyway...
)
echo. >> %LOGFILE%

REM 執行 Python 腳本
echo Running auto-daily-report.py...
echo [PYTHON] Starting auto-daily-report.py... >> %LOGFILE%
python scripts\auto-daily-report.py >> %LOGFILE% 2>&1
set PYTHON_EXIT=%errorlevel%
echo [PYTHON] Exit code: %PYTHON_EXIT% >> %LOGFILE%
echo. >> %LOGFILE%

echo.
echo ======================================
echo Ensuring all commits are pushed
echo ======================================
echo.

REM 保險機制：再次確保所有變更都被推送
echo Final push...
echo [GIT PUSH] Starting final push... >> %LOGFILE%
git push >> %LOGFILE% 2>&1
set PUSH_EXIT=%errorlevel%
echo [GIT PUSH] Exit code: %PUSH_EXIT% >> %LOGFILE%
echo. >> %LOGFILE%

REM 總結
echo ====================================== >> %LOGFILE%
echo Completed: %date% %time% >> %LOGFILE%
echo Results: Pull=%PULL_EXIT%, Python=%PYTHON_EXIT%, Push=%PUSH_EXIT% >> %LOGFILE%
if %PYTHON_EXIT% equ 0 if %PUSH_EXIT% equ 0 (
    echo Status: SUCCESS >> %LOGFILE%
) else (
    echo Status: FAILED >> %LOGFILE%
)
echo ====================================== >> %LOGFILE%

echo.
echo ======================================
echo Completed: %date% %time%
echo Results: Pull=%PULL_EXIT%, Python=%PYTHON_EXIT%, Push=%PUSH_EXIT%
echo Check log: %LOGFILE%
echo ======================================

REM 清理舊 log（保留最近 30 天）
forfiles /P logs /M daily-report-*.log /D -30 /C "cmd /c del @file" 2>nul

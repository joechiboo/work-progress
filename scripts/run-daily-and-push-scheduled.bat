@echo off
REM 專門給排程使用的版本（處理認證問題）
cd /d D:\Personal\Project\work-progress

REM 確保 logs 目錄存在
if not exist logs mkdir logs

REM 設定日誌檔案
set LOGFILE=logs\daily-report-%date:~0,4%-%date:~5,2%-%date:~8,2%.log

REM 開始記錄
echo. >> %LOGFILE%
echo ====================================== >> %LOGFILE%
echo Daily Report Generation Started >> %LOGFILE%
echo %date% %time% >> %LOGFILE%
echo Current User: %USERNAME% >> %LOGFILE%
echo ====================================== >> %LOGFILE%
echo. >> %LOGFILE%

REM 設定完整的 PATH（確保能找到 git 和 python）
set PATH=C:\Python310;C:\Python310\Scripts;%PATH%
set PATH=C:\Program Files\Git\cmd;%PATH%
echo PATH: %PATH% >> %LOGFILE%
echo. >> %LOGFILE%

REM 測試 git 和 python 是否可用
echo [CHECK] Testing git... >> %LOGFILE%
git --version >> %LOGFILE% 2>&1
echo [CHECK] Testing python... >> %LOGFILE%
python --version >> %LOGFILE% 2>&1
echo. >> %LOGFILE%

REM 先同步最新的變更
echo [GIT PULL] Starting... >> %LOGFILE%
git pull origin main >> %LOGFILE% 2>&1
set PULL_EXIT=%errorlevel%
echo [GIT PULL] Exit code: %PULL_EXIT% >> %LOGFILE%
if %PULL_EXIT% neq 0 (
    echo WARNING: Git pull failed, continuing anyway... >> %LOGFILE%
)
echo. >> %LOGFILE%

REM 執行 Python 腳本（不使用 --today，讓它自動處理昨天）
echo [PYTHON] Starting auto-daily-report.py... >> %LOGFILE%
python scripts\auto-daily-report.py >> %LOGFILE% 2>&1
set PYTHON_EXIT=%errorlevel%
echo [PYTHON] Exit code: %PYTHON_EXIT% >> %LOGFILE%
echo. >> %LOGFILE%

REM 檢查是否有需要推送的變更
echo [GIT STATUS] Checking status... >> %LOGFILE%
git status >> %LOGFILE% 2>&1
echo. >> %LOGFILE%

REM 保險機制：再次確保所有變更都被推送
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
    exit /b 0
) else (
    echo Status: FAILED >> %LOGFILE%
    echo ERROR: Check the log above for details >> %LOGFILE%
    exit /b 1
)
echo ====================================== >> %LOGFILE%

REM 清理舊 log（保留最近 30 天）
forfiles /P logs /M daily-report-*.log /D -30 /C "cmd /c del @file" 2>nul

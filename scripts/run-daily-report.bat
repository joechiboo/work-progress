@echo off
REM 每日自動工作紀錄生成器
REM 在工作排程器中執行此批次檔

cd /d D:\Personal\Project\work-progress
python scripts\auto-daily-report.py >> logs\daily-report.log 2>&1

REM 如果需要的話，可以記錄執行時間
echo. >> logs\daily-report.log
echo ===================================== >> logs\daily-report.log
echo. >> logs\daily-report.log

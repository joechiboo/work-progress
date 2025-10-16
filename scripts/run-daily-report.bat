@echo off
REM 每日自動工作紀錄生成器
REM 在工作排程器中執行此批次檔

REM 切換到專案目錄
cd /d D:\Personal\Project\work-progress

REM 確保 logs 目錄存在
if not exist logs mkdir logs

REM 記錄開始時間
echo. >> logs\daily-report.log
echo ================================================ >> logs\daily-report.log
echo [BAT] 批次檔開始執行: %date% %time% >> logs\daily-report.log
echo ================================================ >> logs\daily-report.log

REM 執行 Python 腳本，將輸出寫入 log
python scripts\auto-daily-report.py >> logs\daily-report.log 2>&1

REM 檢查執行結果
if %ERRORLEVEL% EQU 0 (
    echo [BAT] 執行成功: %date% %time% >> logs\daily-report.log
) else (
    echo [BAT] 執行失敗 ^(錯誤碼: %ERRORLEVEL%^): %date% %time% >> logs\daily-report.log
)

echo ================================================ >> logs\daily-report.log
echo. >> logs\daily-report.log

@echo off
REM 重新建立每日工作報告排程任務
echo ======================================
echo 設定每日工作報告排程任務
echo ======================================
echo.

REM 先刪除舊的排程（如果存在）
echo 刪除舊的排程任務...
schtasks /delete /tn "DailyWorkReport" /f 2>nul
schtasks /delete /tn "工作日誌更新" /f 2>nul
echo.

REM 建立新的排程任務
REM 重點：
REM 1. /RL HIGHEST - 以最高權限執行
REM 2. /RU %USERNAME% - 使用當前使用者（確保有 Git 憑證）
REM 3. /IT - 只在使用者登入時執行（確保能存取憑證）

echo 建立新的排程任務...
schtasks /create ^
  /tn "DailyWorkReport" ^
  /tr "D:\Personal\Project\work-progress\scripts\run-daily-and-push-scheduled.bat" ^
  /sc daily ^
  /st 07:00 ^
  /rl HIGHEST ^
  /ru %USERNAME% ^
  /it ^
  /f

if %errorlevel% equ 0 (
    echo.
    echo ✓ 排程任務建立成功！
    echo.
    echo 任務設定：
    echo   - 任務名稱: DailyWorkReport
    echo   - 執行時間: 每天 07:00
    echo   - 執行身分: %USERNAME%
    echo   - 權限: 最高
    echo   - 腳本: run-daily-and-push-scheduled.bat
    echo.
) else (
    echo.
    echo ✗ 排程任務建立失敗！
    echo.
    echo 請確認：
    echo 1. 是否以系統管理員身分執行此腳本
    echo 2. 使用者帳號是否有密碼
    echo.
)

echo.
echo 查詢排程任務：
schtasks /query /tn "DailyWorkReport" /fo LIST /v | findstr /C:"Task To Run" /C:"Run As User" /C:"Status"
echo.

pause

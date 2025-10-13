# 📅 每日自動工作紀錄設定指南

## 功能說明

每天早上 07:00 自動執行，整理昨天的工作紀錄並推送到 GitHub。

---

## 方案一：Windows 工作排程器（推薦）

### 步驟 1：建立 logs 資料夾

```bash
mkdir D:\Personal\Project\work-progress\logs
```

### 步驟 2：設定 Windows 工作排程器

1. **開啟工作排程器**
   - 按 `Win + R`
   - 輸入 `taskschd.msc`
   - 按 Enter

2. **建立基本工作**
   - 點選右側「建立基本工作」
   - 名稱：`每日工作紀錄生成器`
   - 描述：`每天早上 7:00 自動整理昨天的工作紀錄`

3. **設定觸發程序**
   - 選擇「每天」
   - 開始時間：`07:00:00`
   - 每隔：`1` 天

4. **設定動作**
   - 選擇「啟動程式」
   - 程式或指令碼：`D:\Personal\Project\work-progress\scripts\run-daily-report.bat`
   - 起始於（選填）：`D:\Personal\Project\work-progress`

5. **完成設定**
   - 勾選「當按一下完成時，開啟此工作內容的對話方塊」
   - 點選「完成」

6. **進階設定（重要！）**
   - 在「條件」頁籤：
     - **取消勾選**「只有在電腦使用 AC 電源時才啟動工作」
   - 在「設定」頁籤：
     - 勾選「如果工作失敗，每隔以下時間重新啟動：10 分鐘」
     - 勾選「如果要求後工作還在執行，強制停止工作」
     - 停止工作，如果執行時間超過：`1 小時`

### 步驟 3：測試執行

1. 在工作排程器中找到剛建立的工作
2. 右鍵點選「執行」
3. 檢查是否有生成檔案：
   - `daily-reports/2025-10/[日期].md`
   - `daily-reports/2025-10/[日期].json`
4. 檢查 log 檔案：`logs\daily-report.log`

---

## 方案二：GitHub Actions（雲端執行）

如果你的電腦不是 24 小時開機，可以用 GitHub Actions。

### 建立 Workflow 檔案

創建 `.github/workflows/daily-report.yml`：

```yaml
name: Daily Work Report

on:
  schedule:
    # 每天早上 7:00 (UTC 時間要減 8 小時 = 23:00 前一天)
    - cron: '0 23 * * *'
  workflow_dispatch:  # 允許手動觸發

jobs:
  generate-report:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout
      uses: actions/checkout@v3
      with:
        fetch-depth: 0  # 取得完整歷史

    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'

    - name: Install dependencies
      run: |
        pip install gitpython

    - name: Generate Daily Report
      run: |
        python scripts/auto-daily-report.py

    - name: Commit and Push
      run: |
        git config --local user.email "action@github.com"
        git config --local user.name "GitHub Action"
        git add .
        git commit -m "docs: 每日工作紀錄 $(date +%Y-%m-%d)" || exit 0
        git push
```

**限制**：
- GitHub Actions 只能存取 GitHub 上的 repositories
- 無法存取本地的 Gitlab 專案
- **建議使用 Windows 工作排程器**

---

## 方案三：Python Schedule（需要電腦常駐）

如果想要更靈活的排程，可以用 Python schedule 套件。

### 安裝套件

```bash
pip install schedule
```

### 建立常駐程式

創建 `scripts/scheduler.py`：

```python
import schedule
import time
import subprocess

def run_daily_report():
    print(f"執行每日報告生成: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    subprocess.run(['python', 'scripts/auto-daily-report.py'])

# 每天早上 7:00 執行
schedule.every().day.at("07:00").do(run_daily_report)

print("排程器已啟動，每天 07:00 自動執行")
print("按 Ctrl+C 停止\n")

while True:
    schedule.run_pending()
    time.sleep(60)  # 每分鐘檢查一次
```

### 設為開機自動執行

1. 建立批次檔 `start-scheduler.bat`：
```batch
@echo off
cd /d D:\Personal\Project\work-progress
python scripts/scheduler.py
```

2. 將批次檔放到啟動資料夾：
   - `Win + R`
   - 輸入 `shell:startup`
   - 將 `start-scheduler.bat` 的捷徑放進去

---

## 檔案結構

```
work-progress/
├── daily-reports/          # 每日報告
│   ├── 2025-10/
│   │   ├── 2025-10-09.md
│   │   ├── 2025-10-09.json
│   │   ├── 2025-10-10.md
│   │   └── ...
│   ├── 2025-11/
│   └── ...
├── logs/                   # 執行 log
│   └── daily-report.log
└── scripts/
    ├── auto-daily-report.py
    └── run-daily-report.bat
```

---

## 檢查與除錯

### 查看 log

```bash
type D:\Personal\Project\work-progress\logs\daily-report.log
```

### 手動執行測試

```bash
cd D:\Personal\Project\work-progress
python scripts\auto-daily-report.py
```

### 查看工作排程器執行歷史

1. 開啟工作排程器
2. 找到「每日工作紀錄生成器」
3. 點選「歷程記錄」頁籤

---

## 注意事項

1. **電腦需要開機**
   - Windows 工作排程器需要電腦處於開機狀態
   - 如果電腦關機，會在下次開機時補執行（如果有設定）

2. **Git 憑證**
   - 確保 Git 已設定好憑證，可以自動 push
   - 建議使用 SSH key 或 Git Credential Manager

3. **Python 環境**
   - 確保 Python 在系統 PATH 中
   - 測試：在 cmd 輸入 `python --version`

4. **權限問題**
   - 工作排程器建議「不論使用者登入與否均執行」
   - 需要輸入 Windows 密碼

---

## 推薦方案

**建議使用：Windows 工作排程器**

優點：
- ✅ 可存取所有本地 Git repositories（Gitlab + GitHub）
- ✅ 不需要額外套件
- ✅ 穩定可靠
- ✅ 可以設定錯誤重試

缺點：
- ⚠️ 需要電腦在早上 7:00 處於開機狀態

---

📅 設定完成後，每天早上 7:00 會自動執行，無需手動操作！

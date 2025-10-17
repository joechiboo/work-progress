# 工作進度追蹤系統 - 維護文檔

## 📋 系統概述

這是一個自動追蹤 Git commits 並生成工作進度報告的系統，每天早上 07:00 自動執行。

## 🔄 自動化流程

### 每日自動執行（07:05）

**觸發方式**: Windows 工作排程器 → 直接執行 Python 腳本

**工作排程器設定**:
- **程式或指令碼**: `python`
- **新增引數**: `scripts\auto-daily-report.py`
- **開始於**: `D:\Personal\Project\work-progress`

**流程**:
1. 執行 `scripts/auto-daily-report.py`
2. 生成昨天的每日紀錄到 `daily-reports/YYYY-MM/`
3. 彙整所有紀錄到 `public/data/work-log-latest.json`
4. 自動 commit 並 push 到 GitHub
5. GitHub Pages 自動部署更新網頁

**注意**:
- 直接執行 Python 腳本，不透過批次檔
- 輸出直接顯示在 console，不產生本地 log 檔案
- 可透過 GitHub commit 歷史確認執行狀態

## 📁 檔案結構

```
work-progress/
├── daily-reports/          # 每日紀錄（完整資訊）
│   ├── 2025-07/
│   │   ├── 2025-07-15.md   # Markdown 報告
│   │   └── 2025-07-15.json # JSON 資料
│   ├── 2025-08/
│   └── 2025-09/
│
├── public/data/            # 網頁資料源
│   ├── work-log-latest.json              # ✨ 固定檔名（網頁使用）
│   └── work-log-2025-07-15-to-2025-10-14.json  # 帶日期備份
│
├── scripts/                # 腳本檔案
│   ├── auto-daily-report.py       # 主要自動排程腳本
│   ├── daily-report.py            # 手動生成多日報告
│   ├── batch-generate-daily-reports.py  # 批次生成歷史紀錄
│   ├── merge-daily-to-public.py   # 獨立的彙整工具
│   └── collect-all-periods.py     # 時期分析工具
│
├── src/
│   └── App.vue             # 網頁主程式（讀取 work-log-latest.json）
│
└── run-daily-report.bat    # Windows 排程執行入口
```

## 🔧 重要設定

### 1. Author 設定

腳本中的 `AUTHOR` 設定：

```python
AUTHOR = "UCL\\joechiboo"  # 注意雙反斜線
```

**用途**: 過濾出你的 commits，排除其他人的（如 merge commits）

### 2. 路徑設定

```python
GITLAB_PATH = "D:\\Gitlab"           # 公司專案位置
PERSONAL_PATH = "D:\\Personal\\Project"  # 個人專案位置
WORK_PROGRESS_PATH = "D:\\Personal\\Project\\work-progress"
```

### 3. 專案分類邏輯

- **工作專案**: `D:\Gitlab` 下的所有 repos + `uclcloud` 相關專案
- **Side Projects**: `D:\Personal\Project` 下的其他專案（排除 `work-progress` 本身）
- **網頁顯示**: 只顯示工作專案，排除 Side Projects

## 🛠️ 常見維護任務

### 修改 author 名稱

編輯 `scripts/auto-daily-report.py`:

```python
AUTHOR = "你的新名稱"
```

### 修改專案路徑

編輯所有腳本中的路徑常數：
- `GITLAB_PATH`
- `PERSONAL_PATH`
- `WORK_PROGRESS_PATH`

### 修改自動排程時間

1. 打開「工作排程器」
2. 找到對應的任務
3. 修改觸發條件中的時間

### 手動重新生成歷史紀錄

```bash
# 重新生成最近三個月的每日紀錄
python scripts/batch-generate-daily-reports.py

# 手動彙整到網頁
python scripts/merge-daily-to-public.py
```

### 測試自動排程腳本（不推送）

編輯 `scripts/auto-daily-report.py`，註解掉 push 部分：

```python
# subprocess.run(['git', 'push'], check=True)
```

然後執行測試：

```bash
python scripts/auto-daily-report.py
```

## 🔍 故障排查

### 問題 1: 網頁顯示空白或錯誤

**檢查項目**:
1. `public/data/work-log-latest.json` 是否存在？
2. JSON 格式是否正確？
3. 瀏覽器清除快取（Ctrl+Shift+R）
4. GitHub Pages 是否部署成功？

**解決方法**:
```bash
# 重新生成彙整檔案
python -c "from scripts.auto_daily_report import merge_to_public; merge_to_public()"
```

### 問題 2: 自動排程沒執行

**檢查項目**:
1. 工作排程器中任務狀態是否為「就緒」
2. 上次執行結果是否有錯誤碼（如 `0xFFF` 代表找不到檔案）
3. Python 是否在系統 PATH 中（執行 `python --version` 測試）
4. 「開始於」路徑是否正確設定為 `D:\Personal\Project\work-progress`

**確認方式**:
1. 檢查 GitHub 是否有每日自動 commit（格式：`docs: 每日工作紀錄 YYYY-MM-DD`）
2. 檢查 `daily-reports/YYYY-MM/` 是否有最新的報告檔案
3. 手動執行測試：`python scripts\auto-daily-report.py`

**查看排程歷史**:
工作排程器 → 右鍵任務 → 內容 → 歷程記錄

**常見錯誤排除**:

| 錯誤碼 | 原因 | 解決方法 |
|--------|------|----------|
| `0xFFF` | 找不到檔案或路徑錯誤 | 確認「開始於」欄位設定完整路徑 |
| `0x1` | Python 腳本執行失敗 | 手動執行查看錯誤訊息 |
| 無輸出 | 排程未執行 | 確認電腦在排程時間有開機 |

### 問題 3: 某些 commits 沒被記錄

**可能原因**:
1. Author 名稱不符（檢查 `git log --all --format="%an|%ae"`）
2. Commit 是 merge commit（被過濾掉）
3. Repo 不在掃描路徑內

**檢查 author**:
```bash
cd D:\Gitlab\lisweb
git log --all --format="%an|%ae" | grep joechiboo | sort -u
```

### 問題 4: 推送失敗

**可能原因**:
1. Git 認證過期
2. 網路問題
3. 衝突

**解決方法**:
```bash
cd D:\Personal\Project\work-progress
git status
git pull
git push
```

## 📊 資料格式說明

### 每日紀錄格式 (daily-reports/*.json)

```json
{
  "date": "2025-10-14",
  "weekday": "二",
  "work_projects": [
    {
      "name": "lisweb",
      "commits": [...],
      "count": 17
    }
  ],
  "side_projects": [...],
  "summary": {
    "workCommits": 17,
    "sideCommits": 5,
    "totalCommits": 22
  }
}
```

### 網頁資料格式 (public/data/work-log-latest.json)

```json
{
  "period": {
    "start": "2025-07-15",
    "end": "2025-10-14",
    "days": 92,
    "weeks": 13.1
  },
  "author": "UCL\\joechiboo",
  "summary": {
    "totalCommits": 553,
    "projectCount": 7,
    "dailyAverage": 6.0
  },
  "projects": [
    {
      "name": "lisweb",
      "totalCommits": 241,
      "commits": [...]
    }
  ]
}
```

**注意**: 只包含工作專案，不含 Side Projects

## 🚨 重要注意事項

### 1. 不要手動修改生成的檔案

所有 `daily-reports/` 和 `public/data/` 下的檔案都是自動生成的，手動修改會被覆蓋。

### 2. Git 認證

系統依賴 Git 的認證狀態，確保：
- SSH Key 或 Personal Access Token 正常
- 認證不會過期（或設定為長期有效）

### 3. 路徑分隔符號

Windows 路徑需使用雙反斜線：
```python
"D:\\Gitlab"  # ✅ 正確
"D:\Gitlab"   # ❌ 錯誤（會被解析為跳脫字元）
```

### 4. 編碼問題

所有檔案使用 UTF-8 編碼：
```python
with open(file, 'w', encoding='utf-8') as f:
```

### 5. 備份

建議定期備份：
- `daily-reports/` 資料夾
- `public/data/` 帶日期的檔案

## 📝 腳本說明

### auto-daily-report.py（核心腳本）

**功能**:
1. 生成昨天的每日紀錄
2. 彙整所有紀錄到網頁資料
3. 自動 commit & push

**執行時機**: 每天早上 07:00

**關鍵函數**:
- `get_commits_for_date()`: 取得特定日期的 commits
- `generate_daily_report()`: 生成單日報告
- `merge_to_public()`: 彙整成網頁格式
- `git_commit_and_push()`: 推送到 GitHub

### batch-generate-daily-reports.py

**功能**: 批次生成歷史紀錄（用於重建或補齊資料）

**使用時機**:
- 初次設定系統
- 修改 author 後重新生成
- 資料遺失需要重建

### merge-daily-to-public.py

**功能**: 單獨執行彙整功能

**使用時機**:
- 只想更新網頁資料，不生成新的每日紀錄
- 測試彙整邏輯

## 🔗 相關連結

- **GitHub Repo**: https://github.com/joechiboo/work-progress
- **線上網頁**: https://joechiboo.github.io/work-progress/
- **工作排程器路徑**: 電腦管理 → 系統工具 → 工作排程器

## 📞 聯絡資訊

如有問題，請檢查：
1. 這份維護文檔
2. GitHub Issues
3. Git commit history（查看歷史修改）

## 🔧 2025-10-17 排程設定變更

### 變更內容
- **從批次檔改為直接執行 Python**
  - 舊設定：執行 `run-daily-report.bat`
  - 新設定：直接執行 `python scripts\auto-daily-report.py`

### 變更原因
- 批次檔在 Git Bash 環境中執行異常
- 簡化執行流程，減少中間層
- 避免路徑和環境變數問題

### 優缺點

**優點**:
- ✅ 設定簡單直接
- ✅ 減少故障點
- ✅ 執行穩定

**缺點**:
- ❌ 不產生本地 log 檔案（`logs/daily-report.log`）
- ❌ 需要透過 GitHub commit 歷史確認執行狀態

### 如需本地 log

如果需要本地 log 檔案記錄，可改回使用批次檔：

**排程設定**:
- **程式或指令碼**: `cmd.exe`
- **新增引數**: `/c "D:\Personal\Project\work-progress\scripts\run-daily-report.bat"`
- **開始於**: `D:\Personal\Project\work-progress`

批次檔會將所有輸出導向到 `logs/daily-report.log`。

---

**最後更新**: 2025-10-17
**版本**: v1.1
**維護者**: joechiboo

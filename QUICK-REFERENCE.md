# 🚀 快速參考卡片

## 📌 日常使用

### 自動模式（無需操作）
- ⏰ **每天早上 07:00** 自動執行
- 📝 自動生成昨天的工作紀錄
- 🌐 自動更新網頁

### 查看結果
- 🌍 線上網頁: https://joechiboo.github.io/work-progress/
- 📂 每日紀錄: `daily-reports/2025-10/2025-10-15.md`

---

## 🔧 快速指令

### 手動執行（測試用）
```bash
# 生成昨天的紀錄並推送
python scripts/auto-daily-report.py

# 只彙整資料（不生成新紀錄）
python scripts/merge-daily-to-public.py

# 重新生成最近三個月的歷史紀錄
python scripts/batch-generate-daily-reports.py
```

### 查看 Git 狀態
```bash
cd D:\Personal\Project\work-progress
git status
git log --oneline -5
```

### 檢查工作排程器
- 開始 → 搜尋「工作排程器」
- 找到對應的任務
- 查看「歷程記錄」

---

## ⚙️ 重要設定

### Author 名稱
```python
# scripts/auto-daily-report.py
AUTHOR = "UCL\\joechiboo"
```

### 專案路徑
```python
GITLAB_PATH = "D:\\Gitlab"
PERSONAL_PATH = "D:\\Personal\\Project"
```

### 網頁資料檔案
```
public/data/work-log-latest.json  ← 固定檔名（網頁使用）
```

---

## 🆘 常見問題

### ❌ 網頁顯示錯誤
1. 清除瀏覽器快取（Ctrl+Shift+R）
2. 檢查 `public/data/work-log-latest.json` 是否存在
3. 等待 GitHub Pages 部署完成（1-2 分鐘）

### ❌ 某些 commits 沒記錄到
1. 檢查 Author 名稱是否正確
2. 確認 Repo 在掃描路徑內
3. Merge commits 會被過濾掉

### ❌ 自動排程沒執行
1. 檢查工作排程器任務狀態
2. 確認 `run-daily-report.bat` 路徑正確
3. 查看工作排程器的「歷程記錄」

### ❌ Git 推送失敗
```bash
cd D:\Personal\Project\work-progress
git pull
git push
```

---

## 📊 快速統計

### 查看今天會生成的紀錄
```bash
cd D:\Gitlab\lisweb
git log --author="UCL\joechiboo" --since="昨天 00:00" --until="昨天 23:59" --oneline
```

### 查看本週統計
```bash
cd D:\Gitlab\lisweb
git log --author="UCL\joechiboo" --since="1 week ago" --oneline | wc -l
```

---

## 📁 重要檔案位置

| 類型 | 位置 | 說明 |
|------|------|------|
| 網頁資料 | `public/data/work-log-latest.json` | 固定檔名，網頁使用 |
| 每日紀錄 | `daily-reports/YYYY-MM/*.{md,json}` | 完整的每日記錄 |
| 排程腳本 | `scripts/auto-daily-report.py` | 主要自動化腳本 |
| 排程入口 | `run-daily-report.bat` | Windows 排程執行 |
| 網頁程式 | `src/App.vue` | 網頁前端主程式 |

---

## 🔗 相關連結

- 📖 [完整維護文檔](MAINTENANCE.md)
- 🏠 [README](README.md)
- 🌐 [線上網頁](https://joechiboo.github.io/work-progress/)
- 💻 [GitHub Repo](https://github.com/joechiboo/work-progress)

---

## 💡 小提示

1. **備份重要**: 定期備份 `daily-reports/` 資料夾
2. **不要手動修改**: 生成的檔案會被覆蓋
3. **檢查 Git 認證**: 確保 SSH Key 或 Token 有效
4. **路徑用雙反斜線**: `"D:\\Gitlab"` 而非 `"D:\Gitlab"`
5. **檔案編碼 UTF-8**: 避免中文亂碼

---

**最後更新**: 2025-10-15
**快速求助**: 查看 [MAINTENANCE.md](MAINTENANCE.md) 的故障排查章節

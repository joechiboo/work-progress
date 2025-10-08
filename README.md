# 📊 工作進度追蹤系統

自動收集 Git commit 紀錄，產生視覺化工作報告的 Web 應用程式。

**線上展示**: [https://joechiboo.github.io/work-progress/](https://joechiboo.github.io/work-progress/)

## ✨ 功能特色

✅ 自動抓取多個 Git repo 的 commit 紀錄
✅ 智能分類與統計（功能開發、錯誤修正、重構等）
✅ 時間區間篩選
✅ 視覺化 Dashboard 與分類統計
✅ 純前端 Vue 應用，無需後端

## 快速開始

### 1. 安裝依賴

```bash
npm install
```

### 2. 收集 Git Commit 紀錄

從 `D:\Gitlab` 底下所有專案抓取指定時間範圍的 commits：

```bash
# 抓取最近 3 週的紀錄
npm run collect -- --since="2024-09-17" --until="2024-10-08"

# 抓取所有紀錄
npm run collect

# 指定輸出檔名
npm run collect -- --since="2024-09-17" --until="2024-10-08" --output="my-work-log.json"
```

生成的 JSON 會儲存在 `data/` 目錄。

### 3. 啟動 Web 介面

```bash
npm run dev
```

開啟瀏覽器訪問 http://localhost:5173

### 4. 使用介面

- 自動載入工作紀錄 JSON
- 使用時間區間篩選器調整日期範圍
- 查看專案統計與 commit 詳情
- 展開查看每個專案的 commit 列表

## 📂 專案結構

```
work-progress/
├── public/
│   └── data/                 # 工作紀錄 JSON（會被複製到 dist/）
├── docs/                     # 文檔
│   └── deploy.md            # 部署說明
├── scripts/
│   └── collect-commits.js   # Git commit 收集腳本
├── src/
│   ├── App.vue              # 主應用程式
│   ├── main.js              # 進入點
│   └── style.css            # 全域樣式
├── .github/workflows/
│   └── deploy.yml           # GitHub Actions 自動部署
├── index.html
├── package.json
└── vite.config.js
```

## 配置說明

編輯 `scripts/collect-commits.js` 的 `CONFIG` 修改設定：

```javascript
const CONFIG = {
  gitlabPath: 'D:\\Gitlab',        // Git repos 所在路徑
  author: 'UCL\\joechiboo',        // Git author 名稱
  outputDir: './data',             // 輸出目錄
  // ...
};
```

## JSON 資料格式

參考 `data/work-log-2024-09-17-to-10-08.json` 範例檔案。

基本結構：

```json
{
  "period": {
    "start": "2024-09-17",
    "end": "2024-10-08"
  },
  "author": "UCL\\joechiboo",
  "summary": {
    "totalCommits": 130,
    "projectCount": 3
  },
  "projects": [
    {
      "name": "專案名稱",
      "totalCommits": 100,
      "commits": [...]
    }
  ]
}
```

## 🚀 部署

專案使用 GitHub Actions 自動部署到 GitHub Pages。

```bash
# 建置生產版本
npm run build

# 預覽生產版本
npm run preview
```

詳細部署步驟請參考 [docs/deploy.md](docs/deploy.md)。

## 🛠️ 技術棧

- **Vue 3** - 前端框架
- **Vite** - 建置工具
- **Tailwind CSS** - 樣式框架
- **Day.js** - 日期處理
- **GitHub Actions** - CI/CD 自動部署

## 📸 預覽

![工作進度追蹤系統](https://via.placeholder.com/800x450.png?text=Work+Progress+Dashboard)

## 📝 使用場景

- 📋 撰寫週報、月報
- 🎯 績效評估與里程碑追蹤
- 📊 團隊貢獻度分析
- 🔍 個人工作回顧

## License

MIT

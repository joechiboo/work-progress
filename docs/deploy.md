# 部署到 GitHub Pages

## 自動部署設定（推薦）

使用 GitHub Actions 自動建置和部署。

### 1. 啟用 GitHub Pages

1. 前往你的 GitHub repo: `https://github.com/joechiboo/work-progress`
2. 點選 **Settings** > **Pages**
3. Source 選擇 **GitHub Actions**

### 2. 推送程式碼

```bash
git add .
git commit -m "Add GitHub Actions deployment"
git push origin main
```

### 3. 等待部署完成

- 前往 **Actions** 頁籤查看部署進度
- 成功後會顯示綠色勾勾
- 訪問網站: `https://joechiboo.github.io/work-progress/`

## 部署流程

每次推送到 `main` 分支時：

1. GitHub Actions 自動觸發
2. 安裝依賴套件 (`npm ci`)
3. 建置專案 (`npm run build`)
4. 部署 `dist/` 資料夾到 GitHub Pages

## 本地建置測試

```bash
# 建置
npm run build

# 預覽建置結果
npm run preview
```

## Vite 配置說明

`vite.config.js` 中的 `base: '/work-progress/'` 確保資源路徑正確。

如果部署到 `joechiboo.github.io`（使用者/組織頁面），請改為：

```js
export default defineConfig({
  plugins: [vue()],
  base: '/'
})
```

## 疑難排解

### 部署失敗

1. 檢查 Actions 頁籤中的錯誤訊息
2. 確認 Pages 設定為 "GitHub Actions"
3. 確認 workflow 檔案存在於 `.github/workflows/deploy.yml`

### 404 錯誤

1. 檢查 `base` 配置是否正確
2. 確認部署已完成（Actions 顯示綠色）
3. 等待幾分鐘讓 CDN 更新

### 資料檔案載入失敗

確認 JSON 檔案放在 `public/data/` 資料夾中，這樣建置時會自動複製到輸出目錄。

## 更新部署

只需推送到 main 分支即可：

```bash
git add .
git commit -m "Update work progress"
git push
```

## 自訂網域（選用）

1. Settings > Pages > Custom domain
2. 輸入你的網域名稱
3. 等待 DNS 驗證完成

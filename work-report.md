# 📊 您的工作成果（UCL\\joechiboo）- 開始 至 今天

## 📈 總覽統計

* **WebApiService**: 1 次提交 (0%)
* **SyncLisData**: 21 次提交 (4%)
* **LocalPrintHttpService**: 4 次提交 (1%)
* **lisweb**: 374 次提交 (67%)
* **NotificationPlatform**: 3 次提交 (1%)
* **Data2Cloud**: 19 次提交 (3%)
* **ucbio**: 18 次提交 (3%)
* **ucl**: 1 次提交 (0%)
* **FalconCopy**: 37 次提交 (7%)
* **ReportHtmlSync**: 32 次提交 (6%)
* **FOBT**: 2 次提交 (0%)
* **FoodAllergyTestReport**: 1 次提交 (0%)
* **WebOrderArchive**: 4 次提交 (1%)
* **分單系統**: 1 次提交 (0%)
* **Back**: 22 次提交 (4%)
* **Front**: 22 次提交 (4%)
* **總計**: 562 次有效提交

## 🎯 WebApiService 專案成果（1 commits）

### 1. 其他重要功能

**1 次提交**

#### 其他 (1)

* 這麼一大包，但只用到小小的部分 斟酌


## 🎯 SyncLisData 專案成果（21 commits）

### 1. 效能優化 ⚡ (2025-05-05 至 2025-10-08)

**2 次提交**

#### 查詢優化 (2025-05-05)

* 加入 config 控制是否需顯示 sql 幫助排查問題, 調整轉入醫令簽收條件

### 2. FalconCopy 資料同步 🔄 (2025-03-14 至 2025-04-09)

**2 次提交**

#### 同步邏輯 (2025-03-14 至 2025-04-09)

* 1. 加入參數可以控制同步時間長度 2. ※ 重大改動 ※ 假設：同一人同一天只會有一個相同的檢驗項目 > 用於 從 Prd 環境 更新檢驗值至 Test 環境
* 新增 StepIV. 將正式庫的ORD_DLT 同步至 測試環境的 ORD_DTL

### 3. 其他重要功能

**17 次提交**

#### 錯誤修正 (3)

* 修正 CHKINDATE 欄位 NULL 處理，調整富盈模式為僅保留 Ord > Blg
* fix 重複寫入 TNO
* 修正回傳值 L_RCODE

#### 其他 (13)

* 1. 醫令轉入條件調整，應該不管有無簽收都要轉入 2. 更新狀態 method 擴充，並調整流程，醫令轉入完 要更新為 "P"
* 調整成一致條件，避免意外
* UpdateLISDATAStatus include RECEDATE
* HCLITF.P_ORDH 有放 SEQNO
* 解決套餐問題
* ... 以及其他 8 項

#### 功能開發 (1)

* 新增參數控制轉入醫令邏輯


## 🎯 LocalPrintHttpService 專案成果（4 commits）

### 1. 其他重要功能

**4 次提交**

#### 其他 (2)

* 拔掉 time sleep 讓他更順暢
* 拆分 QRCode & tno

#### 功能開發 (1)

* 1. 新增 QRCode 列印模式 2. 切一個 function 讓以後中文字可以輸出異體字 3. 增加uri註解幫助以後測試

#### 錯誤修正 (1)

* 預設不啟動富盈模式 PID支援中文傳入 嘗試解決異體字 a. TSCLIB_DLL.windowsfontU b. 若遇到 bug (text[0] == 0) 的情況 call 舊的  TSCLIB_DLL.windowsfont


## 🎯 lisweb 專案成果（374 commits）

### 1. 效能優化 ⚡ (2025-03-18 至 2025-10-08)

**18 次提交**

#### 查詢優化 (2025-08-26 至 2025-09-26)

* 修正 SQL 查詢中缺少 TIVD_VALUE 轉換 TEXTVALUE 的 JOIN 邏輯
* 修復 AdminConfirm API 確認狀態無法正確顯示的問題
* 優化 PrintLT277 效能 - 將片語轉換和 FLAG 判斷邏輯移至 SQL 層
* 新增 COLLECTOR_ROUTES 表結構修正 SQL 腳本
* 1.  CASE HORD_DTL.OD_TR_RANGE WHEN 'MRR' THEN OD_MRR_DESC ELSE OD_TR_RANGE END OD_TR_RANGE 2. 順便處理 sql injection

### 2. Push 通知系統 🔔 (2025-06-23 至 2025-10-08)

**51 次提交**

#### 診斷工具 (2025-10-07 至 2025-10-08)

* 診斷區塊改用頁籤切換 Push 通知和 PWA 安裝
* 增強 Push 通知診斷功能，添加詳細狀態檢查
* 將 Push 通知訂閱和診斷區塊移至頁面底部
* 將 Push 通知診斷區塊改為可收合
* 增強 Push 通知診斷工具
* ... 以及其他 1 項改進

#### 核心實作 (2025-10-02 至 2025-10-08)

* 更新 Service Worker 快取版本並加入 PWA 卡片診斷日誌
* 訂閱按鈕永久顯示，並優化 iOS 18 設定指引
* 修正 iPhone 看不到訂閱按鈕的問題
* Update VAPID key generation to use internal API
* Add VAPID key generation guide
* ... 以及其他 12 項改進

#### iOS 支援 (2025-10-07)

* 優化 iOS 18 的 Push Notification 設定指引

#### 文檔與優化 (2025-10-07)

* 行政人員取消收檢時發送 Web Push 通知

#### 功能完善 (2025-10-02 至 2025-10-03)

* Refactor notification guide to focus on Web Push only
* Add email notification testing and improve logging
* 新增收檢登記 Email 和 Push 通知功能

### 3. 收檢系統 ⭐ (2025-05-15 至 2025-10-03)

**24 次提交**

#### 系統重構 (2025-09-15 至 2025-10-03)

* 優化手機版收檢查詢互動體驗
* [LT257] 優化 GetPhoneList 查詢效能 - 12秒降至1秒
* 優化收檢系統顯示和交互功能
* 收檢系統 v2.0 完整重構與UI優化
* 簡化收檢系統架構，移除複雜關聯表
* ... 以及其他 1 項改進

#### 行政確認功能 (2025-09-25)

* 修正確認狀態更新問題及收檢員名稱格式

#### 收檢員維護 (2025-05-15 至 2025-09-25)

* 移除收檢員欄位的電話號碼顯示
* 修正收檢登記路線 ID 傳遞問題
* 完成收檢系統和收檢員管理功能
* LT257 聯絡人資訊新增電話號碼顯示
* Merge branch 'main' into LT257電話通報
* ... 以及其他 2 項改進

#### 代班功能 (2025-09-25)

* 修復代班功能查詢與指派邏輯

### 4. BT201 申報畫面智能化 💼 (2025-04-29 至 2025-10-01)

**20 次提交**

#### 自動化功能 (2025-05-09 至 2025-09-18)

* 新增 BT201 病歷號自動帶出個資功能
* BT201 醫師欄位自動帶入上一單同診所醫師功能
* BT201 申報畫面預防保健代號自動填入功能
* Merge branch 'main' into BT201醫師欄位僅顯示該單位醫師
* Merge branch 'main' into BT201醫師欄位僅顯示該單位醫師

### 5. FalconCopy 資料同步 🔄 (2025-05-13 至 2025-09-22)

**4 次提交**

### 6. 其他重要功能

**257 次提交**

#### 功能開發 (50)

* 完成 PWA 診斷頁籤並移除上方卡片
* 新增精美的 PWA 安裝提示卡片
* 在診斷區塊中加入 PWA 安裝教學
* 實作 Progressive Web App (PWA) 支援
* 更新 SigninRepository 登入相關功能
* ... 以及其他 45 項

#### 錯誤修正 (50)

* 修正瀏覽器類型偵測邏輯
* 修正代班按鈕點擊無反應的問題
* Remove NLog debug statements
* Reactivate disabled subscriptions when re-subscribing
* Convert collection view files to UTF-8 with BOM to fix Chinese character encoding
* ... 以及其他 45 項

#### 重構 (6)

* Standardize route name mapping to zero-padded format
* Use internal SMTP settings as default
* Reorganize Service files into Services folder
* 重新整理 SchemaModify 資料夾架構
* 重構一下
* ... 以及其他 1 項

#### 其他 (141)

* Reorganize HomeController and add httpErrors PassThrough
* 清理多餘的 console.log 調試訊息
* 移除 todo.txt 檔案並清理多餘的 console.log
* 砍掉 todo
* resolve merge conflict: keep simplified schema version
* ... 以及其他 136 項

#### 配置 (5)

* resolve: 解決 .claude/settings.local.json 衝突
* config 怎麼設定有問題
* Auto Verification Control Default Value 9 Block All 檢查了台北的工作站設定，全部都是 9
* 加個選項控制身分證隱藏
* 預設不隱藏 (若Debtor_detail 沒設定)

#### 文檔 (3)

* 調整金色換成灰色，說金色太明顯 調整F2 說明 按鈕點姓名容易誤按，調整成 checkbox
* 週邊 table 砍一砍，加上文檔說明
* ## 💡 調整說明 / Description

#### 測試 (1)

* 不知道會不會有很多可怕的影響 乍看之下只有 TestGroupRepository/WorkStationRepository 會用

#### 樣式 (1)

* 1. 調整列印模式的 CSS, 不必要的元素隱藏起來 2. 增加參數傳入機制，可以直接顯示, 不需輸入 3. 增加是否顯示單號功能 4. 可選擇字型大小


## 🎯 NotificationPlatform 專案成果（3 commits）

### 1. 其他重要功能

**3 次提交**

#### 其他 (3)

* 不要再寄給我了
* 加入 Trigger 專案, 可以將例行性Query 整合在這裡
* 第一階段：主體 EmailService 根據 EmailQueue table 中的任務寄信


## 🎯 Data2Cloud 專案成果（19 commits）

### 1. 效能優化 ⚡ (2025-09-02 至 2025-09-03)

**2 次提交**

### 2. FalconCopy 資料同步 🔄 (2025-08-27)

**1 次提交**

### 3. 其他重要功能

**16 次提交**

#### 功能開發 (8)

* 增強過濾階段的日誌記錄機制
* 完成剩餘文檔的更新以反映最新系統架構
* 重構資料處理架構 - 移除臨時表機制並修正memberid欄位映射
* 修復測試並新增 DatabaseService 單元測試和連接字串加密
* 實作整合處理模式 - 自動偵測新用戶並處理昨日審核報告
* ... 以及其他 3 項

#### 文檔 (1)

* 更新文檔以反映雙模式執行架構和最新系統狀況

#### 錯誤修正 (5)

* 改善補傳模式和正常模式的 log 訊息，避免重複執行驗證機制
* resolve merge conflict in settings
* 修正補傳模式的資料欄位對應，確保與正常模式一致
* 修正 goodsProvider 使用原始 testcode 而不是對應的 GoodsID
* 修正 AllGoods 對應邏輯，使用正確的 GoodsID 取代原始 testcode

#### 其他 (2)

* update settings on main branch
* update todo and settings before branch merge


## 🎯 ucbio 專案成果（18 commits）

### 1. 效能優化 ⚡ (2025-03-22)

**1 次提交**

### 2. 其他重要功能

**17 次提交**

#### 其他 (16)

* 增加 ISO 27001 證書
* 文字調整 from 文軒
* 文字調整
* 名稱調整
* 中文描述調整
* ... 以及其他 11 項

#### 功能開發 (1)

* 1. SEO meta 更新 2. 圖片更新(解析度提升) 3. 新增放大圖片功能 4. 新增說明書下載功能


## 🎯 ucl 專案成果（1 commits）

### 1. 其他重要功能

**1 次提交**

#### 其他 (1)

* 初始化專案


## 🎯 FalconCopy 專案成果（37 commits）

### 1. FalconCopy 資料同步 🔄 (2025-09-30 至 2025-10-09)

**12 次提交**

#### 同步邏輯 (2025-09-30 至 2025-10-09)

* 新增完整的機制說明文件和重開機檢查清單
* pat_resulth 每個 order_no 只保留最大 trx_num 的記錄
* 加強整單同步流程的日誌追蹤
* 整合 PAT_RESULTD 同步到 SyncResultHeaderAsync
* 改為串行執行 PAT_RESULTH 和 PAT_RESULTD 同步
* ... 以及其他 6 項改進

#### 資料遷移 (2025-10-07)

* 更新桃園遷徙專案：完成全量遷移並更新文檔

### 2. 效能優化 ⚡ (2025-09-10 至 2025-10-08)

**15 次提交**

#### 查詢優化 (2025-10-07 至 2025-10-08)

* 新增 Oracle 重置腳本，用於重新同步被誤刪的單號
* 新增清理重複 pat_resulth 記錄的 SQL 文件
* 修正 MSSQL 表的欄位名稱錯誤
* 移除正常執行時的 SQL 日誌，只在錯誤時顯示
* 在 SQL 錯誤訊息中顯示完整 SQL 語句
* ... 以及其他 4 項改進

### 3. 其他重要功能

**10 次提交**

#### 其他 (2)

* 繞過 pat_resulthx 的有問題觸發器，直接寫入 pat_resulth
* 簡化日誌輸出，只顯示重要訊息

#### 錯誤修正 (2)

* 修正 pat_resulth 複合主鍵為 (order_no, test_code)
* 精簡日誌輸出並修正欄位長度限制

#### 功能開發 (3)

* 加強刪除操作的日誌追蹤
* 新增 .gitignore 並移除已追蹤的 bin/obj 檔案
* 新增 Claude Code 語音提示設定說明文件

#### 文檔 (2)

* 清理根目錄的重複文件
* 整理文件目錄結構

#### 配置 (1)

* 更新 Claude Code 權限設定


## 🎯 ReportHtmlSync 專案成果（32 commits）

### 1. FalconCopy 資料同步 🔄 (2025-10-08)

**1 次提交**

### 2. 效能優化 ⚡ (2025-09-05 至 2025-09-06)

**7 次提交**

#### 查詢優化 (2025-09-06)

* Add comprehensive SQL analysis tools for processing time monitoring

### 3. 其他重要功能

**24 次提交**

#### 錯誤修正 (4)

* Fix URL configuration and add error logging for deployment
* Fix connection string decryption issues and improve error handling
* Fix compilation errors after database architecture optimization
* Fix corrupted connection string in appsettings.json

#### 樣式 (2)

* Add .gitignore and remove build artifacts from repository
* Add deployment guide and publish build

#### 功能開發 (2)

* Merge feature/deployment-complete into master
* Add comprehensive project documentation

#### 其他 (8)

* Add Claude settings
* Implement optimal priority-based record processing with deduplication
* Optimize database query architecture for complete record processing
* Correct 2-year report processing timeline based on actual system capacity
* Update batch sizes for enhanced processing capacity
* ... 以及其他 3 項

#### 文檔 (6)

* Update project documentation and maintenance queries
* Add logging guide to documentation index
* Add comprehensive logging and monitoring guide
* Replace real connection strings with example placeholders for security
* Update README.md with comprehensive project documentation
* ... 以及其他 1 項

#### 重構 (2)

* Restructure documentation with Chinese filenames and sequence numbers
* Restructure documentation with organized directory layout


## 🎯 FOBT 專案成果（2 commits）

### 1. 其他重要功能

**2 次提交**

#### 其他 (2)

* 這個 query  原本是 ORD_DTL & ORD_HDR 調整成 ORD_DTL & HORD_HDR 只有差 一個 column 是 OD_UPDATE_BY 改成 抓 EVENTLOG
* clone project


## 🎯 FoodAllergyTestReport 專案成果（1 commits）

### 1. 其他重要功能

**1 次提交**

#### 功能開發 (1)

* 這個版本印出去完成日期是正確的


## 🎯 WebOrderArchive 專案成果（4 commits）

### 1. 其他重要功能

**4 次提交**

#### 其他 (2)

* 亂砍一通，完蛋啦
* 專案建置

#### 測試 (1)

* 整合了測試專案，但好像 failed 了

#### 功能開發 (1)

* 主體架構實作


## 🎯 分單系統 專案成果（1 commits）

### 1. 其他重要功能

**1 次提交**

#### 其他 (1)

* 加入 dll, 不然專案跑不起來


## 🎯 Back 專案成果（22 commits）

### 1. 效能優化 ⚡ (2025-02-11)

**1 次提交**

#### 查詢優化 (2025-02-11)

* OS 遠端登入太慢了，再寫一個 SQL Server

### 2. 其他重要功能

**21 次提交**

#### 錯誤修正 (2)

* Merge branch 'main' into 修復門診表功能
* fix 儲存失敗

#### 其他 (13)

* 1. 門診列表，上午排在上面、下午排下面，比較直覺 2. Weekday 0-4 不太直覺, 改成 1-7 3. 增加 預設門診 model 狀態 Status 直接把假日 預設，這樣邏輯比較簡單 4. 因應可寫入未安排的診次，調整前端 json
* wwwroot
* 專案重整
* Install-Package NLog.Database
* 增加db類型的寫入
* ... 以及其他 8 項

#### 功能開發 (4)

* 新增門診表維護功能
* 1. 預約新增看診類別(一般/通訊) 2. 截圖新增 SMTP 至 user email
* 新增Controller 供同意書圖片上傳
* 新增影像api

#### 測試 (1)

* 整合測試專案

#### 樣式 (1)

* 後台維護介面


## 🎯 Front 專案成果（22 commits）

### 1. 效能優化 ⚡ (2025-02-05)

**1 次提交**

### 2. 其他重要功能

**21 次提交**

#### 功能開發 (3)

* 新增頁面，以及調整相關元件
* Merge branch 'feat/newebpaylink' of https://gitlab.ucl.com.tw/ucl/his/upc-website-frontend into 視訊看診同意書
* 同意書更新 傳送Email至後端 預約新增欄位看診類別

#### 其他 (17)

* 學歷、門診時間更新
* 調整日期格式驗證
* 增加驗證機制 validateForm
* 按鈕們擋到簽名了
* 將照片上傳至伺服器
* ... 以及其他 12 項

#### 錯誤修正 (1)

* 修復api路徑


## 📊 工作分析

### 提交密度

* 最高峰: 2025-10-02 (35 commits) 🔥
* 第二峰: 2025-10-08 (32 commits)

### 功能分類

* 其他: 254 (45%)
* 功能開發: 150 (27%)
* 錯誤修正: 103 (18%)
* 文檔: 18 (3%)
* 重構: 17 (3%)
* 配置: 8 (1%)
* 測試: 4 (1%)
* 樣式: 4 (1%)
* 效能優化: 4 (1%)

---

📅 報告生成時間: 2025-11-24

製表日期： 115 年 02 月 09 日                  紀錄編號：4059-202602-01
部門名稱：資訊部                              填表人員：紀伯喬

變更項目：VisionReportHub 報告轉發系統

預定執行期程：自 115 年 02 月 04 日 至 115 年 02 月 09 日止

---

## 變更需求

變更原因及內容說明：

因應多家合作醫療院所使用不同 HIS 廠商系統，檢驗報告需透過各廠商 API 進行轉發。現有作業為個別對接，維護困難且擴充性差，需建立統一的報告轉發中樞系統。

**變更原因：**
1. 合作院所使用不同 HIS 廠商（AlleyPin、Vision、Realsun、Esis 等），各有不同的報告接收格式與 API
2. 現有報告轉發為各自獨立實作，程式碼分散、維護困難
3. 缺乏統一的轉發狀態追蹤與失敗重送機制
4. 無法集中管理各院所的對接設定

**變更內容：**
1. 建立 VisionReportHub 統一轉發中樞
2. 實作多廠商 Adapter 架構：
   - AlleyPin Adapter（含 Token 認證服務）
   - Vision Adapter（XML 格式）
   - Realsun Adapter（XML 格式）
   - Esis Adapter（XML 格式）
3. 資料層建置：
   - MSSQL 資料庫設計（HisVendors、Sites、SiteHisMapping、TransferLogs）
   - Oracle 查詢整合（檢驗結果來源）
4. 功能實作：
   - 手動批次發送與重送 API
   - 轉發統計與歷程記錄
   - PII 遮罩（個資保護）
   - Email 異常通知
   - Serilog 結構化日誌
5. 部署架構：
   - Windows Service 託管
   - Web 管理介面（站點搜尋、重送管理分頁）

**影響範圍：** 新增 TwowayConnection\VisionReportHub 獨立服務

申請人員：紀伯喬

---

## 變更評估

**影響分析：**
- 影響模組：新增獨立 Windows Service + Web 管理介面
- 資料庫：新增 MSSQL 資料庫（4 張資料表）；Oracle 唯讀查詢
- 網路設定：需開放對各 HIS 廠商 API 的網路連線
- 第三方元件：Serilog、各廠商 SDK
- 無需停機，為新增獨立服務
- 備份作業：不適用（新系統）
- 變更失敗處理：停止 Windows Service，移除部署檔案

評估人員：紀伯喬

---

## 變更處理

已依原規劃方式完成變更作業：
1. 多廠商 Adapter 架構開發完成（Phase 5 完成，18+ commits）
2. AlleyPin、Vision、Realsun、Esis 四組 Adapter 測試通過
3. MSSQL 資料庫部署完成
4. Windows Service 託管運作正常
5. Web 管理介面功能驗證通過（站點搜尋、重送管理）
6. PII 遮罩與 Email 通知功能正常

執行人員：紀伯喬

---

## 結果確認

已確認依照原規劃方式執行變更，VisionReportHub 報告轉發系統正常運作，各廠商 Adapter 轉發成功。

確認人員：

安全測試結果：
☒ 無須進行測試

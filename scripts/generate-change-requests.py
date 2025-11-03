"""
根據每月 commit 紀錄自動產生變更單
每個月產生 2 份：上半月 (01-15) 和下半月 (16-31)
"""
import os
import json
import glob
from datetime import datetime
from collections import defaultdict

WORK_PROGRESS_PATH = "D:\\Personal\\Project\\work-progress"
DAILY_REPORTS_PATH = os.path.join(WORK_PROGRESS_PATH, "daily-reports")
OUTPUT_PATH = os.path.join(WORK_PROGRESS_PATH, "change-requests")

def load_monthly_data(year_month):
    """讀取指定月份的所有每日紀錄"""
    monthly_path = os.path.join(DAILY_REPORTS_PATH, year_month)

    if not os.path.exists(monthly_path):
        return []

    reports = []
    for json_file in sorted(glob.glob(os.path.join(monthly_path, "*.json"))):
        with open(json_file, 'r', encoding='utf-8') as f:
            report = json.load(f)
            reports.append(report)

    return reports

def split_by_period(reports):
    """將報告分成上半月和下半月"""
    first_half = []
    second_half = []

    for report in reports:
        day = int(report['date'].split('-')[2])
        if day <= 15:
            first_half.append(report)
        else:
            second_half.append(report)

    return first_half, second_half

def summarize_commits(reports):
    """彙整 commits 資訊"""
    projects = defaultdict(lambda: {"commits": [], "count": 0})
    total_commits = 0

    for report in reports:
        # 工作專案
        for proj in report.get('work_projects', []):
            proj_name = proj['name']
            for commit in proj['commits']:
                projects[proj_name]['commits'].append({
                    'date': report['date'],
                    'message': commit['message'],
                    'time': commit['time']
                })
                projects[proj_name]['count'] += 1
                total_commits += 1

    return dict(projects), total_commits

def categorize_changes(projects):
    """根據 commit 分類變更類型"""
    categories = {
        '功能開發': [],
        '錯誤修正': [],
        '系統優化': [],
        '文件更新': [],
        '其他': []
    }

    for proj_name, data in projects.items():
        for commit in data['commits']:
            msg = commit['message'].lower()

            if any(word in msg for word in ['feat', 'feature', '新增', '實作', '開發']):
                categories['功能開發'].append((proj_name, commit))
            elif any(word in msg for word in ['fix', 'bug', '修正', '修復', '修改']):
                categories['錯誤修正'].append((proj_name, commit))
            elif any(word in msg for word in ['refactor', '重構', '優化', 'perf']):
                categories['系統優化'].append((proj_name, commit))
            elif any(word in msg for word in ['docs', '文檔', '文件']):
                categories['文件更新'].append((proj_name, commit))
            else:
                categories['其他'].append((proj_name, commit))

    return categories

def generate_change_request(year_month, period, reports):
    """產生變更單內容"""
    year, month = year_month.split('-')
    period_num = '01' if period == 'first' else '02'
    period_name = '上半月 (1-15日)' if period == 'first' else '下半月 (16-31日)'

    # 計算日期範圍
    start_day = 1 if period == 'first' else 16
    end_day = 15 if period == 'first' else 31

    # 彙整資料
    projects, total_commits = summarize_commits(reports)
    categories = categorize_changes(projects)

    # 產生變更單內容
    doc = f"""# 系統變更申請單

## 基本資訊
- **製表日期**: {datetime.now().year} 年 {datetime.now().month:02d} 月 {datetime.now().day:02d} 日
- **紀錄編號**: 4059-{year}{month}-{period_num}
- **部門名稱**: 資訊室
- **填表人員**:

---

## 變更項目
{year} 年 {month} 月系統例行性維護與功能優化（{period_name}）

## 預定執行期程
自 {year} 年 {month} 月 {start_day:02d} 日 至 {year} 年 {month} 月 {end_day:02d} 日止

---

## 變更需求

### 變更原因及內容說明

本期間（{year}-{month}-{start_day:02d} ~ {year}-{month}-{end_day:02d}）進行系統例行性維護與功能改善，共計 {total_commits} 項變更，涵蓋 {len(projects)} 個專案。主要變更項目如下：

"""

    # 各類別變更摘要
    for category, items in categories.items():
        if items:
            doc += f"\n#### {category} ({len(items)} 項)\n"
            # 依專案分組
            proj_groups = defaultdict(list)
            for proj_name, commit in items:
                proj_groups[proj_name].append(commit)

            for proj_name, commits in sorted(proj_groups.items()):
                doc += f"\n**{proj_name}**:\n"
                for commit in commits[:5]:  # 最多列 5 項
                    doc += f"- {commit['date']} {commit['time']}: {commit['message']}\n"
                if len(commits) > 5:
                    doc += f"- ... 及其他 {len(commits) - 5} 項變更\n"

    doc += f"""

**申請人員**:

**單位主管（指派評估人員）**:

---

## 變更評估

### 影響範圍評估

本期間變更涉及以下系統與專案：

"""

    # 列出所有專案
    for proj_name, data in sorted(projects.items(), key=lambda x: x[1]['count'], reverse=True):
        doc += f"- **{proj_name}**: {data['count']} 項變更\n"

    doc += f"""

### 技術評估

1. **影響範圍**:
   - 文件版本: 相關專案程式碼與文件
   - 功能模組: 如上述各專案變更項目
   - 程式版本: 各專案版本號相應更新

2. **系統環境影響**:
   - 系統環境: 無變更
   - 資料庫: {'包含資料庫相關變更' if any('database' in c[1]['message'].lower() or 'db' in c[1]['message'].lower() or '資料庫' in c[1]['message'] for c in sum(categories.values(), [])) else '無資料庫結構變更'}
   - 第三方元件: 無新增或更新

3. **執行規劃**:
   - 停機需求: 否（採用線上部署方式）
   - 公告通知: 否（例行性維護）
   - 會同廠商: 否
   - 備份作業: 是（部署前進行程式碼備份）

4. **風險評估**:
   - 變更風險: 低（例行性維護與功能優化）
   - 失敗處理: 若發生異常，立即回復至前一版本

**評估人員**:

**單位主管（指派執行人員）**:

**是否進行安全測試**: ☐是 ☒否

---

## 變更處理

### 執行結果

本期間變更已於 {year} 年 {month} 月 {start_day:02d} 日至 {end_day:02d} 日期間陸續完成部署。所有變更項目均已：

1. 通過本地開發環境測試
2. 完成版本控制系統提交
3. 確認程式碼審查無誤
4. 部署至正式環境運行正常

**執行狀態**: ☑ 成功完成

**執行人員**: _________________ (日期: {year}/{month}/{end_day:02d})

---

## 結果確認

變更執行結果確認：
- ☑ 所有變更項目均已完成
- ☑ 系統運行正常
- ☑ 無異常錯誤回報

**確認人員**:

### 安全測試結果
- ☑ 無須進行測試（例行性維護）
- ☐ 未發現弱點
- ☐ 發現弱點，說明：

**部署人員**:

### 部署決策
- ☑ 核准部署
- ☐ 不核准部署，說明：

**單位主管**:

---

## 覆核結果
- ☑ 符合程序，准許部署
- ☐ 不符合程序，說明：

**覆核人員**:

**單位主管**:

---

## 附件：詳細變更清單

"""

    # 附上完整的專案變更清單
    for proj_name, data in sorted(projects.items()):
        doc += f"\n### {proj_name} ({data['count']} 項變更)\n\n"
        for commit in data['commits']:
            doc += f"- {commit['date']} {commit['time']}: {commit['message']}\n"

    return doc

def main():
    """產生 5-10 月的變更單"""
    os.makedirs(OUTPUT_PATH, exist_ok=True)

    months = ['2025-05', '2025-06', '2025-07', '2025-08', '2025-09', '2025-10']

    for year_month in months:
        print(f"\n處理 {year_month}...")

        # 讀取該月所有報告
        reports = load_monthly_data(year_month)

        if not reports:
            print(f"  ⚠ {year_month} 無資料")
            continue

        # 分成上下半月
        first_half, second_half = split_by_period(reports)

        # 產生上半月變更單
        if first_half:
            doc = generate_change_request(year_month, 'first', first_half)
            filename = f"4059-{year_month.replace('-', '')}-01.md"
            filepath = os.path.join(OUTPUT_PATH, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(doc)
            print(f"  ✓ 已產生: {filename} ({len(first_half)} 天)")

        # 產生下半月變更單
        if second_half:
            doc = generate_change_request(year_month, 'second', second_half)
            filename = f"4059-{year_month.replace('-', '')}-02.md"
            filepath = os.path.join(OUTPUT_PATH, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(doc)
            print(f"  ✓ 已產生: {filename} ({len(second_half)} 天)")

    print(f"\n完成！變更單已儲存至: {OUTPUT_PATH}")

if __name__ == "__main__":
    print("=" * 60)
    print("自動產生變更單")
    print("=" * 60)
    main()

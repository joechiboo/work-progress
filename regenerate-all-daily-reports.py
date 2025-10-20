"""重新產生 2025-07-15 到 2025-10-19 的所有每日報告"""
import sys
import os
sys.path.insert(0, 'scripts')

# 載入函數
exec(open('scripts/auto-daily-report.py', encoding='utf-8').read())

from datetime import datetime, timedelta

start_date = datetime(2025, 7, 15)
end_date = datetime(2025, 10, 19)

current = start_date
total_days = 0
total_work = 0
total_side = 0

print("重新產生所有每日報告...")
print(f"期間: {start_date.date()} 到 {end_date.date()}")
print("=" * 60)

while current <= end_date:
    date_str = current.strftime('%Y-%m-%d')

    # 生成報告
    report = generate_daily_report(date_str)
    markdown = generate_markdown(report)

    # 儲存檔案
    year_month = current.strftime('%Y-%m')
    monthly_folder = f'daily-reports/{year_month}'
    os.makedirs(monthly_folder, exist_ok=True)

    # 儲存 JSON
    json_file = f'{monthly_folder}/{date_str}.json'
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    # 儲存 MD
    md_file = f'{monthly_folder}/{date_str}.md'
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(markdown)

    work = report["summary"]["workCommits"]
    side = report["summary"]["sideCommits"]
    total = work + side

    if total > 0:
        print(f"{date_str}: 工作 {work:2d} + Side {side:2d} = {total:2d}")

    total_days += 1
    total_work += work
    total_side += side

    current += timedelta(days=1)

print("=" * 60)
print(f"完成 {total_days} 天的報告")
print(f"工作專案: {total_work} commits")
print(f"Side Projects: {total_side} commits")
print(f"總計: {total_work + total_side} commits")

print("\n彙整到 public/data...")
merge_to_public()
print("\n完成!")

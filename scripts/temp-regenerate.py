"""臨時腳本：重新生成 10/17-10/22 的報告"""
import sys
import os
from datetime import datetime, timedelta

# 加入 auto-daily-report.py 的路徑
sys.path.insert(0, os.path.dirname(__file__))

# 匯入需要的函數
import importlib.util
spec = importlib.util.spec_from_file_location("auto_daily_report", os.path.join(os.path.dirname(__file__), "auto-daily-report.py"))
auto_daily_report = importlib.util.module_from_spec(spec)
spec.loader.exec_module(auto_daily_report)
generate_daily_report = auto_daily_report.generate_daily_report
generate_markdown = auto_daily_report.generate_markdown
import json

WORK_PROGRESS_PATH = "D:\\Personal\\Project\\work-progress"

# 要重新生成的日期範圍
start_date = datetime(2025, 10, 17)
end_date = datetime(2025, 10, 22)

current = start_date
while current <= end_date:
    date_str = current.strftime('%Y-%m-%d')
    print(f"\n處理 {date_str}...")

    try:
        # 生成報告
        report = generate_daily_report(date_str)
        markdown = generate_markdown(report)

        # 儲存檔案
        year_month = current.strftime('%Y-%m')
        monthly_folder = os.path.join(WORK_PROGRESS_PATH, "daily-reports", year_month)
        os.makedirs(monthly_folder, exist_ok=True)

        # 儲存 Markdown
        md_file = os.path.join(monthly_folder, f"{date_str}.md")
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(markdown)

        # 儲存 JSON
        json_file = os.path.join(monthly_folder, f"{date_str}.json")
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        print(f"  工作: {report['summary']['workCommits']} commits")
        print(f"  Side: {report['summary']['sideCommits']} commits")
        print(f"  ✓ 已儲存: {md_file}")

    except Exception as e:
        print(f"  ✗ 錯誤: {e}")

    current += timedelta(days=1)

print("\n完成!")

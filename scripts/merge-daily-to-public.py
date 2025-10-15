"""
將 daily-reports 資料夾中的每日紀錄彙整到 public/data/work-log-*.json
供網頁使用
"""
import os
import json
from datetime import datetime, timedelta

WORK_PROGRESS_PATH = "D:\\Personal\\Project\\work-progress"
DAILY_REPORTS_PATH = os.path.join(WORK_PROGRESS_PATH, "daily-reports")
PUBLIC_DATA_PATH = os.path.join(WORK_PROGRESS_PATH, "public", "data")

def get_all_daily_reports():
    """讀取所有每日紀錄"""
    all_reports = []

    # 掃描 daily-reports 資料夾
    for year_month in os.listdir(DAILY_REPORTS_PATH):
        folder_path = os.path.join(DAILY_REPORTS_PATH, year_month)
        if not os.path.isdir(folder_path):
            continue

        # 讀取該月份的所有 JSON 檔案
        for filename in os.listdir(folder_path):
            if filename.endswith('.json'):
                file_path = os.path.join(folder_path, filename)
                with open(file_path, 'r', encoding='utf-8') as f:
                    report = json.load(f)
                    all_reports.append(report)

    # 按日期排序
    all_reports.sort(key=lambda x: x['date'])
    return all_reports

def main():
    print("=" * 80)
    print("彙整每日紀錄到 public/data")
    print("=" * 80)

    # 讀取所有每日紀錄
    all_reports = get_all_daily_reports()
    print(f"\n找到 {len(all_reports)} 天的紀錄")

    if not all_reports:
        print("沒有找到任何紀錄")
        return

    # 顯示日期範圍
    start_date = all_reports[0]['date']
    end_date = all_reports[-1]['date']
    print(f"日期範圍: {start_date} ~ {end_date}")

    # 儲存完整紀錄
    output_file = os.path.join(PUBLIC_DATA_PATH, f"work-log-{start_date}-to-{end_date}.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_reports, f, ensure_ascii=False, indent=2)

    print(f"\n已儲存: {output_file}")

    # 統計資訊
    total_work = sum(r['summary']['workCommits'] for r in all_reports)
    total_side = sum(r['summary']['sideCommits'] for r in all_reports)
    print(f"\n統計:")
    print(f"  工作專案: {total_work} commits")
    print(f"  Side Projects: {total_side} commits")
    print(f"  總計: {total_work + total_side} commits")

    print("\n完成!")

if __name__ == "__main__":
    main()

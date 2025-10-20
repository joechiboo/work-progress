"""重新產生 10/18 和 10/19 的報告以包含 Fast-Trivia 和履歷專案"""
import sys
import os
sys.path.insert(0, 'scripts')

# 直接使用腳本中的函數
exec(open('scripts/auto-daily-report.py', encoding='utf-8').read())

# 重新產生 10/18 和 10/19
for date_str in ['2025-10-18', '2025-10-19']:
    print(f'\n重新產生 {date_str} 的報告...')
    report = generate_daily_report(date_str)
    markdown = generate_markdown(report)

    # 儲存檔案
    year_month = '2025-10'
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

    print(f'  工作: {report["summary"]["workCommits"]} commits')
    print(f'  Side: {report["summary"]["sideCommits"]} commits')
    print(f'  已儲存: {json_file}')

print('\n彙整到 public/data...')
merge_to_public()
print('\n完成!')

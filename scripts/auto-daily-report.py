"""
每日自動工作紀錄生成器
在每天早上 07:00 執行，自動整理昨天的工作紀錄
"""
import subprocess
import os
import json
from datetime import datetime, timedelta

GITLAB_PATH = "D:\\Gitlab"
PERSONAL_PATH = "D:\\Personal\\Project"
WORK_PROGRESS_PATH = "D:\\Personal\\Project\\work-progress"
AUTHOR = "UCL\\joechiboo"

def get_git_repos(base_path, max_depth=3):
    """遞迴尋找所有 Git repositories"""
    repos = []
    for root, dirs, files in os.walk(base_path):
        depth = root.replace(base_path, '').count(os.sep)
        if depth >= max_depth:
            dirs[:] = []
            continue
        if '.git' in dirs:
            repos.append(root)
            dirs[:] = []
    return repos

def get_commits_for_date(repo_path, author, date_str):
    """取得特定日期的 commits"""
    try:
        # 先抓全部 commits，包含 author name
        cmd = [
            'git', '-C', repo_path, 'log',
            f'--since={date_str} 00:00',
            f'--until={date_str} 23:59',
            '--format=%an|||%H|||%ai|||%s|||%b',
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')

        commits = []
        for line in result.stdout.strip().split('\n'):
            if not line:
                continue
            parts = line.split('|||')
            if len(parts) >= 4:
                author_name = parts[0].strip()
                # 只保留 UCL\joechiboo 的 commits，排除 merge commits (紀伯喬)
                if author in author_name:
                    commits.append({
                        "hash": parts[1].strip()[:8],
                        "time": parts[2].strip()[11:16],
                        "message": parts[3].strip(),
                        "body": parts[4].strip() if len(parts) > 4 else ""
                    })
        return commits
    except Exception as e:
        return []

def categorize_commit(message):
    """簡易分類"""
    msg_lower = message.lower()
    if any(word in msg_lower for word in ['feat', 'feature', '新增', '實作']):
        return '功能開發'
    elif any(word in msg_lower for word in ['fix', 'bug', '修正', '修復']):
        return '錯誤修正'
    elif any(word in msg_lower for word in ['refactor', '重構', '優化']):
        return '重構'
    elif any(word in msg_lower for word in ['docs', '文檔', '文件']):
        return '文檔'
    else:
        return '其他'

def generate_daily_report(date_str):
    """生成單日報告"""
    gitlab_repos = get_git_repos(GITLAB_PATH)
    personal_repos = get_git_repos(PERSONAL_PATH)

    date_obj = datetime.strptime(date_str, '%Y-%m-%d')

    report = {
        "date": date_str,
        "weekday": ["一", "二", "三", "四", "五", "六", "日"][date_obj.weekday()],
        "work_projects": [],
        "side_projects": [],
        "summary": {
            "workCommits": 0,
            "sideCommits": 0,
            "totalCommits": 0
        }
    }

    # 收集工作專案
    for repo in gitlab_repos:
        proj_name = repo.replace(GITLAB_PATH + "\\", "")
        commits = get_commits_for_date(repo, AUTHOR, date_str)
        if commits:
            report["work_projects"].append({
                "name": proj_name,
                "commits": commits,
                "count": len(commits)
            })
            report["summary"]["workCommits"] += len(commits)

    # 收集個人專案（含 uclcloud）
    for repo in personal_repos:
        proj_name = repo.replace(PERSONAL_PATH + "\\", "")

        # 跳過 work-progress 本身
        if 'work-progress' in proj_name.lower():
            continue

        commits = get_commits_for_date(repo, AUTHOR, date_str)
        if commits:
            # uclcloud 算工作專案
            if 'uclcloud' in proj_name.lower():
                report["work_projects"].append({
                    "name": proj_name,
                    "commits": commits,
                    "count": len(commits)
                })
                report["summary"]["workCommits"] += len(commits)
            else:
                report["side_projects"].append({
                    "name": proj_name,
                    "commits": commits,
                    "count": len(commits)
                })
                report["summary"]["sideCommits"] += len(commits)

    report["summary"]["totalCommits"] = report["summary"]["workCommits"] + report["summary"]["sideCommits"]

    # 排序
    report["work_projects"].sort(key=lambda x: x["count"], reverse=True)
    report["side_projects"].sort(key=lambda x: x["count"], reverse=True)

    return report

def generate_markdown(report):
    """生成單日 Markdown 報告"""
    date = report["date"]
    weekday = report["weekday"]
    work_count = report["summary"]["workCommits"]
    side_count = report["summary"]["sideCommits"]
    total_count = report["summary"]["totalCommits"]

    md = f"# 📅 每日工作紀錄 - {date} (週{weekday})\n\n"

    if total_count == 0:
        md += "🏖️ **休假日或無提交紀錄**\n\n"
        md += f"📅 報告生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        return md

    md += f"**統計**: 工作 {work_count} + Side {side_count} = 總計 {total_count} commits\n\n"
    md += "---\n\n"

    # 工作專案
    if report["work_projects"]:
        md += "## 💼 工作專案\n\n"
        for proj in report["work_projects"]:
            md += f"### {proj['name']} ({proj['count']} commits)\n\n"
            for commit in proj["commits"]:
                category = categorize_commit(commit["message"])
                md += f"- **{commit['time']}** [{category}] {commit['message']}\n"
            md += "\n"

    # Side Projects
    if report["side_projects"]:
        md += "## 🎨 Side Projects\n\n"
        for proj in report["side_projects"]:
            md += f"### {proj['name']} ({proj['count']} commits)\n\n"
            for commit in proj["commits"]:
                category = categorize_commit(commit["message"])
                md += f"- **{commit['time']}** [{category}] {commit['message']}\n"
            md += "\n"

    md += "---\n\n"
    md += f"📅 報告生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"

    return md

def git_commit_and_push(date_str, total_commits):
    """自動 commit 並 push"""
    try:
        os.chdir(WORK_PROGRESS_PATH)

        # git add
        subprocess.run(['git', 'add', '.'], check=True)

        # git commit
        commit_msg = f"docs: 每日工作紀錄 {date_str} ({total_commits} commits)\n\n🤖 自動生成於 {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        subprocess.run(['git', 'commit', '-m', commit_msg], check=True)

        # git push
        subprocess.run(['git', 'push'], check=True)

        return True
    except subprocess.CalledProcessError as e:
        print(f"Git operation failed: {e}")
        return False

def main():
    # 取得昨天的日期
    yesterday = datetime.now() - timedelta(days=1)
    date_str = yesterday.strftime('%Y-%m-%d')

    print(f"========================================")
    print(f"自動生成每日工作紀錄: {date_str}")
    print(f"執行時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"========================================\n")

    # 生成報告
    report = generate_daily_report(date_str)

    print(f"工作專案: {report['summary']['workCommits']} commits")
    print(f"Side Projects: {report['summary']['sideCommits']} commits")
    print(f"總計: {report['summary']['totalCommits']} commits\n")

    # 生成 Markdown
    markdown = generate_markdown(report)

    # 儲存檔案
    daily_folder = os.path.join(WORK_PROGRESS_PATH, "daily-reports")
    os.makedirs(daily_folder, exist_ok=True)

    # 依年月分類
    year_month = yesterday.strftime('%Y-%m')
    monthly_folder = os.path.join(daily_folder, year_month)
    os.makedirs(monthly_folder, exist_ok=True)

    md_file = os.path.join(monthly_folder, f"{date_str}.md")
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(markdown)

    # 儲存 JSON
    json_file = os.path.join(monthly_folder, f"{date_str}.json")
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"Markdown: {md_file}")
    print(f"JSON: {json_file}\n")

    # 自動 commit 和 push
    if report['summary']['totalCommits'] > 0:
        print("正在 commit 並 push 到 GitHub...")
        if git_commit_and_push(date_str, report['summary']['totalCommits']):
            print("成功推送到 GitHub!")
        else:
            print("推送失敗，請手動處理")
    else:
        print("無提交紀錄，跳過 git push")

    print(f"\n完成!")

def merge_to_public():
    """彙整所有每日紀錄到 public/data（輸出網頁需要的彙整格式）"""
    import glob

    print("\n" + "=" * 80)
    print("彙整每日紀錄到 public/data")
    print("=" * 80)

    # 讀取所有每日紀錄
    daily_reports_path = os.path.join(WORK_PROGRESS_PATH, "daily-reports")
    all_reports = []

    for year_month_dir in sorted(glob.glob(os.path.join(daily_reports_path, "*"))):
        if not os.path.isdir(year_month_dir):
            continue

        for json_file in sorted(glob.glob(os.path.join(year_month_dir, "*.json"))):
            with open(json_file, 'r', encoding='utf-8') as f:
                report = json.load(f)
                all_reports.append(report)

    if not all_reports:
        print("沒有找到任何紀錄")
        return

    # 按日期排序
    all_reports.sort(key=lambda x: x['date'])

    start_date = all_reports[0]['date']
    end_date = all_reports[-1]['date']

    print(f"找到 {len(all_reports)} 天的紀錄")
    print(f"日期範圍: {start_date} ~ {end_date}")

    # 計算總天數和週數
    from datetime import datetime
    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
    end_dt = datetime.strptime(end_date, '%Y-%m-%d')
    days = (end_dt - start_dt).days + 1
    weeks = round(days / 7, 1)

    # 彙整成專案視角的格式（網頁需要的格式）
    # 只包含工作專案，排除 Side Projects
    projects_map = {}

    for daily in all_reports:
        # 只處理工作專案（排除 Side Projects）
        for proj in daily.get('work_projects', []):
            proj_name = proj['name']
            if proj_name not in projects_map:
                projects_map[proj_name] = {
                    'name': proj_name,
                    'totalCommits': 0,
                    'commits': []
                }

            for commit in proj['commits']:
                projects_map[proj_name]['commits'].append({
                    'hash': commit['hash'],
                    'date': daily['date'],
                    'message': commit['message'],
                    'body': commit.get('body', ''),
                    'category': categorize_commit(commit['message']),
                    'tags': []
                })
                projects_map[proj_name]['totalCommits'] += 1

    # 轉成列表並排序
    projects_list = list(projects_map.values())
    projects_list.sort(key=lambda x: x['totalCommits'], reverse=True)

    # 組合最終格式
    total_commits = sum(p['totalCommits'] for p in projects_list)
    output = {
        'period': {
            'start': start_date,
            'end': end_date,
            'days': days,
            'weeks': weeks
        },
        'author': AUTHOR,
        'summary': {
            'totalCommits': total_commits,
            'projectCount': len(projects_list),
            'dailyAverage': round(total_commits / days, 1) if days > 0 else 0
        },
        'projects': projects_list
    }

    # 儲存到 public/data
    public_data_path = os.path.join(WORK_PROGRESS_PATH, "public", "data")

    # 儲存固定檔名（供網頁使用）
    output_file = os.path.join(public_data_path, f"work-log-{start_date}-to-{end_date}.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n已儲存: {output_file}")
    print(f"統計: {total_commits} commits / {len(projects_list)} 專案 / 日均 {output['summary']['dailyAverage']}")

    return output_file

if __name__ == "__main__":
    main()

    # 彙整到 public/data 供網頁使用
    merge_to_public()

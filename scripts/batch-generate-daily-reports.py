"""
批次生成每日工作紀錄
重新生成最近三個月的每日紀錄
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

def generate_daily_report(date_str, gitlab_repos, personal_repos):
    """生成單日報告"""
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

def main():
    # 日期範圍：最近三個月
    start_date = datetime(2025, 7, 15)
    end_date = datetime(2025, 10, 14)

    print("=" * 80)
    print("批次生成每日工作紀錄（最近三個月）")
    print(f"日期範圍: {start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}")
    print("=" * 80)

    # 找出所有 repositories
    print("\n掃描 Git repositories...")
    gitlab_repos = get_git_repos(GITLAB_PATH)
    personal_repos = get_git_repos(PERSONAL_PATH)
    print(f"Gitlab 專案: {len(gitlab_repos)} 個")
    print(f"個人專案: {len(personal_repos)} 個")

    # 生成每一天的紀錄
    current = start_date
    total_days = 0
    total_commits = 0

    while current <= end_date:
        date_str = current.strftime('%Y-%m-%d')
        year_month = current.strftime('%Y-%m')

        # 生成報告
        report = generate_daily_report(date_str, gitlab_repos, personal_repos)

        # 只儲存有 commits 的日子
        if report["summary"]["totalCommits"] > 0:
            # 建立目錄
            daily_folder = os.path.join(WORK_PROGRESS_PATH, "daily-reports", year_month)
            os.makedirs(daily_folder, exist_ok=True)

            # 儲存 Markdown
            md_file = os.path.join(daily_folder, f"{date_str}.md")
            markdown = generate_markdown(report)
            with open(md_file, 'w', encoding='utf-8') as f:
                f.write(markdown)

            # 儲存 JSON
            json_file = os.path.join(daily_folder, f"{date_str}.json")
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)

            print(f"[OK] {date_str}: {report['summary']['totalCommits']} commits")
            total_days += 1
            total_commits += report["summary"]["totalCommits"]
        else:
            print(f"  {date_str}: 無提交")

        current += timedelta(days=1)

    print("\n" + "=" * 80)
    print(f"完成！共生成 {total_days} 天的紀錄，總計 {total_commits} commits")
    print("=" * 80)

if __name__ == "__main__":
    main()

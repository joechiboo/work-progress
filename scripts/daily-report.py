import subprocess
import os
import json
from datetime import datetime, timedelta

GITLAB_PATH = "D:\\Gitlab"
PERSONAL_PATH = "D:\\Personal\\Project"
AUTHOR = "joechiboo"

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
        cmd = [
            'git', '-C', repo_path, 'log',
            f'--author={author}',
            f'--since={date_str} 00:00',
            f'--until={date_str} 23:59',
            '--format=%H|||%ai|||%s|||%b',
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')

        commits = []
        for line in result.stdout.strip().split('\n'):
            if not line:
                continue
            parts = line.split('|||')
            if len(parts) >= 3:
                commits.append({
                    "hash": parts[0].strip()[:8],
                    "time": parts[1].strip()[11:16],  # HH:MM
                    "message": parts[2].strip(),
                    "body": parts[3].strip() if len(parts) > 3 else ""
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

def generate_markdown(reports):
    """生成 Markdown 報告"""
    md = "# 📅 每日工作紀錄 (2025-10-09 ~ 2025-10-13)\n\n"

    # 統計總覽
    total_work = sum(r["summary"]["workCommits"] for r in reports)
    total_side = sum(r["summary"]["sideCommits"] for r in reports)
    total = total_work + total_side

    md += "## 📊 期間統計\n\n"
    md += f"| 項目 | 數量 |\n"
    md += f"|------|------|\n"
    md += f"| 工作專案 commits | {total_work} |\n"
    md += f"| Side Projects commits | {total_side} |\n"
    md += f"| **總計** | **{total}** |\n"
    md += f"| 日均 | {total/len(reports):.1f} |\n\n"

    md += "---\n\n"

    # 每日明細
    for report in reports:
        date = report["date"]
        weekday = report["weekday"]
        work_count = report["summary"]["workCommits"]
        side_count = report["summary"]["sideCommits"]
        total_count = report["summary"]["totalCommits"]

        md += f"## 📆 {date} (週{weekday})\n\n"

        if total_count == 0:
            md += "🏖️ **休假日或無提交紀錄**\n\n"
            md += "---\n\n"
            continue

        md += f"**統計**: 工作 {work_count} + Side {side_count} = 總計 {total_count} commits\n\n"

        # 工作專案
        if report["work_projects"]:
            md += "### 💼 工作專案\n\n"
            for proj in report["work_projects"]:
                md += f"#### {proj['name']} ({proj['count']} commits)\n\n"
                for commit in proj["commits"]:
                    category = categorize_commit(commit["message"])
                    md += f"- **{commit['time']}** [{category}] {commit['message']}\n"
                md += "\n"

        # Side Projects
        if report["side_projects"]:
            md += "### 🎨 Side Projects\n\n"
            for proj in report["side_projects"]:
                md += f"#### {proj['name']} ({proj['count']} commits)\n\n"
                for commit in proj["commits"]:
                    category = categorize_commit(commit["message"])
                    md += f"- **{commit['time']}** [{category}] {commit['message']}\n"
                md += "\n"

        md += "---\n\n"

    md += f"📅 報告生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"

    return md

def main():
    # 生成 10/9 - 10/13 的報告
    dates = [
        "2025-10-09",
        "2025-10-10",
        "2025-10-11",
        "2025-10-12",
        "2025-10-13"
    ]

    print("=" * 80)
    print("生成每日工作紀錄 (2025-10-09 ~ 2025-10-13)")
    print("=" * 80)

    reports = []
    for date_str in dates:
        print(f"\n處理 {date_str}...")
        report = generate_daily_report(date_str)
        reports.append(report)
        print(f"  工作: {report['summary']['workCommits']} commits")
        print(f"  Side: {report['summary']['sideCommits']} commits")
        print(f"  總計: {report['summary']['totalCommits']} commits")

    # 生成 Markdown
    markdown = generate_markdown(reports)

    # 儲存
    output_file = "daily-reports-1009-1013.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(markdown)

    # 同時儲存 JSON
    json_file = "public/data/daily-reports-1009-1013.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(reports, f, ensure_ascii=False, indent=2)

    print(f"\nMarkdown report: {output_file}")
    print(f"JSON data: {json_file}")

if __name__ == "__main__":
    main()

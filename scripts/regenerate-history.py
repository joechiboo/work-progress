"""
重新生成歷史紀錄（5-7 月）
直接複製 auto-daily-report.py 的邏輯
"""
import subprocess
import os
import json
import sys
import logging
from datetime import datetime, timedelta

# 設定 logging（Windows console 需要設定 UTF-8）
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

GITLAB_PATH = "D:\\Gitlab"
PERSONAL_PATH = "D:\\Personal\\Project"
WORK_PROGRESS_PATH = "D:\\Personal\\Project\\work-progress"
AUTHOR = "UCL\\joechiboo"

def get_git_repos(base_path, max_depth=3):
    """遞迴尋找所有 Git repositories"""
    repos = []
    if not os.path.exists(base_path):
        return repos

    for root, dirs, files in os.walk(base_path):
        depth = root.replace(base_path, '').count(os.sep)
        if depth >= max_depth:
            dirs[:] = []
            continue
        if '.git' in dirs:
            repos.append(root)

    return repos

def get_commits_for_date(repo_path, author, date_str):
    """取得特定日期的 commits"""
    try:
        cmd = [
            'git', '-C', repo_path, 'log',
            f'--since={date_str} 00:00',
            f'--until={date_str} 23:59',
            '--format=%an|||%H|||%ai|||%s|||%b',
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')

        if result.returncode != 0:
            return []

        commits = []
        for line in result.stdout.strip().split('\n'):
            if not line:
                continue
            parts = line.split('|||')
            if len(parts) >= 4:
                author_name = parts[0].strip()
                if author in author_name or author_name == 'joechiboo':
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

    # 收集個人專案
    for repo in personal_repos:
        proj_name = repo.replace(PERSONAL_PATH + "\\", "")
        commits = get_commits_for_date(repo, AUTHOR, date_str)
        if commits:
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

def regenerate_range(start_date_str, end_date_str):
    """重新生成指定日期範圍的報告"""
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d')

    current_date = start_date
    generated_count = 0

    logging.info(f"掃描 Git repositories...")
    gitlab_repos = get_git_repos(GITLAB_PATH)
    personal_repos = get_git_repos(PERSONAL_PATH)
    logging.info(f"找到 {len(gitlab_repos)} 個工作 repos, {len(personal_repos)} 個個人 repos")

    while current_date <= end_date:
        date_str = current_date.strftime('%Y-%m-%d')

        try:
            # 生成報告
            report = generate_daily_report(date_str)

            # 只儲存有 commits 的日期
            if report['summary']['totalCommits'] > 0:
                # 生成 Markdown
                markdown = generate_markdown(report)

                # 建立目錄
                daily_folder = os.path.join(WORK_PROGRESS_PATH, "daily-reports")
                year_month = current_date.strftime('%Y-%m')
                monthly_folder = os.path.join(daily_folder, year_month)
                os.makedirs(monthly_folder, exist_ok=True)

                # 儲存檔案
                md_file = os.path.join(monthly_folder, f"{date_str}.md")
                with open(md_file, 'w', encoding='utf-8') as f:
                    f.write(markdown)

                json_file = os.path.join(monthly_folder, f"{date_str}.json")
                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump(report, f, ensure_ascii=False, indent=2)

                logging.info(f"✓ {date_str}: {report['summary']['totalCommits']} commits (工作:{report['summary']['workCommits']}, Side:{report['summary']['sideCommits']})")
                generated_count += 1

        except Exception as e:
            logging.error(f"✗ {date_str}: {str(e)}")

        current_date += timedelta(days=1)

    logging.info(f"\n完成！已生成 {generated_count} 天的紀錄")

if __name__ == "__main__":
    logging.info("=" * 60)
    logging.info("重新生成歷史紀錄")
    logging.info("=" * 60)

    # 生成 2025 年 5-7 月的紀錄
    regenerate_range("2025-05-01", "2025-07-31")

    logging.info("\n完成！請執行 merge_to_public() 來彙整所有資料")

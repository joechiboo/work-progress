import subprocess
import os
import json
from datetime import datetime

GITLAB_PATH = "D:\\Gitlab"
PERSONAL_PATH = "D:\\Personal\\Project"
AUTHOR = "UCL\\joechiboo"

periods = [
    {
        "name": "使用前",
        "id": "pre-claude",
        "since": "2025-05-01",
        "until": "2025-07-13",
        "days": 74,
        "cost": 0
    },
    {
        "name": "Claude 標準版",
        "id": "claude-standard",
        "since": "2025-07-14",
        "until": "2025-09-10",
        "days": 59,
        "cost": 40
    },
    {
        "name": "Claude Max 版",
        "id": "claude-max",
        "since": "2025-09-11",
        "until": "2025-10-29",
        "days": 49,
        "cost": 97.81
    }
]

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

def get_commits_detail(repo_path, author, since, until):
    """取得詳細的 commit 資訊"""
    try:
        # 先抓全部 commits，包含 author name
        cmd = [
            'git', '-C', repo_path, 'log',
            f'--since={since}',
            f'--until={until}',
            '--format=%an|||%H|||%ad|||%s|||%b',
            '--date=short'
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
                        "hash": parts[1].strip(),
                        "date": parts[2].strip(),
                        "message": parts[3].strip(),
                        "body": parts[4].strip() if len(parts) > 4 else ""
                    })
        return commits
    except Exception as e:
        print(f"Error in {repo_path}: {e}")
        return []

def categorize_commit(message, body):
    """自動分類 commit"""
    text = f"{message} {body}".lower()

    categories = {
        '功能開發': ['feat', 'feature', '新增', '實作', '完成'],
        '錯誤修正': ['fix', 'bug', 'hotfix', '修正', '修復', '除錯'],
        '重構': ['refactor', 'restructure', '重構', '優化'],
        '文檔': ['docs', 'documentation', '文檔', '文件', '說明'],
        '測試': ['test', 'testing', '測試'],
        '樣式': ['style', 'ui', 'ux', 'css', '樣式', '介面'],
        '配置': ['config', 'setup', '配置', '設定'],
    }

    for category, keywords in categories.items():
        if any(keyword in text for keyword in keywords):
            return category

    return '其他'

def process_period(period, gitlab_repos, personal_repos):
    """處理單一時期的數據"""
    result = {
        "period": {
            "name": period["name"],
            "id": period["id"],
            "start": period["since"],
            "end": period["until"],
            "days": period["days"],
            "cost": period["cost"]
        },
        "work_projects": [],
        "side_projects": [],
        "summary": {}
    }

    # 處理工作專案
    work_total = 0
    for repo in gitlab_repos:
        proj_name = repo.replace(GITLAB_PATH + "\\", "")
        commits = get_commits_detail(repo, AUTHOR, period["since"], period["until"])

        if commits:
            # 分類統計
            categories = {}
            for commit in commits:
                category = categorize_commit(commit["message"], commit["body"])
                commit["category"] = category
                categories[category] = categories.get(category, 0) + 1

            result["work_projects"].append({
                "name": proj_name,
                "totalCommits": len(commits),
                "categories": categories,
                "commits": commits[:10] if len(commits) > 10 else commits  # 只保留前10個詳細記錄
            })
            work_total += len(commits)

    # 處理個人專案
    side_total = 0
    for repo in personal_repos:
        proj_name = repo.replace(PERSONAL_PATH + "\\", "")
        commits = get_commits_detail(repo, AUTHOR, period["since"], period["until"])

        if commits:
            categories = {}
            for commit in commits:
                category = categorize_commit(commit["message"], commit["body"])
                commit["category"] = category
                categories[category] = categories.get(category, 0) + 1

            result["side_projects"].append({
                "name": proj_name,
                "totalCommits": len(commits),
                "categories": categories,
                "commits": commits[:10] if len(commits) > 10 else commits
            })
            side_total += len(commits)

    # 排序
    result["work_projects"].sort(key=lambda x: x["totalCommits"], reverse=True)
    result["side_projects"].sort(key=lambda x: x["totalCommits"], reverse=True)

    # 統計
    result["summary"] = {
        "workCommits": work_total,
        "sideCommits": side_total,
        "totalCommits": work_total + side_total,
        "dailyAverage": round((work_total + side_total) / period["days"], 2),
        "workDailyAverage": round(work_total / period["days"], 2),
        "sideDailyAverage": round(side_total / period["days"], 2)
    }

    return result

def main():
    print("=" * 80)
    print("收集所有時期的 Git Commit 資料")
    print("=" * 80)

    # 找出所有 repositories
    print("\n掃描 Git repositories...")
    gitlab_repos = get_git_repos(GITLAB_PATH)
    personal_repos = get_git_repos(PERSONAL_PATH)

    print(f"Gitlab 專案: {len(gitlab_repos)} 個")
    print(f"個人專案: {len(personal_repos)} 個")

    # 收集所有時期的數據
    all_periods = []

    for period in periods:
        print(f"\n處理 {period['name']} ({period['since']} ~ {period['until']})...")
        period_data = process_period(period, gitlab_repos, personal_repos)
        all_periods.append(period_data)

        print(f"  工作專案: {period_data['summary']['workCommits']} commits")
        print(f"  個人專案: {period_data['summary']['sideCommits']} commits")
        print(f"  總計: {period_data['summary']['totalCommits']} commits")
        print(f"  日均: {period_data['summary']['dailyAverage']} commits/day")

    # 組合最終結果
    output = {
        "generatedAt": datetime.now().isoformat(),
        "author": AUTHOR,
        "periods": all_periods,
        "comparison": {
            "work": {
                "pre": all_periods[0]["summary"]["workCommits"],
                "standard": all_periods[1]["summary"]["workCommits"],
                "max": all_periods[2]["summary"]["workCommits"]
            },
            "side": {
                "pre": all_periods[0]["summary"]["sideCommits"],
                "standard": all_periods[1]["summary"]["sideCommits"],
                "max": all_periods[2]["summary"]["sideCommits"]
            },
            "total": {
                "pre": all_periods[0]["summary"]["totalCommits"],
                "standard": all_periods[1]["summary"]["totalCommits"],
                "max": all_periods[2]["summary"]["totalCommits"]
            }
        }
    }

    # 儲存檔案
    output_file = "public/data/claude-efficiency-data.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\nSaved: {output_file}")
    print(f"File size: {os.path.getsize(output_file)} bytes")

if __name__ == "__main__":
    main()

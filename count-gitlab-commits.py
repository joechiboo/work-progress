import subprocess
import os
from datetime import datetime

GITLAB_PATH = "D:\\Gitlab"
AUTHOR = "joechiboo"

periods = [
    ("使用前", "2025-05-01", "2025-07-13", 74),
    ("Claude 標準版", "2025-07-14", "2025-09-10", 59),
    ("Claude Max 版", "2025-09-11", "2025-10-08", 28),
]

def get_git_repos(base_path, max_depth=3):
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

def count_commits(repo_path, author, since, until):
    try:
        cmd = [
            'git', '-C', repo_path, 'log',
            f'--author={author}',
            f'--since={since}',
            f'--until={until}',
            '--oneline'
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        return len([line for line in result.stdout.strip().split('\n') if line])
    except:
        return 0

print("=" * 80)
print("Gitlab 工作專案 Commit 統計")
print("=" * 80)

repos = get_git_repos(GITLAB_PATH)
print(f"\n找到 {len(repos)} 個 Git repositories\n")

for period_name, since, until, days in periods:
    print(f"\n{'=' * 80}")
    print(f"{period_name} ({since} ~ {until}, {days}天)")
    print(f"{'=' * 80}")

    total = 0
    project_stats = []

    for repo in repos:
        proj_name = repo.replace(GITLAB_PATH + "\\", "")
        count = count_commits(repo, AUTHOR, since, until)
        if count > 0:
            project_stats.append((proj_name, count))
            total += count

    # 排序並顯示
    project_stats.sort(key=lambda x: x[1], reverse=True)
    for proj_name, count in project_stats:
        print(f"{proj_name:40s}: {count:4d} commits")

    print(f"\n{'總計':40s}: {total:4d} commits")
    print(f"{'日均':40s}: {total/days:5.2f} commits/day")

print("\n" + "=" * 80)

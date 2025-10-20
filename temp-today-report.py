"""產生今天的報告來測試 Fast-Trivia"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

from datetime import datetime
import subprocess
import json

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

# 測試掃描 Personal repos
print("掃描 Personal Project repos...")
personal_repos = get_git_repos(PERSONAL_PATH)
print(f"找到 {len(personal_repos)} 個 repos:\n")

for repo in personal_repos:
    proj_name = repo.replace(PERSONAL_PATH + "\\", "")
    # 測試 10/18, 10/19, 10/20
    for date in ['2025-10-18', '2025-10-19', '2025-10-20']:
        commits = get_commits_for_date(repo, AUTHOR, date)
        if commits:
            print(f"{proj_name} ({date}): {len(commits)} commits")
            for c in commits[:3]:
                print(f"  - {c['message']}")

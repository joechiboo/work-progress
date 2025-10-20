"""檢查各 side project 從 7/15 到現在有多少 commits"""
import subprocess
import os

PERSONAL_PATH = "D:\\Personal\\Project"

side_projects = [
    "bordeaux-ii",
    "CharMon",
    "CyclePulse",
    "FridgeMaster",
    "jiayi.github.io",
    "joechiboo.github.io",
    "Pomodoro",
    "ResearchSeminar-3H",
    "RiskPrediction-3H",
    "water-tracker",
    "ZebraSite",
    "Fast-Trivia\\Fast-Trivia"
]

print("檢查 2025-07-15 到 2025-10-19 的 commits (author=joechiboo):\n")
total = 0

for proj in side_projects:
    repo_path = os.path.join(PERSONAL_PATH, proj)
    if os.path.exists(os.path.join(repo_path, ".git")):
        cmd = [
            'git', '-C', repo_path, 'log',
            '--since=2025-07-15',
            '--until=2025-10-19 23:59',
            '--author=joechiboo',
            '--oneline'
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        count = len([line for line in result.stdout.strip().split('\n') if line])
        if count > 0:
            print(f"{proj}: {count} commits")
            total += count

print(f"\n總計: {total} commits")

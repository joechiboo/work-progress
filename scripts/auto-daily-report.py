"""
每日自動工作紀錄生成器
在每天早上 07:00 執行，自動整理昨天的工作紀錄
"""
import re
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

# 自動偵測環境路徑（公司用 D:\，家裡用 C:\）
if os.path.exists("D:\\Gitlab"):
    GITLAB_PATH = "D:\\Gitlab"
    PERSONAL_PATH = "D:\\Personal\\Project"
    WORK_PROGRESS_PATH = "D:\\Personal\\Project\\work-progress"
else:
    GITLAB_PATH = "C:\\Gitlab"  # 家裡可能沒有 Gitlab
    PERSONAL_PATH = "C:\\Personal\\Project"
    WORK_PROGRESS_PATH = "C:\\Personal\\Project\\work-progress\\work-progress-ssh"

# Claude 設定 repo（skills / runbooks / memory），不在上面兩個掃描根底下
CLAUDE_PATH = os.path.join(os.path.expanduser("~"), ".claude")

MERGE_CATEGORY = '合併MR'

AUTHOR = "UCL\\joechiboo"

def summarize_merge(message, body):
    """GitLab MR merge -> (可讀訊息, 分類)；本地 sync merge -> None（雜訊，丟棄）

    merge commit 的 subject 是 "Merge branch 'x' into 'main'"，看不出做了什麼；
    真正的內容在 body 第一行，MR 編號在 "See merge request <group>!<n>" 那行。
    """
    mr_no = None
    title_lines = []
    for line in body.split('\n'):
        line = line.strip()
        if not line:
            continue
        m = re.search(r'See merge request \S+!(\d+)', line)
        if m:
            mr_no = m.group(1)
        else:
            title_lines.append(line)

    if mr_no is None:
        return None  # 沒有 MR 編號 = 本地 sync merge，不是工作

    title = title_lines[0] if title_lines else message
    return ('合併 MR !%s: %s' % (mr_no, title), MERGE_CATEGORY, title)

def drop_redundant_merges(commits):
    """自己開自己 merge 的 repo，每件事會出現兩次（原始 commit ＋ merge commit）。
    merge 標題和當天同 repo 已收錄的 commit 重複時丟掉 merge，只留原始 commit；
    留下來的是「原始 commit 當天看不到」的 merge（別人的分支、跨日的分支），
    那正是 review -> merge -> 上版 這類在日報裡原本隱形的工作。
    """
    plain = set(c["message"].strip() for c in commits if not c.get("_merge_title"))
    kept = []
    for c in commits:
        title = c.pop("_merge_title", None)
        if title and title.strip() in plain:
            continue
        kept.append(c)
    return kept

def get_git_repos(base_path, max_depth=4):
    """遞迴尋找所有 Git repositories"""
    logging.info(f"掃描 Git repositories: {base_path} (max_depth={max_depth})")
    repos = []

    if not os.path.exists(base_path):
        logging.error(f"路徑不存在: {base_path}")
        return repos

    for root, dirs, files in os.walk(base_path):
        depth = root.replace(base_path, '').count(os.sep)
        if depth >= max_depth:
            dirs[:] = []
            continue
        if '.git' in dirs:
            repos.append(root)
            logging.debug(f"找到 repo: {root}")
            # 不要立即清空 dirs，繼續掃描子目錄（支援巢狀 repo）

    logging.info(f"找到 {len(repos)} 個 repositories")
    return repos

def get_commits_for_date(repo_path, author, date_str):
    """取得特定日期的 commits"""
    try:
        # 先抓全部 commits，包含 author name (包含所有分支)
        # %ad + format-local: GitLab 網頁按 merge 產生的 commit 是 UTC，用 %ai 會早 8 小時
        # %x1e 當紀錄分隔: body 可能多行，用換行切會把多行 body 的 commit 整筆漏掉
        cmd = [
            'git', '-C', repo_path, 'log',
            '--all',
            f'--since={date_str} 00:00',
            f'--until={date_str} 23:59',
            '--date=format-local:%Y-%m-%d %H:%M:%S',
            '--format=%an|||%H|||%ad|||%s|||%b%x1e',
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')

        if result.returncode != 0:
            logging.warning(f"Git command failed for {repo_path}: {result.stderr}")
            return []

        commits = []
        for record in result.stdout.split('\x1e'):
            record = record.strip()
            if not record:
                continue
            parts = record.split('|||')
            if len(parts) >= 4:
                author_name = parts[0].strip()
                # 只保留 UCL\joechiboo、joechiboo、紀伯喬 或 Claude 的 commits
                if not (author in author_name or author_name == 'joechiboo'
                        or author_name == '紀伯喬' or author_name == 'Claude'):
                    continue

                commit_msg = parts[3].strip()
                commit_body = parts[4].strip() if len(parts) > 4 else ""
                category = None
                merge_title = None

                if commit_msg.startswith('Merge '):
                    # 自己按下的 MR merge 是工作（review -> merge -> 上版），要留下來；
                    # 本地 sync 用的 merge 沒有 See merge request，那才是雜訊
                    merged = summarize_merge(commit_msg, commit_body)
                    if merged is None:
                        continue
                    commit_msg, category, merge_title = merged

                commits.append({
                    "hash": parts[1].strip()[:8],
                    "time": parts[2].strip()[11:16],
                    "message": commit_msg,
                    "body": commit_body,
                    "category": category or categorize_commit(commit_msg),
                    "_merge_title": merge_title
                })

        commits = drop_redundant_merges(commits)

        if commits:
            logging.info(f"  ✓ {os.path.basename(repo_path)}: {len(commits)} commits")

        return commits
    except Exception as e:
        logging.error(f"Error getting commits from {repo_path}: {str(e)}")
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
    logging.info(f"開始生成 {date_str} 的報告")

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

    # Claude 設定 repo（skills / runbooks / memory）算工作專案
    if os.path.exists(os.path.join(CLAUDE_PATH, ".git")):
        claude_commits = get_commits_for_date(CLAUDE_PATH, AUTHOR, date_str)
        if claude_commits:
            report["work_projects"].append({
                "name": ".claude (工具設定)",
                "commits": claude_commits,
                "count": len(claude_commits)
            })
            report["summary"]["workCommits"] += len(claude_commits)

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
                category = commit.get("category") or categorize_commit(commit["message"])
                md += f"- **{commit['time']}** [{category}] {commit['message']}\n"
            md += "\n"

    # Side Projects
    if report["side_projects"]:
        md += "## 🎨 Side Projects\n\n"
        for proj in report["side_projects"]:
            md += f"### {proj['name']} ({proj['count']} commits)\n\n"
            for commit in proj["commits"]:
                category = commit.get("category") or categorize_commit(commit["message"])
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
        result = subprocess.run(['git', 'add', 'daily-reports/', 'public/data/'],
                               capture_output=True, text=True, encoding='utf-8')
        if result.returncode != 0:
            logging.error(f"git add failed: {result.stderr}")
            return False
        logging.info(f"git add 成功")

        # git commit
        commit_msg = f"docs: 每日工作紀錄 {date_str} ({total_commits} commits)\n\n🤖 自動生成於 {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        result = subprocess.run(['git', 'commit', '-m', commit_msg],
                               capture_output=True, text=True, encoding='utf-8')
        if result.returncode != 0:
            # 可能沒有變更，這不算錯誤
            if 'nothing to commit' in result.stdout or 'nothing to commit' in result.stderr:
                logging.info("沒有變更需要 commit")
            else:
                logging.error(f"git commit failed: {result.stderr}")
                return False
        else:
            logging.info(f"git commit 成功: {commit_msg.split(chr(10))[0]}")

        # git push
        result = subprocess.run(['git', 'push'],
                               capture_output=True, text=True, encoding='utf-8',
                               timeout=30)
        if result.returncode != 0:
            logging.error(f"git push failed: {result.stderr}")
            logging.error(f"stdout: {result.stdout}")
            return False

        logging.info(f"git push 成功: {result.stdout}")
        return True
    except subprocess.TimeoutExpired:
        logging.error("git push timeout (30秒)")
        return False
    except subprocess.CalledProcessError as e:
        logging.error(f"Git operation failed: {e}")
        logging.error(f"stderr: {e.stderr if hasattr(e, 'stderr') else 'N/A'}")
        return False
    except Exception as e:
        logging.error(f"Unexpected error: {e}", exc_info=True)
        return False

def main():
    # 先同步最新的變更
    logging.info("正在同步遠端變更...")
    try:
        os.chdir(WORK_PROGRESS_PATH)
        result = subprocess.run(['git', 'pull', 'origin', 'main'],
                               capture_output=True, text=True, encoding='utf-8')
        if result.returncode == 0:
            logging.info(f"Git pull 成功: {result.stdout}")
        else:
            logging.warning(f"Git pull 失敗，繼續執行: {result.stderr}")
    except Exception as e:
        logging.warning(f"Git pull 發生錯誤，繼續執行: {e}")

    # 解析參數：如果有 --today 就用今天，否則用昨天
    import sys
    use_today = '--today' in sys.argv

    if use_today:
        target_date = datetime.now()
    else:
        target_date = datetime.now() - timedelta(days=1)

    date_str = target_date.strftime('%Y-%m-%d')

    logging.info("=" * 60)
    logging.info(f"自動生成每日工作紀錄: {date_str}")
    logging.info(f"執行時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logging.info("=" * 60)

    # 生成報告
    try:
        report = generate_daily_report(date_str)
    except Exception as e:
        logging.error(f"生成報告失敗: {str(e)}", exc_info=True)
        return

    logging.info(f"工作專案: {report['summary']['workCommits']} commits")
    logging.info(f"Side Projects: {report['summary']['sideCommits']} commits")
    logging.info(f"總計: {report['summary']['totalCommits']} commits")

    # 生成 Markdown
    markdown = generate_markdown(report)

    # 儲存檔案
    daily_folder = os.path.join(WORK_PROGRESS_PATH, "daily-reports")
    os.makedirs(daily_folder, exist_ok=True)

    # 依年月分類
    year_month = target_date.strftime('%Y-%m')
    monthly_folder = os.path.join(daily_folder, year_month)
    os.makedirs(monthly_folder, exist_ok=True)

    md_file = os.path.join(monthly_folder, f"{date_str}.md")
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(markdown)

    # 儲存 JSON
    json_file = os.path.join(monthly_folder, f"{date_str}.json")
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    logging.info(f"已儲存 Markdown: {md_file}")
    logging.info(f"已儲存 JSON: {json_file}")

    # 自動 commit 和 push
    if report['summary']['totalCommits'] > 0:
        logging.info("正在 commit 並 push 到 GitHub...")
        if git_commit_and_push(date_str, report['summary']['totalCommits']):
            logging.info("✓ 成功推送到 GitHub!")
        else:
            logging.error("✗ 推送失敗，請手動處理")
    else:
        logging.info("無提交紀錄，跳過 git push")

    logging.info("完成!")

def merge_to_public():
    """彙整所有每日紀錄到 public/data（輸出網頁需要的彙整格式）"""
    import glob

    logging.info("\n" + "=" * 60)
    logging.info("彙整每日紀錄到 public/data")
    logging.info("=" * 60)

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
        logging.warning("沒有找到任何紀錄")
        return

    # 按日期排序
    all_reports.sort(key=lambda x: x['date'])

    start_date = all_reports[0]['date']
    end_date = all_reports[-1]['date']

    logging.info(f"找到 {len(all_reports)} 天的紀錄")
    logging.info(f"日期範圍: {start_date} ~ {end_date}")

    # 計算總天數和週數
    from datetime import datetime
    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
    end_dt = datetime.strptime(end_date, '%Y-%m-%d')
    days = (end_dt - start_dt).days + 1
    weeks = round(days / 7, 1)

    # 彙整成專案視角的格式（網頁需要的格式）
    work_projects_map = {}
    side_projects_map = {}

    for daily in all_reports:
        # 處理工作專案
        for proj in daily.get('work_projects', []):
            proj_name = proj['name']
            if proj_name not in work_projects_map:
                work_projects_map[proj_name] = {
                    'name': proj_name,
                    'totalCommits': 0,
                    'commits': [],
                    'type': 'work'
                }

            for commit in proj['commits']:
                work_projects_map[proj_name]['commits'].append({
                    'hash': commit['hash'],
                    'date': daily['date'],
                    'message': commit['message'],
                    'body': commit.get('body', ''),
                    'category': commit.get('category') or categorize_commit(commit['message']),
                    'tags': []
                })
                work_projects_map[proj_name]['totalCommits'] += 1

        # 處理 Side Projects
        for proj in daily.get('side_projects', []):
            proj_name = proj['name']
            if proj_name not in side_projects_map:
                side_projects_map[proj_name] = {
                    'name': proj_name,
                    'totalCommits': 0,
                    'commits': [],
                    'type': 'side'
                }

            for commit in proj['commits']:
                side_projects_map[proj_name]['commits'].append({
                    'hash': commit['hash'],
                    'date': daily['date'],
                    'message': commit['message'],
                    'body': commit.get('body', ''),
                    'category': commit.get('category') or categorize_commit(commit['message']),
                    'tags': []
                })
                side_projects_map[proj_name]['totalCommits'] += 1

    # 轉成列表並排序
    work_projects_list = list(work_projects_map.values())
    work_projects_list.sort(key=lambda x: x['totalCommits'], reverse=True)

    side_projects_list = list(side_projects_map.values())
    side_projects_list.sort(key=lambda x: x['totalCommits'], reverse=True)

    # 合併所有專案（用於網頁篩選）
    projects_list = work_projects_list + side_projects_list

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
    os.makedirs(public_data_path, exist_ok=True)

    # 儲存帶日期的檔案（備份用）
    dated_file = os.path.join(public_data_path, f"work-log-{start_date}-to-{end_date}.json")
    with open(dated_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    # 儲存固定檔名（供網頁「專案明細」分頁按需載入）
    latest_file = os.path.join(public_data_path, "work-log-latest.json")
    with open(latest_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    # 產生輕量摘要（供網頁「總覽」與趨勢圖，不含 commit 明細）
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from build_summary import write_summary
    summary_file = write_summary(public_data_path, output)

    logging.info(f"已儲存:")
    logging.info(f"  - {dated_file} (備份)")
    logging.info(f"  - {latest_file} (明細，按需載入)")
    logging.info(f"  - {summary_file} (總覽，{os.path.getsize(summary_file) // 1024} KB)")
    logging.info(f"統計: {total_commits} commits / {len(projects_list)} 專案 / 日均 {output['summary']['dailyAverage']}")

    return latest_file

if __name__ == "__main__":
    main()

    # 彙整到 public/data 供網頁使用
    merge_to_public()

    # 確保 merge_to_public 的變更也被 commit 和 push
    logging.info("\n正在 commit 並 push merge_to_public 的變更...")
    try:
        os.chdir(WORK_PROGRESS_PATH)

        # 檢查是否有變更
        status_result = subprocess.run(['git', 'status', '--porcelain'],
                                      capture_output=True, text=True, encoding='utf-8')

        if status_result.stdout.strip():
            # 有變更才 commit
            result = subprocess.run(['git', 'add', 'public/data/'],
                                   capture_output=True, text=True, encoding='utf-8')
            if result.returncode != 0:
                logging.error(f"git add failed: {result.stderr}")
            else:
                logging.info("git add 成功")

                commit_msg = f"docs: 更新彙整資料 {datetime.now().strftime('%Y-%m-%d')}\n\n🤖 自動生成於 {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                result = subprocess.run(['git', 'commit', '-m', commit_msg],
                                       capture_output=True, text=True, encoding='utf-8')
                if result.returncode != 0:
                    logging.error(f"git commit failed: {result.stderr}")
                else:
                    logging.info(f"git commit 成功: {commit_msg.split(chr(10))[0]}")

                    result = subprocess.run(['git', 'push'],
                                           capture_output=True, text=True, encoding='utf-8',
                                           timeout=30)
                    if result.returncode != 0:
                        logging.error(f"git push failed: {result.stderr}")
                        logging.error(f"stdout: {result.stdout}")
                    else:
                        logging.info(f"✓ 成功推送彙整資料到 GitHub!")
                        logging.info(f"push output: {result.stdout}")
        else:
            logging.info("無需推送（沒有變更）")
    except subprocess.TimeoutExpired:
        logging.error("git push timeout (30秒)")
    except subprocess.CalledProcessError as e:
        logging.error(f"✗ 推送彙整資料失敗: {e}")
        logging.error(f"stderr: {e.stderr if hasattr(e, 'stderr') else 'N/A'}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}", exc_info=True)

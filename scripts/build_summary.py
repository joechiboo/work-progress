"""
把完整的 work-log（含每筆 commit 明細）壓成網頁「總覽」用的輕量摘要。

總覽頁只需要「每天、每專案、每分類各幾筆」就能算出任意區間的
統計、專案排行與趨勢圖，不需要載入 commit 明細（1.5MB+）。
明細改由「專案明細」分頁按需載入 work-log-latest.json。

可獨立執行：
    python scripts/build_summary.py
也被 auto-daily-report.py 的 merge_to_public() 呼叫。
"""
import json
import os
import sys
from collections import defaultdict


def build_summary(full):
    """full: work-log-latest.json 的結構 -> 回傳輕量摘要 dict"""
    # date -> {'work': n, 'side': n, 'projects': {name: n}, 'categories': {cat: n}}
    daily = defaultdict(lambda: {
        'work': 0,
        'side': 0,
        'projects': defaultdict(int),
        'categories': {'work': defaultdict(int), 'side': defaultdict(int)},
    })
    projects_meta = []

    for proj in full.get('projects', []):
        commits = proj.get('commits') or []
        if not commits:
            continue
        dates = sorted(c['date'] for c in commits)
        projects_meta.append({
            'name': proj['name'],
            'type': proj.get('type', 'work'),
            'totalCommits': len(commits),
            'firstDate': dates[0],
            'lastDate': dates[-1],
        })
        ptype = proj.get('type', 'work')
        for c in commits:
            day = daily[c['date']]
            day[ptype] = day.get(ptype, 0) + 1
            day['projects'][proj['name']] += 1
            day['categories'][ptype][c.get('category') or '未分類'] += 1

    daily_list = [
        {
            'date': d,
            'work': v['work'],
            'side': v['side'],
            'total': v['work'] + v['side'],
            'projects': dict(v['projects']),
            'categories': {k: dict(cats) for k, cats in v['categories'].items()},
        }
        for d, v in sorted(daily.items())
    ]

    return {
        'period': full.get('period', {}),
        'author': full.get('author', ''),
        'summary': full.get('summary', {}),
        'projects': projects_meta,
        'daily': daily_list,
    }


def write_summary(public_data_path, full):
    """產生 work-log-summary.json，回傳檔案路徑"""
    summary = build_summary(full)
    path = os.path.join(public_data_path, 'work-log-summary.json')
    with open(path, 'w', encoding='utf-8') as f:
        # 不縮排：這份檔案是給瀏覽器讀的，體積優先
        json.dump(summary, f, ensure_ascii=False, separators=(',', ':'))
    return path


if __name__ == '__main__':
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    public_data = os.path.join(root, 'public', 'data')
    latest = os.path.join(public_data, 'work-log-latest.json')

    if not os.path.exists(latest):
        print(f'找不到 {latest}', file=sys.stderr)
        sys.exit(1)

    with open(latest, 'r', encoding='utf-8') as f:
        full = json.load(f)

    out = write_summary(public_data, full)
    print(f'{out}  ({os.path.getsize(out) / 1024:.0f} KB, 原檔 {os.path.getsize(latest) / 1024:.0f} KB)')

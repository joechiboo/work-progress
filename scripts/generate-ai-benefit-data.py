# -*- coding: utf-8 -*-
"""
產生 AI 效益分頁所需的資料 (public/data/ai-benefit-data.json)

資料來源：public/data/work-log-latest.json（與儀表板工作紀錄同一份，口徑一致）
費用來源：Anthropic 實際帳單（見 ai-expense-summary-*.html）

口徑說明（務實版）：
- 只用可驗證的數字：commits、活躍天數、實付費用
- 不換算「時間價值 $XXX」「ROI XXX 倍」這類不可辯護的推估
- 改用「回本門檻」：每月費用相當於多少工程師工時，省下超過就划算
"""
import json
import os
from collections import defaultdict
from datetime import date, timedelta

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(BASE, 'public', 'data', 'work-log-latest.json')
OUT = os.path.join(BASE, 'public', 'data', 'ai-benefit-data.json')

# Joe 的實際訂閱扣款（US$），依帳單日
BILLING = [
    ('2025-07-14', 20.00, 'Claude Pro'),
    ('2025-08-14', 20.00, 'Claude Pro'),
    ('2025-09-11', 97.81, 'Claude Max 5x（首月按比例）'),
    ('2025-10-11', 100.00, 'Claude Max 5x'),
    ('2025-11-11', 100.00, 'Claude Max 5x'),
    ('2025-12-11', 100.00, 'Claude Max 5x'),
    ('2026-01-11', 100.00, 'Claude Max 5x'),
    ('2026-02-10', 100.00, 'Claude Max 5x'),
    ('2026-03-10', 100.00, 'Claude Max 5x'),
    ('2026-04-10', 100.00, 'Claude Max 5x'),
    ('2026-05-11', 100.00, 'Claude Max 5x'),
    ('2026-06-11', 100.00, 'Claude Max 5x'),
    ('2026-07-11', 100.00, 'Claude Max 5x'),
    ('2026-08-11', 100.00, 'Claude Max 5x'),   # 尚未列入季度報銷單，暫以定額計
    ('2026-09-11', 100.00, 'Claude Max 5x'),   # 同上
]

PERIODS = [
    dict(id='pre-claude',   name='使用前',           start='2025-05-05', end='2025-07-13', plan='無 AI 輔助'),
    dict(id='claude-pro',   name='Claude Pro',       start='2025-07-14', end='2025-09-10', plan='Pro US$20/月'),
    dict(id='claude-max-1', name='Claude Max 初期',  start='2025-09-11', end='2025-12-31', plan='Max 5x US$100/月'),
    dict(id='claude-max-2', name='Claude Max 長期',  start='2026-01-01', end='2026-09-16', plan='Max 5x US$100/月'),
]

# 回本門檻假設（可調）
USD_TWD = 32.71          # 含 1.5% 國外交易手續費的實際扣款匯率
HOURLY_TWD = 500         # 工程師工時成本假設


def daterange_days(start, end):
    s = date.fromisoformat(start)
    e = date.fromisoformat(end)
    return (e - s).days + 1


def cost_in(start, end):
    return round(sum(amt for d, amt, _ in BILLING if start <= d <= end), 2)


def main():
    with open(SRC, encoding='utf-8') as f:
        data = json.load(f)

    # 攤平成 (date, type, project)
    rows = []
    for p in data['projects']:
        ptype = p.get('type', 'work')
        for c in p.get('commits', []):
            rows.append((c['date'], ptype, p['name']))

    # ---- 每月序列 ----
    monthly = defaultdict(lambda: dict(work=0, side=0, days=set()))
    for d, t, _ in rows:
        m = monthly[d[:7]]
        m[t] = m.get(t, 0) + 1
        m['days'].add(d)

    monthly_series = []
    for ym in sorted(monthly):
        m = monthly[ym]
        total = m['work'] + m['side']
        y, mo = int(ym[:4]), int(ym[5:])
        # 該月落在資料範圍內的天數
        first = date(y, mo, 1)
        last = date(y + (mo == 12), (mo % 12) + 1, 1) - timedelta(days=1)
        first = max(first, date.fromisoformat(data['period']['start']))
        last = min(last, date.fromisoformat(data['period']['end']))
        span = (last - first).days + 1
        monthly_series.append(dict(
            month=ym, work=m['work'], side=m['side'], total=total,
            days=span, activeDays=len(m['days']),
            dailyAverage=round(total / span, 2),
            workDailyAverage=round(m['work'] / span, 2),
        ))

    # ---- 分期統計 ----
    periods = []
    baseline = None
    for spec in PERIODS:
        sub = [r for r in rows if spec['start'] <= r[0] <= spec['end']]
        days = daterange_days(spec['start'], spec['end'])
        work = sum(1 for r in sub if r[1] == 'work')
        side = len(sub) - work
        total = len(sub)
        active = len({r[0] for r in sub})
        cost = cost_in(spec['start'], spec['end'])
        s = dict(
            spec,
            days=days,
            cost=cost,
            costTwd=round(cost * USD_TWD),
            totalCommits=total,
            workCommits=work,
            sideCommits=side,
            projectCount=len({r[2] for r in sub}),
            activeDays=active,
            activeRatio=round(active / days * 100, 1),
            dailyAverage=round(total / days, 2),
            workDailyAverage=round(work / days, 2),
            sideDailyAverage=round(side / days, 2),
            perActiveDay=round(total / active, 2) if active else 0,
            costPerCommit=round(cost / total, 2) if total and cost else 0,
            workShare=round(work / total * 100, 1) if total else 0,
        )
        if baseline is None:
            baseline = s
            s['totalLift'] = None
            s['workLift'] = None
        else:
            s['totalLift'] = round((s['dailyAverage'] / baseline['dailyAverage'] - 1) * 100)
            s['workLift'] = round((s['workDailyAverage'] / baseline['workDailyAverage'] - 1) * 100)
        periods.append(s)

    total_cost = round(sum(amt for _, amt, _ in BILLING), 2)
    all_days = daterange_days(PERIODS[0]['start'], PERIODS[-1]['end'])
    ai_days = daterange_days(PERIODS[1]['start'], PERIODS[-1]['end'])
    ai_commits = sum(p['totalCommits'] for p in periods[1:])
    ai_work_commits = sum(p['workCommits'] for p in periods[1:])

    monthly_cost_twd = round(100 * USD_TWD)
    output = dict(
        generatedAt=date.today().isoformat(),
        source='public/data/work-log-latest.json',
        dataRange=dict(start=data['period']['start'], end=data['period']['end'], days=all_days),
        assumptions=dict(
            usdTwd=USD_TWD,
            hourlyTwd=HOURLY_TWD,
            note='台幣金額為信用卡實際扣款（含約 1.5% 國外交易手續費）；2026/08、2026/09 帳單尚未列入季度報銷單，暫以定額 US$100 計'
        ),
        overall=dict(
            totalCost=total_cost,
            totalCostTwd=round(total_cost * USD_TWD),
            aiDays=ai_days,
            aiCommits=ai_commits,
            aiWorkCommits=ai_work_commits,
            costPerCommit=round(total_cost / ai_commits, 2),
            costPerCommitTwd=round(total_cost * USD_TWD / ai_commits, 1),
            dailyCostTwd=round(total_cost * USD_TWD / ai_days, 1),
            monthlyCostTwd=monthly_cost_twd,
            breakEvenHours=round(monthly_cost_twd / HOURLY_TWD, 1),
        ),
        periods=periods,
        monthly=monthly_series,
        billing=[dict(date=d, amount=a, plan=p) for d, a, p in BILLING],
    )

    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print('Saved:', OUT)
    for p in periods:
        print('{:<14} {} ~ {} {:>4}d  total {:>5} (work {:>4}) {:>6}/day  active {:>4}/{:<4} ({:>5}%)  cost ${:>8}  {:>7}/commit'.format(
            p['name'], p['start'], p['end'], p['days'], p['totalCommits'], p['workCommits'],
            p['dailyAverage'], p['activeDays'], p['days'], p['activeRatio'], p['cost'], p['costPerCommit']))
    print('overall:', json.dumps(output['overall'], ensure_ascii=False))


if __name__ == '__main__':
    main()

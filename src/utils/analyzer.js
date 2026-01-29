/**
 * Commits 分析工具
 */

// 功能分組規則
const FEATURE_PATTERNS = [
  {
    name: 'Push 通知系統',
    icon: '🔔',
    keywords: ['push', 'notification', 'vapid', 'service worker', 'sw.js', '通知', '訂閱'],
    subgroups: [
      { name: '核心實作', keywords: ['實作', 'webpush', 'vapid', 'service worker', '註冊', '訂閱按鈕'] },
      { name: '相容性修正', keywords: ['兼容', 'framework', 'bouncycastle', 'ecdsa', 'cng'] },
      { name: '功能完善', keywords: ['跨域', 'email', '收檢員', '代班', '重新訂閱'] },
      { name: '文檔與優化', keywords: ['文檔', '指南', '說明', '重構'] },
      { name: 'iOS 支援', keywords: ['ios', 'iphone', '瀏覽器', '設定指引'] },
      { name: '診斷工具', keywords: ['診斷', '狀態檢查', '可視化', '收合'] }
    ]
  },
  {
    name: '收檢系統',
    icon: '⭐',
    keywords: ['收檢', 'lt257', 'inspection'],
    subgroups: [
      { name: '系統重構', keywords: ['重構', 'ui', 'ux', '優化', '手機版'] },
      { name: '行政確認功能', keywords: ['行政', '確認', '篩選', '狀態'] },
      { name: '代班功能', keywords: ['代班', 'modal', '按鈕'] },
      { name: '收檢員維護', keywords: ['收檢員', '路線', '電話'] },
      { name: '編碼修正', keywords: ['utf-8', 'bom', '編碼', '字串'] }
    ]
  },
  {
    name: 'BT201 檢驗單系統',
    icon: '💼',
    keywords: ['bt201', '申報', '智能'],
    subgroups: [
      { name: '申報畫面', keywords: ['申報', '智能', '自動', '身分證', '病歷號', '個資', '醫師', '預防保健', 'f10'] },
      { name: '檢驗單功能', keywords: ['列印', '份數', '單位', '開立'] }
    ]
  },
  {
    name: '效能優化',
    icon: '⚡',
    keywords: ['效能', '優化', 'performance', 'perf:'],
    subgroups: [
      { name: '查詢優化', keywords: ['lt257', 'lt277', 'sql', '編譯'] }
    ]
  },
  {
    name: 'FalconCopy 資料同步',
    icon: '🔄',
    keywords: ['falconcopy', 'sync', '同步', 'pat_resultd', 'trx_num', '桃園'],
    subgroups: [
      { name: '同步邏輯', keywords: ['同步', 'pat_resultd', 'trx_num', 'reported_dt', '髒資料'] },
      { name: '欄位處理', keywords: ['欄位', '截斷', '長度', '日誌'] },
      { name: '資料遷移', keywords: ['遷移', '遷徙', '全量', 'sql', '腳本'] },
      { name: '診斷工具', keywords: ['診斷', '重置', '輔助'] },
      { name: '文檔整理', keywords: ['文檔', '文件', '目錄', '整理', '清理'] }
    ]
  }
]

/**
 * 將 commits 按功能分組
 */
export function groupCommitsByFeature(commits) {
  const grouped = {}
  const ungrouped = []

  for (const commit of commits) {
    const text = `${commit.message} ${commit.body || ''}`.toLowerCase()
    let matched = false

    for (const pattern of FEATURE_PATTERNS) {
      if (pattern.keywords.some(kw => text.includes(kw))) {
        if (!grouped[pattern.name]) {
          grouped[pattern.name] = {
            ...pattern,
            commits: [],
            subgroups: {}
          }
        }

        let subgroupMatched = false
        for (const subgroup of pattern.subgroups) {
          if (subgroup.keywords.some(kw => text.includes(kw))) {
            if (!grouped[pattern.name].subgroups[subgroup.name]) {
              grouped[pattern.name].subgroups[subgroup.name] = []
            }
            grouped[pattern.name].subgroups[subgroup.name].push(commit)
            subgroupMatched = true
            break
          }
        }

        if (!subgroupMatched) {
          grouped[pattern.name].commits.push(commit)
        }

        matched = true
        break
      }
    }

    if (!matched) {
      ungrouped.push(commit)
    }
  }

  return { grouped, ungrouped }
}

/**
 * 分析時間分布
 */
export function analyzeTimeDistribution(commits) {
  const byDate = {}

  commits.forEach(commit => {
    const date = commit.date
    byDate[date] = (byDate[date] || 0) + 1
  })

  const sorted = Object.entries(byDate).sort((a, b) => b[1] - a[1])

  return {
    byDate,
    peak: sorted[0] || null,
    secondPeak: sorted[1] || null
  }
}

/**
 * 清理 commit message（移除前綴）
 */
export function cleanCommitMessage(message) {
  return message.replace(/^(feat|fix|refactor|docs|style|test|chore|perf|build|ci|debug):\s*/i, '')
}

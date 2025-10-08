#!/usr/bin/env node

import { readFileSync, writeFileSync } from 'fs';
import { join } from 'path';

/**
 * 智能分析 commits 並生成精美報告
 */

// 關鍵字分組規則
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
    name: 'BT201 申報畫面智能化',
    icon: '💼',
    keywords: ['bt201', '申報', '智能'],
    subgroups: [
      { name: '自動化功能', keywords: ['自動', '身分證', '病歷號', '個資', '醫師', '預防保健', 'f10'] }
    ]
  },
  {
    name: '效能優化',
    icon: '⚡',
    keywords: ['效能', '優化', 'performance', 'sql', '查詢'],
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
];

/**
 * 將 commits 按功能分組
 */
function groupCommitsByFeature(commits) {
  const grouped = {};
  const ungrouped = [];

  for (const commit of commits) {
    const text = `${commit.message} ${commit.body}`.toLowerCase();
    let matched = false;

    for (const pattern of FEATURE_PATTERNS) {
      // 檢查是否匹配主要功能
      if (pattern.keywords.some(kw => text.includes(kw))) {
        if (!grouped[pattern.name]) {
          grouped[pattern.name] = {
            ...pattern,
            commits: [],
            subgroups: {}
          };
        }

        // 嘗試匹配子分組
        let subgroupMatched = false;
        for (const subgroup of pattern.subgroups) {
          if (subgroup.keywords.some(kw => text.includes(kw))) {
            if (!grouped[pattern.name].subgroups[subgroup.name]) {
              grouped[pattern.name].subgroups[subgroup.name] = [];
            }
            grouped[pattern.name].subgroups[subgroup.name].push(commit);
            subgroupMatched = true;
            break;
          }
        }

        if (!subgroupMatched) {
          grouped[pattern.name].commits.push(commit);
        }

        matched = true;
        break;
      }
    }

    if (!matched) {
      ungrouped.push(commit);
    }
  }

  return { grouped, ungrouped };
}

/**
 * 分析時間分布
 */
function analyzeTimeDistribution(commits) {
  const byDate = {};

  commits.forEach(commit => {
    const date = commit.date;
    byDate[date] = (byDate[date] || 0) + 1;
  });

  // 找出高峰日
  const sorted = Object.entries(byDate).sort((a, b) => b[1] - a[1]);

  return {
    byDate,
    peak: sorted[0] || null,
    secondPeak: sorted[1] || null
  };
}

/**
 * 生成精美報告
 */
function generateReport(data, startDate, endDate) {
  const filteredProjects = data.projects.map(project => {
    const filteredCommits = project.commits.filter(commit => {
      const commitDate = new Date(commit.date);
      const start = startDate ? new Date(startDate) : null;
      const end = endDate ? new Date(endDate) : null;

      if (start && commitDate < start) return false;
      if (end && commitDate > end) return false;
      return true;
    });

    return {
      ...project,
      commits: filteredCommits,
      totalCommits: filteredCommits.length
    };
  }).filter(p => p.totalCommits > 0);

  const totalCommits = filteredProjects.reduce((sum, p) => sum + p.totalCommits, 0);

  let report = `# 📊 您的工作成果（${data.author}）- ${startDate || '開始'} 至 ${endDate || '今天'}\n\n`;

  // 總覽統計
  report += `## 📈 總覽統計\n\n`;
  filteredProjects.forEach(project => {
    const percentage = Math.round((project.totalCommits / totalCommits) * 100);
    report += `* **${project.name}**: ${project.totalCommits} 次提交 (${percentage}%)\n`;
  });
  report += `* **總計**: ${totalCommits} 次有效提交\n\n`;

  // 各專案成果
  filteredProjects.forEach(project => {
    report += `## 🎯 ${project.name} 專案成果（${project.totalCommits} commits）\n\n`;

    const { grouped, ungrouped } = groupCommitsByFeature(project.commits);

    let featureIndex = 1;
    Object.values(grouped).forEach(feature => {
      const featureCommits = [
        ...feature.commits,
        ...Object.values(feature.subgroups).flat()
      ];

      if (featureCommits.length === 0) return;

      // 找出時間範圍
      const dates = featureCommits.map(c => c.date).sort();
      const dateRange = dates.length > 1 ? `${dates[0]} 至 ${dates[dates.length - 1]}` : dates[0];

      report += `### ${featureIndex}. ${feature.name} ${feature.icon} (${dateRange})\n\n`;
      report += `**${featureCommits.length} 次提交**\n\n`;

      // 子分組
      Object.entries(feature.subgroups).forEach(([subgroupName, commits]) => {
        if (commits.length === 0) return;

        const subDates = commits.map(c => c.date).sort();
        const subDateRange = subDates.length > 1
          ? `(${subDates[0]} 至 ${subDates[subDates.length - 1]})`
          : `(${subDates[0]})`;

        report += `#### ${subgroupName} ${subDateRange}\n\n`;

        // 提煉關鍵點（取前5個commit的message）
        commits.slice(0, 5).forEach(commit => {
          const msg = commit.message.replace(/^(feat|fix|refactor|docs|style|test|chore|perf|build|ci|debug):\s*/i, '');
          report += `* ${msg}\n`;
        });

        if (commits.length > 5) {
          report += `* ... 以及其他 ${commits.length - 5} 項改進\n`;
        }

        report += `\n`;
      });

      featureIndex++;
    });

    // 其他功能
    if (ungrouped.length > 0) {
      report += `### ${featureIndex}. 其他重要功能\n\n`;
      report += `**${ungrouped.length} 次提交**\n\n`;

      // 按分類分組
      const byCategory = {};
      ungrouped.forEach(commit => {
        const cat = commit.category || '其他';
        if (!byCategory[cat]) byCategory[cat] = [];
        byCategory[cat].push(commit);
      });

      Object.entries(byCategory).forEach(([category, commits]) => {
        report += `#### ${category} (${commits.length})\n\n`;
        commits.slice(0, 5).forEach(commit => {
          const msg = commit.message.replace(/^(feat|fix|refactor|docs|style|test|chore|perf|build|ci|debug):\s*/i, '');
          report += `* ${msg}\n`;
        });
        if (commits.length > 5) {
          report += `* ... 以及其他 ${commits.length - 5} 項\n`;
        }
        report += `\n`;
      });
    }

    report += `\n`;
  });

  // 工作分析
  const allCommits = filteredProjects.flatMap(p => p.commits);
  const timeAnalysis = analyzeTimeDistribution(allCommits);

  report += `## 📊 工作分析\n\n`;

  if (timeAnalysis.peak) {
    report += `### 提交密度\n\n`;
    report += `* 最高峰: ${timeAnalysis.peak[0]} (${timeAnalysis.peak[1]} commits) 🔥\n`;
    if (timeAnalysis.secondPeak) {
      report += `* 第二峰: ${timeAnalysis.secondPeak[0]} (${timeAnalysis.secondPeak[1]} commits)\n`;
    }
    report += `\n`;
  }

  // 分類統計
  const byCategory = {};
  allCommits.forEach(commit => {
    const cat = commit.category || '其他';
    byCategory[cat] = (byCategory[cat] || 0) + 1;
  });

  report += `### 功能分類\n\n`;
  Object.entries(byCategory)
    .sort((a, b) => b[1] - a[1])
    .forEach(([category, count]) => {
      const percentage = Math.round((count / totalCommits) * 100);
      report += `* ${category}: ${count} (${percentage}%)\n`;
    });

  report += `\n---\n\n`;
  report += `📅 報告生成時間: ${new Date().toISOString().split('T')[0]}\n`;

  return report;
}

/**
 * 主程式
 */
function main() {
  const args = process.argv.slice(2);

  let inputFile = 'public/data/work-log-2025-09-17-to-10-08.json';
  let outputFile = 'work-report.md';
  let startDate = null;
  let endDate = null;

  // 解析參數
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--input' && args[i + 1]) {
      inputFile = args[i + 1];
      i++;
    } else if (args[i] === '--output' && args[i + 1]) {
      outputFile = args[i + 1];
      i++;
    } else if (args[i] === '--since' && args[i + 1]) {
      startDate = args[i + 1];
      i++;
    } else if (args[i] === '--until' && args[i + 1]) {
      endDate = args[i + 1];
      i++;
    }
  }

  console.log('📊 分析工作成果...\n');
  console.log(`📂 輸入: ${inputFile}`);
  if (startDate) console.log(`📅 起始: ${startDate}`);
  if (endDate) console.log(`📅 結束: ${endDate}`);
  console.log('');

  // 讀取資料
  const data = JSON.parse(readFileSync(inputFile, 'utf-8'));

  // 生成報告
  const report = generateReport(data, startDate, endDate);

  // 儲存報告
  writeFileSync(outputFile, report, 'utf-8');

  console.log(`✅ 報告已生成: ${outputFile}\n`);
}

main();

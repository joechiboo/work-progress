#!/usr/bin/env node

import { execSync } from 'child_process';
import { readdirSync, statSync, writeFileSync } from 'fs';
import { join, basename } from 'path';

const CONFIG = {
  gitlabPath: 'D:\\Gitlab',
  author: 'UCL\\joechiboo',
  outputDir: './data',
  dateFormat: '%Y-%m-%d',
  encoding: 'utf-8'
};

/**
 * 取得所有 Git repositories
 */
function getGitRepos(basePath) {
  const repos = [];

  try {
    const items = readdirSync(basePath);

    for (const item of items) {
      const fullPath = join(basePath, item);

      try {
        const stat = statSync(fullPath);
        if (stat.isDirectory()) {
          const gitPath = join(fullPath, '.git');
          try {
            statSync(gitPath);
            repos.push({
              name: item,
              path: fullPath
            });
          } catch {
            // 不是 git repo，忽略
          }
        }
      } catch (err) {
        console.warn(`無法存取 ${fullPath}:`, err.message);
      }
    }
  } catch (err) {
    console.error(`無法讀取目錄 ${basePath}:`, err.message);
  }

  return repos;
}

/**
 * 執行 git log 並解析結果
 */
function getCommits(repoPath, author, since, until) {
  try {
    // Git log 格式: hash|date|subject|body
    const separator = '|||';
    const format = `%H${separator}%ad${separator}%s${separator}%b`;

    let cmd = `git -C "${repoPath}" log --author="${author}" --date=short --format="${format}"`;

    if (since) {
      cmd += ` --since="${since}"`;
    }
    if (until) {
      cmd += ` --until="${until}"`;
    }

    const output = execSync(cmd, {
      encoding: 'utf-8',
      maxBuffer: 10 * 1024 * 1024 // 10MB
    });

    if (!output.trim()) {
      return [];
    }

    const commits = [];
    const lines = output.trim().split('\n');

    for (const line of lines) {
      const [hash, date, subject, body] = line.split(separator);

      if (hash && date && subject) {
        commits.push({
          hash: hash.trim(),
          date: date.trim(),
          message: subject.trim(),
          body: body ? body.trim() : '',
          category: null,
          tags: []
        });
      }
    }

    return commits;
  } catch (err) {
    console.error(`抓取 commits 失敗 (${repoPath}):`, err.message);
    return [];
  }
}

/**
 * 自動分類 commit (基於關鍵字)
 */
function categorizeCommit(commit) {
  const message = commit.message.toLowerCase();
  const body = commit.body.toLowerCase();
  const text = `${message} ${body}`;

  // 定義分類規則
  const categories = {
    '功能開發': ['feat', 'feature', '新增', '實作', '完成'],
    '錯誤修正': ['fix', 'bug', 'hotfix', '修正', '修復', '除錯'],
    '重構': ['refactor', 'restructure', '重構', '優化'],
    '效能優化': ['perf', 'performance', '效能', '速度', '優化'],
    '文檔': ['docs', 'documentation', '文檔', '文件', '說明'],
    '測試': ['test', 'testing', '測試'],
    '樣式': ['style', 'ui', 'ux', 'css', '樣式', '介面'],
    '配置': ['config', 'setup', '配置', '設定'],
    '部署': ['deploy', 'release', '部署', '發布'],
    '其他': []
  };

  for (const [category, keywords] of Object.entries(categories)) {
    if (category === '其他') continue;

    for (const keyword of keywords) {
      if (text.includes(keyword)) {
        commit.category = category;
        return;
      }
    }
  }

  commit.category = '其他';
}

/**
 * 主程式
 */
function main() {
  const args = process.argv.slice(2);

  let since = null;
  let until = null;
  let output = null;

  // 解析參數
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--since' && args[i + 1]) {
      since = args[i + 1];
      i++;
    } else if (args[i] === '--until' && args[i + 1]) {
      until = args[i + 1];
      i++;
    } else if (args[i] === '--output' && args[i + 1]) {
      output = args[i + 1];
      i++;
    }
  }

  console.log('🔍 掃描 Git repositories...');
  console.log(`📂 路徑: ${CONFIG.gitlabPath}`);
  console.log(`👤 作者: ${CONFIG.author}`);
  if (since) console.log(`📅 起始: ${since}`);
  if (until) console.log(`📅 結束: ${until}`);
  console.log('');

  const repos = getGitRepos(CONFIG.gitlabPath);
  console.log(`找到 ${repos.length} 個 Git repositories\n`);

  const projects = [];
  let totalCommits = 0;

  for (const repo of repos) {
    console.log(`📦 處理 ${repo.name}...`);

    const commits = getCommits(repo.path, CONFIG.author, since, until);

    if (commits.length > 0) {
      // 自動分類
      commits.forEach(categorizeCommit);

      projects.push({
        name: repo.name,
        totalCommits: commits.length,
        commits: commits
      });

      totalCommits += commits.length;
      console.log(`   ✓ ${commits.length} 個 commits`);
    } else {
      console.log(`   - 無 commits`);
    }
  }

  console.log(`\n✅ 總計: ${totalCommits} 個 commits\n`);

  // 組裝 JSON
  const workLog = {
    period: {
      start: since || '(all)',
      end: until || new Date().toISOString().split('T')[0],
      weeks: since && until ? Math.ceil((new Date(until) - new Date(since)) / (7 * 24 * 60 * 60 * 1000)) : null
    },
    author: CONFIG.author,
    summary: {
      totalCommits: totalCommits,
      projectCount: projects.length,
      dailyAverage: null
    },
    projects: projects,
    generatedAt: new Date().toISOString()
  };

  // 儲存檔案
  const filename = output || `work-log-${since || 'all'}-to-${until || 'now'}.json`;
  const filepath = join(CONFIG.outputDir, filename);

  writeFileSync(filepath, JSON.stringify(workLog, null, 2), 'utf-8');
  console.log(`💾 已儲存: ${filepath}`);
}

main();

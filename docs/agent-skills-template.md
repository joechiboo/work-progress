# Agent Skills 架構模板

> 讓 AI 助手快速理解你的專案，提升協作效率

## 什麼是 Agent Skills？

Agent Skills 是一種專案文檔架構模式，透過標準化的目錄結構和入口文件，讓 AI 助手（如 Claude Code、GitHub Copilot）能夠快速理解專案脈絡，並有效執行任務。

## 核心概念

```
project/
├── .claude/
│   └── skills/
│       └── [skill-name]/
│           └── SKILL.md      ← AI 入口點（不進版控）
│
├── docs/                      ← 進版控，給人看也給 AI 看
│   ├── feature-a.md
│   └── feature-b.md
│
└── src/                       ← 實際程式碼
```

### 三層分離原則

| 層級 | 位置 | 進版控 | 對象 | 用途 |
|-----|------|-------|------|------|
| AI 入口 | `.claude/skills/` | ❌ | AI | 快速導航、上下文摘要 |
| 共享文檔 | `docs/` | ✅ | 人 + AI | 詳細說明、架構設計 |
| 程式碼 | `src/`, `scripts/` | ✅ | 人 + AI | 實際實作 |

## 快速開始

### 步驟 1：建立目錄結構

```bash
# 建立 skills 目錄
mkdir -p .claude/skills/[your-skill-name]

# 建立文檔目錄（如果還沒有）
mkdir -p docs
```

### 步驟 2：更新 .gitignore

在專案的 `.gitignore` 加入：

```gitignore
# Claude Code Skills (local AI context, not versioned)
.claude/skills/
```

### 步驟 3：建立 SKILL.md

複製以下模板到 `.claude/skills/[skill-name]/SKILL.md`：

```markdown
# [Skill Name] - 一句話描述

## 概述
此技能用於 [描述這個 skill 的主要功能]。

## 核心文件

### 文檔
- [文檔名稱](../../../docs/xxx.md) - 說明

### 程式碼
- [檔案名稱](../../../src/xxx.ts) - 說明

## 系統架構

[用 ASCII 或 Mermaid 畫出架構圖]

## 常用操作

### 操作一：[名稱]
```bash
command here
```

### 操作二：[名稱]
```bash
command here
```

## 重要設定

| 設定項 | 值 | 說明 |
|-------|---|------|
| XXX | YYY | ZZZ |

## 故障排除

### 問題：[問題描述]
- **原因**: ...
- **解法**: ...
```

## SKILL.md 撰寫指南

### 好的 SKILL.md 應該包含

1. **一句話概述** - AI 能快速理解這個 skill 做什麼
2. **核心文件連結** - 指向相關的 docs 和程式碼
3. **架構圖** - 視覺化系統結構
4. **常用操作** - 可直接複製執行的指令
5. **故障排除** - 常見問題的解決方案

### 撰寫原則

- **簡潔優先**：SKILL.md 是導航用，不是完整文檔
- **連結為主**：詳細內容放在 docs/，SKILL.md 只做指引
- **實用導向**：包含可執行的指令和範例
- **持續更新**：專案變動時同步更新 SKILL.md

## 範例：Daily Report Skill

```markdown
# Daily Report - 每日工作紀錄系統

## 概述
自動掃描本地 Git repositories，彙整 commit 紀錄生成每日工作報告。

## 核心文件

### 文檔
- [設定指南](../../../docs/setup-auto-daily-report.md)
- [部署文件](../../../docs/deploy.md)

### 腳本
- [auto-daily-report.py](../../../scripts/auto-daily-report.py)
- [run-daily-and-push.bat](../../../scripts/run-daily-and-push.bat)

## 系統架構

```
D:\Gitlab\          ─┐
D:\Personal\Project\ ─┼─→ auto-daily-report.py ─→ daily-reports/*.json
                     │                          └─→ public/data/work-log-latest.json
                     │                                      │
                     └─────────────────────────────────────→ Vue.js 前端
```

## 常用操作

### 手動執行
```bash
python scripts\auto-daily-report.py
```

### 生成今日報告
```bash
python scripts\auto-daily-report.py --today
```

## 故障排除

### 排程執行失敗 (Error 101)
- **原因**: Python 環境變數未載入
- **解法**: 使用 `cmd.exe /c` 包裝 bat 檔執行
```

## 多 Skill 專案

對於較大的專案，可以有多個 skills：

```
.claude/skills/
├── auth/
│   └── SKILL.md          # 認證系統
├── api/
│   └── SKILL.md          # API 開發
├── database/
│   └── SKILL.md          # 資料庫操作
└── deployment/
    └── SKILL.md          # 部署流程
```

## 為什麼 SKILL.md 不進版控？

1. **本地化彈性**：每個開發者可以依自己習慣調整
2. **保持乾淨**：避免 AI 相關文件污染 Git 歷史
3. **快速迭代**：可以隨時修改而不需要 commit
4. **文檔分離**：實際文檔在 `docs/`，團隊都看得到

## 與現有專案整合

如果專案已經有 `docs/` 或 `README.md`：

1. **不需要重寫**：SKILL.md 只是新增一個 AI 入口
2. **建立連結**：在 SKILL.md 中連結到現有文檔
3. **漸進式導入**：可以先建立一個 skill，之後再擴充

## FAQ

### Q: 每個專案都需要 Agent Skills 嗎？
A: 不一定。小型專案或結構簡單的專案可能不需要。當你發現每次請 AI 協助都要重複解釋專案結構時，就是導入的好時機。

### Q: SKILL.md 要寫多詳細？
A: 以「AI 能獨立完成任務」為目標。包含必要的上下文、檔案位置、常用指令即可，詳細說明放在 docs/。

### Q: 團隊成員需要自己建立 SKILL.md 嗎？
A: 可以提供 SKILL.template.md 讓團隊參考，但每個人可以依自己需求調整自己的版本。

### Q: 可以用在 Claude Code 以外的 AI 工具嗎？
A: 可以。這個架構模式是通用的，任何能讀取專案文件的 AI 助手都能受益。

---

## 相關資源

- [本專案的 SKILL.md 範例](../.claude/skills/daily-report/SKILL.md)
- [Agent Skills 架構指南](./agent-skills-guide.md)

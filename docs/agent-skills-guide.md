# Agent Skills 架構指南

## 概述

本專案採用 Agent Skills 架構模式，讓 AI 助手（如 Claude Code）能夠快速理解專案結構和執行相關任務。

## 目錄結構

```
project/
├── .claude/
│   └── skills/
│       └── [skill-name]/
│           └── SKILL.md      # AI 入口點（不進版控）
│
├── docs/                      # 進版控，給人看也給 AI 看
│   ├── setup-auto-daily-report.md
│   └── agent-skills-guide.md
│
└── scripts/                   # 實際程式碼
```

## 設計原則

### 1. SKILL.md 作為 AI 入口點
- 位於 `.claude/skills/[skill-name]/SKILL.md`
- 不進版控（在 .gitignore 中排除）
- 提供 AI 理解專案的快速途徑
- 指向 `docs/` 和 `scripts/` 中的實際檔案

### 2. docs/ 是共享文檔
- 進版控，團隊成員都可以看到
- 同時服務於人和 AI
- 包含設定指南、架構說明、故障排除

### 3. 分離關注點
- `SKILL.md`: AI 專用的導航和上下文
- `docs/`: 詳細的人類可讀文檔
- `scripts/`: 實際的程式碼實作

## 建立新 Skill

### 步驟 1: 建立目錄
```bash
mkdir -p .claude/skills/[skill-name]
```

### 步驟 2: 建立 SKILL.md
```markdown
# [Skill Name] - 簡短描述

## 概述
此技能用於...

## 核心文件
- [文檔1](../../../docs/xxx.md) - 說明
- [腳本1](../../../scripts/xxx.py) - 說明

## 常用操作
### 操作名稱
\`\`\`bash
command here
\`\`\`

## 故障排除
### 問題描述
- 原因: ...
- 解法: ...
```

### 步驟 3: 確認 .gitignore
確保 `.gitignore` 包含：
```
.claude/skills/
```

## 現有 Skills

| Skill 名稱 | 說明 | 路徑 |
|-----------|------|------|
| daily-report | 每日工作紀錄系統 | `.claude/skills/daily-report/` |

## 使用方式

當 Claude Code 或其他 AI 助手需要了解專案時，可以：
1. 閱讀對應的 `SKILL.md` 快速獲得上下文
2. 根據 SKILL.md 的指引找到相關文檔和程式碼
3. 執行常用操作或進行故障排除

## 為什麼不進版控？

`.claude/skills/` 不進版控的原因：
1. **本地化設定**: 每個開發者可能有不同的 AI 工具偏好
2. **避免污染**: 保持 Git 歷史乾淨
3. **靈活性**: 可以隨時調整而不影響團隊
4. **文檔分離**: 實際文檔在 `docs/` 中，SKILL.md 只是導航用

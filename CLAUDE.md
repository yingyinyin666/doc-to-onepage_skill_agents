# Claude Multi-Agent PM Configuration — doc-to-onepage

本文件为 Claude Code 在 `doc-to-onepage` 项目中的行为指南，遵循 Claude PM Framework 规范。

## 🧠 MANDATORY BEHAVIORAL CHECKLIST

□ **工作记录 = TrackDown** (`~/Projects/Claude-PM/trackdown/BACKLOG.md`)
□ **框架规范 = Claude PM** (`~/Projects/Claude-PM/framework/CLAUDE.md`)
□ **项目规格 = /docs/PROJECT.md**
□ **工作流程 = /docs/WORKFLOW.md**
□ **技术栈 = /docs/TOOLCHAIN.md**
□ **AI指令 = /docs/INSTRUCTIONS.md**

## 🎯 项目定位

**doc-to-onepage** 是一个多 Agent 协作技能，将任意文档转化为可决策的一页纸（OnePage）网页。

核心能力：文档解析 → 内容重构 → 视觉渲染 → 质量校验 → 分发交付

详见 `/docs/PROJECT.md`。

## 🤖 Agent 角色映射

本项目使用 **5个自定义 Agent**，映射到 claude-pm 标准角色如下：

| 本项目 Agent | claude-pm 角色 | Worktree | 核心职责 |
|------------|----------------|----------|---------|
| Document Analyst | Researcher | `doc-to-onepage-analyst` | 文档解析+模板推荐 |
| Content Architect | Architect | `doc-to-onepage-architect` | OnePage结构+内容填充 |
| Visual Designer | UI/UX | `doc-to-onepage-designer` | 风格决策+HTML生成 |
| QA Validator | QA | `doc-to-onepage-qa` | 质量校验+自动修复 |
| Publisher | DevOps | `doc-to-onepage-publisher` | 飞书写回+文件交付 |

每个 Agent 的详细规格见 `agents/` 目录。

## 🔄 Orchestrator 行为规范

作为 Orchestrator，Claude Code 必须：

1. **收到文档输入** → 立即启动 Document Analyst（Researcher worktree）
2. **Analyst 完成** → 启动 Content Architect（Architect worktree）；若有截图则同时启动 Visual Designer:analyze
3. **Architect 完成** → 向用户展示草稿，等待确认后启动 Visual Designer:build
4. **Visual Designer 完成** → 自动启动 QA Validator（无需用户确认）
5. **QA 通过** → 询问用户是否写回飞书，然后启动 Publisher

**禁止行为**：
- ❌ 不得跳过 QA Validator 直接交付
- ❌ 不得在用户未确认前写回飞书
- ❌ 不得越权修改其他 Agent 的输出文件（通过 contracts/ 传递）

## 📁 关键路径

```
~/Projects/managed/doc-to-onepage/    ← 主项目目录（Orchestrator）
~/Projects/managed/doc-to-onepage-analyst/    ← Document Analyst worktree
~/Projects/managed/doc-to-onepage-architect/  ← Content Architect worktree
~/Projects/managed/doc-to-onepage-designer/   ← Visual Designer worktree
~/Projects/managed/doc-to-onepage-qa/         ← QA Validator worktree
~/Projects/managed/doc-to-onepage-publisher/  ← Publisher worktree
```

## TrackDown 集成

所有工作项通过 TrackDown 追踪，格式：`M01-XXX`

- 分支命名：`task/M01-XXX-brief-description`
- 提交格式：`feat: description (closes M01-XXX)`

# Development Workflow — doc-to-onepage

## 🎯 Multi-Agent Execution Workflow

### Standard Run（无截图）

```
Step 1  [Orchestrator] 接收用户输入，解析文档来源
Step 2  [Document Analyst] 读取文档，输出 contracts/parsed_content.json
Step 3  [Orchestrator] 向用户展示模板推荐，确认模式（OnePage重构/保留原文）
Step 4  [Content Architect] 生成 OnePage 草稿，输出 onepage_draft.md + onepage_data.json
Step 5  [Orchestrator] 向用户展示草稿，多轮修改
Step 6  [Orchestrator] 询问风格偏好
Step 7  [Visual Designer] 生成 HTML，输出 output/web/index.html
Step 8  [QA Validator] 校验+修复，输出 qa_report.json
Step 9  [Orchestrator] 询问是否写回飞书
Step 10 [Publisher] 交付（可选写飞书 + 本地 HTML）
```

### Parallel Run（有截图）

```
Step 1  [Orchestrator] 接收文档 + 截图
Step 2  并行启动：
        ├── [Document Analyst] → parsed_content.json
        └── [Visual Designer:analyze] → custom_style.json
Step 3  等待两者完成
Step 4  [Content Architect] → onepage_data.json
Step 5  [Visual Designer:build]（content + style 就绪）→ index.html
Step 6  [QA Validator] → qa_report.json
Step 7  [Publisher] → delivery.json
```

### Revision Run（用户要求修改）

```
修改文字/结构 → 退回 Content Architect → Visual Designer → QA → Publisher
修改视觉风格  → 退回 Visual Designer → QA → Publisher
微调内容细节  → Orchestrator 直接修改 → Visual Designer → QA → Publisher
```

## 📋 TrackDown 集成

### Ticket 前缀规范

| 前缀 | 含义 | 示例 |
|------|------|------|
| `FEAT-` | 新功能 | FEAT-001 添加 PPT 格式支持 |
| `FIX-` | Bug 修复 | FIX-002 修复飞书鉴权超时 |
| `REF-` | 重构 | REF-003 优化 HTML 渲染性能 |
| `DOC-` | 文档 | DOC-004 更新 API 文档 |

### Branch 命名

```bash
feature/FEAT-001-ppt-support
fix/FIX-002-lark-auth-timeout
task/M01-XXX-description        # claude-pm 全局任务
```

### 提交规范

```bash
git commit -m "feat: 添加 PPT 解析支持 (closes FEAT-001)"
git commit -m "fix: 修复飞书 token 刷新逻辑 (closes FIX-002)"
```

## 🔄 Git Worktree 工作流

### 初始化（已完成）

```bash
cd ~/Projects/managed/doc-to-onepage
git worktree add ../doc-to-onepage-analyst main    # Document Analyst
git worktree add ../doc-to-onepage-architect main  # Content Architect
git worktree add ../doc-to-onepage-designer main   # Visual Designer
git worktree add ../doc-to-onepage-qa main         # QA Validator
git worktree add ../doc-to-onepage-publisher main  # Publisher
```

### Agent 工作目录

| Agent | 工作目录 | 可写文件 |
|-------|---------|---------|
| Orchestrator | `~/Projects/managed/doc-to-onepage/` | `contracts/*.json`, `SKILL.md` |
| Document Analyst | `doc-to-onepage-analyst/` | `contracts/parsed_content.json` |
| Content Architect | `doc-to-onepage-architect/` | `contracts/onepage_draft.md`, `contracts/onepage_data.json` |
| Visual Designer | `doc-to-onepage-designer/` | `contracts/custom_style.json`, `output/web/` |
| QA Validator | `doc-to-onepage-qa/` | `contracts/qa_report.json`, `output/web/index.html` |
| Publisher | `doc-to-onepage-publisher/` | `contracts/delivery.json` |

### 合并规范

每个 Agent 完成任务后，其输出文件由 Orchestrator 通过 PR 合并到 main：

```bash
# 在 worktree 分支上提交
cd ~/Projects/managed/doc-to-onepage-analyst
git add contracts/parsed_content.json
git commit -m "chore: document analysis output for task/FEAT-XXX"

# Orchestrator 合并
cd ~/Projects/managed/doc-to-onepage
git merge doc-to-onepage-analyst/main --no-ff
```

## 🚨 Quality Gates

| Gate | 触发时机 | 通过标准 |
|------|---------|---------|
| Content Gate | Content Architect 完成后 | 有结论+CTA+风险，章节数 4-6 |
| Visual Gate | Visual Designer 完成后 | HTML < 80KB，样式加载成功 |
| QA Gate | QA Validator 完成后 | 评分 ≥ 80 |
| Delivery Gate | Publisher 前 | QA 通过 + 用户同意 |

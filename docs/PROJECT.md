# Project Specification — doc-to-onepage

## 🎯 Mission

将任意文档（飞书/Word/PDF/聊天记录）转化为**可决策的一页纸（OnePage）**，生成可直接用于汇报的网页与飞书文档。

**帮用户把"信息"变成"说服力"。**

## 🏗️ Architecture

### Multi-Agent Pipeline

```
[用户输入：文档 + (可选)截图 + 风格偏好]
        ↓
[Orchestrator] — 协调所有 Agent，与用户沟通
        │
        ├─[1] Document Analyst ──────────────→ contracts/parsed_content.json
        │      (Researcher worktree)
        │              ↓
        ├─[2] Content Architect ─────────────→ contracts/onepage_draft.md
        │      (Architect worktree)             contracts/onepage_data.json
        │
        │      (若有截图，与[2]并行)
        ├─[2'] Visual Designer:analyze ──────→ contracts/custom_style.json
        │       (Designer worktree)
        │
        ├─[3] Visual Designer:build ─────────→ output/web/index.html
        │      (Designer worktree)
        │
        ├─[4] QA Validator ──────────────────→ contracts/qa_report.json
        │      (QA worktree)
        │
        └─[5] Publisher (用户同意后) ─────────→ contracts/delivery.json
               (Publisher worktree)
```

### 数据契约（contracts/）

| 文件 | 生产者 | 消费者 |
|------|--------|--------|
| `parsed_content.json` | Document Analyst | Content Architect |
| `onepage_draft.md` | Content Architect | Publisher |
| `onepage_data.json` | Content Architect | Visual Designer |
| `custom_style.json` | Visual Designer:analyze | Visual Designer:build |
| `qa_report.json` | QA Validator | Orchestrator/Publisher |
| `delivery.json` | Publisher | Orchestrator |

## 🔧 Technology Stack

- **Python 3.7+** — 所有脚本
- **Anthropic SDK** — Claude Vision（图片风格分析）
- **lark-cli** (`@larksuite/cli@1.0.4`) — 飞书文档读写
- **PyPDF2** — PDF 处理
- **python-docx** — Word 处理
- **playwright** （可选）— 截图校验

## 📂 Directory Structure

```
doc-to-onepage/
├── CLAUDE.md              # claude-pm 配置（本文件同级）
├── SKILL.md               # Orchestrator 行为指南
├── agents/                # 各 Agent 角色定义
│   ├── document-analyst.md
│   ├── content-architect.md
│   ├── visual-designer.md
│   ├── qa-validator.md
│   └── publisher.md
├── contracts/             # Agent 间数据契约（运行时生成）
│   └── README.md
├── scripts/               # 功能脚本
│   ├── read_lark_doc.py
│   ├── process_document.py
│   ├── recommend_template.py
│   ├── generate_onepage.py
│   ├── export_onepage_json.py
│   ├── build_web_onepage.py
│   ├── analyze_style_from_image.py
│   ├── validate_onepage.py
│   ├── screenshot_validator.py
│   ├── create_lark_doc.py
│   └── deploy_web.py
├── docs/                  # claude-pm 文档
├── output/                # 生成产物（运行时）
└── reference/             # 参考文档
```

## 🎨 模板体系（9种）

| 模板 | 适用场景 |
|------|----------|
| `decision-report` | 高层汇报/决策申请 |
| `product-solution` | 产品方案/BRD |
| `project-progress` | 项目进展/周报 |
| `governance-improvement` | 专项治理/体验优化 |
| `holiday-support` | 大促/节假日保障 |
| `product-tool` | 工具/系统建设 |
| `project-management` | 长周期项目/能力建设 |
| `team-intro` | 团队介绍/协作地图 |
| `personal-review` | 个人述职/阶段性总结 |

## 🚦 Current Status

- ✅ 单 Agent 版本（scripts/ 全部可用）
- ✅ 多 Agent 架构定义（agents/ + contracts/）
- ✅ 图片风格逆推（analyze_style_from_image.py）
- ✅ claude-pm 集成（CLAUDE.md + docs/ + worktrees）
- 🔄 TrackDown 工作流集成（进行中）

# Agent 数据契约

本目录存放各 Agent 之间传递的中间数据文件。每个文件是一个特定 Agent 的输出，作为下游 Agent 的输入。

## 文件列表

| 文件 | 生产者 | 消费者 | 说明 |
|------|--------|--------|------|
| `parsed_content.json` | document-analyst | content-architect | 文档解析结果 + 模板推荐 |
| `onepage_draft.md` | content-architect | visual-designer, publisher | OnePage Markdown 正文 |
| `onepage_data.json` | content-architect | visual-designer | 结构化 JSON，供 build_web 使用 |
| `custom_style.json` | visual-designer (analyze) | visual-designer (build) | 截图逆推的自定义风格 |
| `web_build.json` | visual-designer | qa-validator | 构建元数据 |
| `qa_report.json` | qa-validator | orchestrator, publisher | 质量报告 |
| `delivery.json` | publisher | orchestrator | 交付清单 |

## 数据流图

```
[用户输入]
    ↓
[document-analyst] ──→ parsed_content.json
    ↓                           ↓
    │                  [content-architect] ──→ onepage_draft.md
    │                                    └──→ onepage_data.json
    │                                              ↓
    └── (若有截图) [visual-designer:analyze] ──→ custom_style.json
                                                   ↓
                              [visual-designer:build] ──→ output/web/index.html
                                                              ↓
                                         [qa-validator] ──→ qa_report.json
                                                              ↓
                                            [publisher] ──→ delivery.json
```

## 并行执行节点

当用户提供截图时，以下两个任务可**并行**启动：
- `content-architect`（等待 `parsed_content.json`）
- `visual-designer:analyze`（立即启动，只需截图文件）

两者都完成后，`visual-designer:build` 才能启动。

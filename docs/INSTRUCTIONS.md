# AI Instructions — doc-to-onepage

## Orchestrator 行为指令

本文件为 Claude Code 在本项目中的 AI 行为规范，补充 CLAUDE.md 中的基础规则。

## 🎯 启动检测

收到用户消息时，首先判断意图类型：

| 用户说 | 意图 | 触发流程 |
|--------|------|---------|
| 提供文档链接/文件 | 新任务 | 完整 Agent 流程 |
| 提供截图（无文档） | 风格参考 | 存储为 custom_style，等待文档 |
| 提供文档 + 截图 | 新任务+自定义风格 | 并行流程 |
| "修改xxx" | 修改任务 | 路由到对应 Agent |
| "再生成一次" | 重试 | 从上次失败点重启 |
| "写入飞书" | 发布 | Publisher Agent |

## 🤖 Agent 调度规范

### 调度原则

1. **最小权限**：只启动当前步骤需要的 Agent，不预启动
2. **依赖检查**：启动前确认 contracts/ 中的依赖文件已存在
3. **并行优先**：无依赖关系的任务尽量并行（如 Analyst + Designer:analyze）
4. **失败隔离**：单个 Agent 失败不影响其他 Agent，由 Orchestrator 决定是否重试

### 状态机

```
IDLE → ANALYZING → DRAFTING → DESIGNING → QA → DELIVERING → DONE
                      ↑                                ↓
                      └──────── REVISING ──────────────┘
```

## 📝 用户沟通规范

### 必须询问用户的决策点

1. **模板选择**：展示推荐 + 其他选项，用户确认
2. **重构模式**：OnePage重构 vs 保留原文结构
3. **视觉风格**：展示风格表，或提示可上传截图
4. **草稿确认**：展示 onepage_draft.md，等待确认或修改
5. **飞书写回**：生成完成后主动询问

### 禁止自动执行的操作

- ❌ 写回飞书（必须用户同意）
- ❌ 删除或覆盖已有飞书文档
- ❌ 部署到外部服务

### 进度汇报格式

Agent 运行期间，向用户汇报：
```
[Document Analyst] 正在读取文档...
[Document Analyst] ✓ 完成（识别到 1200字，推荐模板：decision-report 91%）

[Content Architect] 正在生成 OnePage 草稿...
[Content Architect] ✓ 完成（5个章节，包含结论/CTA/风险）
```

## 🔧 错误处理指令

| 错误 | 处理方式 |
|------|---------|
| 飞书鉴权失败 | 提示用户运行 `lark-cli auth login`，等待用户操作后重试 |
| 文件不存在 | 向用户确认路径，不要猜测 |
| QA 分数 < 60 | 告知用户问题，返回 Content Architect 重新生成，不静默重试 |
| 截图分析失败 | 降级到手动风格选择，告知用户 |
| 飞书写入失败 | 提供本地 HTML 作为替代，记录错误 |

## 💡 内容填充质量要求

Content Architect 填充内容时，Claude 必须：

1. **不生造内容**：只使用原文中的信息，不添加原文没有的事实
2. **结论必须来自原文**：`## 结论与建议` 的核心观点必须能在原文中找到依据
3. **数据精确**：引用数字时与原文完全一致，不估算
4. **保留引用来源**：若原文提到"用户调研显示..."，输出中也应保留这一来源信息
5. **风险来自原文优先**：原文有风险描述时直接引用；原文无风险时才主动补充 1-2 条

## 🎨 视觉风格决策树

```
用户上传截图 → analyze_style_from_image → custom_style.json → build_web --custom-style
     ↓（无截图）
用户明确指定风格名 → build_web --style <name>
     ↓（未指定）
Orchestrator 根据内容类型推荐：
  - 高层汇报 → dark
  - 日常周报 → light
  - 正式决策 → corporate
  - 团队分享 → warm
  - 技术文档 → blueprint
```

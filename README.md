# doc-to-onepage Skill

**将任意文档转化为"可决策的一页纸（OnePage）"**，并生成可直接用于汇报的网页与飞书文档。

> 帮你把"信息"变成"说服力"。

## 核心能力

- **内容重构**：从"信息堆积" → "结论优先"
- **信息压缩**：将长文压缩为1页可读完、3分钟可讲清
- **可视化增强**：自动识别数据指标、流程步骤、优先级等，渲染为 Metric 大数卡片、流程图、Badge 等组件
- **汇报增强**：汇报开场句、结论总结句、Q&A预判

## 使用方式

这是一个 [Claude Code](https://claude.ai/code) 的 Skill，安装后可通过自然语言调用：

```
用户: /doc-to-onepage 帮我把这个飞书文档整理成 onepage
```

### 安装

将本仓库克隆到你的项目 `.claude/skills/` 目录下：

```bash
mkdir -p .claude/skills
cd .claude/skills
git clone https://github.com/yingyinyin666/doc-to-onepage_skill.git doc-to-onepage
```

### 工作流程

```
1. 解析文档（飞书/Word/PDF/Markdown/聊天记录）
2. AI 推荐最优模板（8种模板）
3. 生成 OnePage 初稿（Claude 主动填充内容）
4. 创建飞书文档
5. 支持多轮修改
6. 生成网页版本（4种视觉风格）
7. 自检与自修复（确保汇报质量）
```

## 可视化组件

V2 版本自动识别内容类型，渲染为可视化组件：

| 组件 | 触发条件 | 效果 |
|------|----------|------|
| Metric 大数卡片 | 文本含 2+ 个加粗数字 | 网格布局大数字 + 数字滚动动画 |
| Flow 流程图 | 有序列表 | 竖向时间轴 + 节点 + 卡片 |
| Journey 旅程线 | 含旅程关键词的列表 | 彩色节点 + 连线 + 阶段卡片 |
| Priority Badge | 表格含 P00/P0/P1 | 红/橙/黄色标签 |
| Risk Level | 表格含风险等级 | 带颜色圆点的风险指示器 |
| CTA 决策框 | 结论区加粗问句 | 独立高亮决策卡片 |

## 视觉风格

| 风格 | 适用场景 |
|------|----------|
| `dark` | 高层汇报、产品评审（暗色背景 + 毛玻璃 + 光晕） |
| `light` | 日常周报、团队分享（白色背景 + 蓝色强调） |
| `corporate` | 正式决策、跨部门汇报（深蓝顶部 + 严谨排版） |
| `warm` | 团队介绍、项目复盘（米色背景 + 暖棕色调） |

## 模板体系（8种）

| 模板 | 适用场景 |
|------|----------|
| `decision-report` | 高层汇报 / 决策申请 |
| `product-solution` | 产品方案 / BRD |
| `project-progress` | 项目进展 / 周报 |
| `governance-improvement` | 专项治理 / 体验优化 |
| `holiday-support` | 大促 / 节假日保障 |
| `product-tool` | 工具 / 系统建设 |
| `project-management` | 长周期项目 / 能力建设 |
| `team-intro` | 团队介绍 / 协作地图 |

## 目录结构

```
doc-to-onepage/
├── SKILL.md              # Skill 定义（Claude Code 读取）
├── scripts/              # 核心脚本
│   ├── build_web_onepage.py   # 网页版生成（V2 可视化增强）
│   ├── generate_onepage.py    # OnePage 初稿生成
│   ├── recommend_template.py  # 模板推荐
│   ├── validate_onepage.py    # 质量自检
│   ├── read_lark_doc.py       # 飞书文档读取
│   ├── create_lark_doc.py     # 飞书文档创建
│   └── templates/             # 8种模板文件
├── reference/            # 参考文档
├── examples/             # 使用示例
└── demo/                 # Demo 数据与输出
```

## License

MIT

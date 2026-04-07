# doc-to-onepage

> 将任意文档转化为**可决策的一页纸（OnePage）**，并生成可直接汇报的网页。  
> 帮你把"信息"变成"说服力"。

这是一个 [Claude Code Skill](https://docs.anthropic.com/en/docs/claude-code/skills)，可直接安装到你的 Claude Code 中使用。

---

## 安装

```bash
# 在 Claude Code 中执行
/plugin install github:yingyinyin666/doc-to-onepage_skill
```

安装后，向 Claude 发送文档链接或文件路径即可触发。

---

## 核心能力

### 输入支持
| 类型 | 处理方式 |
|------|----------|
| 飞书文档 URL | `lark-cli docs +fetch` 读取，`+media-download` 下载图片 |
| Word (.docx) | python-docx 解析 |
| PDF | PyPDF2 提取 |
| 聊天记录 | 微信 / 钉钉 / 通用格式 |
| Markdown / TXT | 直接读取 |

### 两种生成模式
- **OnePage 重构**（默认）：结论优先、信息压缩、汇报增强，适合对内容做结构化重组
- **保留原文结构**：用户说"直接用原文档"时，按原有章节生成网页，不强制套模板

### 9 种内容模板
`decision-report` / `product-solution` / `project-progress` / `governance-improvement` / `holiday-support` / `product-tool` / `project-management` / `team-intro` / `personal-review`

### 10 种视觉风格

**基础风格**

| 风格 | 适用场景 |
|------|----------|
| `dark` | 高层汇报、产品评审 |
| `light` | 日常周报、团队分享 |
| `corporate` | 正式决策、跨部门汇报 |
| `warm` | 团队介绍、项目复盘 |

**创意风格（物理隐喻）**

| 风格 | 视觉特点 |
|------|----------|
| `blueprint` | 蓝图网格 + 等宽字体，像建筑图纸 |
| `retro` | 高饱和色块 + 粗黑边框，活泼易传播 |
| `folder` | 蓝色文件夹 + 彩色标签页，专业有序 |
| `receipt` | 热敏纸质感 + 虚线分隔，简洁高效 |
| `scrapbook` | 牛皮纸 + 便签拼贴 + 红色图钉，温暖有思考感 |
| `dossier` | 软木板 + 金属夹 + URGENT 标签，像作战指挥室 |

### 6 种自动识别可视化组件
无需手动配置，自动检测内容类型并渲染：

| 组件 | 触发条件 |
|------|----------|
| Metric 大数卡片 | 文本含 2+ 个 `**数字%**` |
| Flow 流程图 | 有序列表（1. 2. 3.） |
| Journey 旅程线 | 含旅程关键词的无序列表 |
| Priority Badge | 表格中含独立的 P00/P0/P1 |
| Risk Level | 表格含风险等级 + 高/中/低 |
| CTA 决策框 | 结论区的 `**问句？**` |

### 图片支持
飞书文档中的图片通过 `lark-cli docs +media-download` 下载后，构建时自动以 **base64 内嵌**到 HTML，生成的网页是完全自包含的单文件，可直接分享。

### 质量自检与自修复
- **标准模式**（OnePage重构）：检查结论区 / CTA / 风险模块 / 模块数量 / 视觉层级 / 内容长度
- **宽松模式**（`--lenient`，保留原文结构时）：跳过结构性强制检查，只校验视觉质量

---

## 使用流程

```
用户提供文档
  ↓
解析文档 + 下载图片
  ↓
推荐模板 / 确认生成模式（重构 or 保留原文）
  ↓
Claude 填充 OnePage 内容
  ↓
询问视觉风格 + 受众
  ↓
生成网页（图片 base64 内嵌，单文件可分享）
  ↓
自检与自修复
  ↓
[可选] 写回飞书文档
```

---

## 脚本说明

| 脚本 | 功能 |
|------|------|
| `build_web_onepage.py` | 核心：生成 HTML 网页，支持 10 种风格 + 图片 base64 内嵌 |
| `export_onepage_json.py` | 将 OnePage Markdown 解析为结构化 JSON |
| `generate_onepage.py` | 从模板生成 OnePage 初稿 |
| `validate_onepage.py` | 质量自检 + 自动修复，支持 `--lenient` 宽松模式 |
| `recommend_template.py` | 基于关键词智能推荐模板 |
| `read_lark_doc.py` | 读取飞书文档（需 lark-cli 已登录） |
| `create_lark_doc.py` | 创建/更新飞书文档（可选步骤） |
| `screenshot_validator.py` | Playwright 截图视觉校验（可选） |

---

## 环境依赖

```bash
# 必须
pip install PyPDF2 python-docx   # PDF/Word 文档解析（可选，按需安装）

# 飞书集成（可选）
npm install -g @larksuite/cli
lark-cli config init --new
lark-cli auth login

# 截图校验（可选）
pip install playwright && playwright install chromium
```

---

## License

MIT

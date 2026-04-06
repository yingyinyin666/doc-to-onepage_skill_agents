# 脚本参考文档

## 文档处理脚本

### process_document.py

处理本地文档（PDF、Word、TXT），提取文本内容。

```bash
python3 scripts/process_document.py --file <文档路径> --output <输出路径>
```

**功能**：
- PDF文本提取（PyPDF2）
- Word文档解析（python-docx）
- Markdown/TXT直接读取
- 内容分析（标题、关键点、数据提取）

---

### process_chat.py

处理聊天记录，支持微信、钉钉等格式。

```bash
python3 scripts/process_chat.py --file <聊天记录文件> --type <类型> --output <输出路径>
```

**类型选项**：`wechat`、`dingtalk`、`generic`

**功能**：
- 解析聊天记录结构
- 提取参与者、时间、消息内容
- 分析关键话题、决策、行动项
- 转换为Markdown格式

---

### process_lark.py

处理飞书文档格式。

```bash
python3 scripts/process_lark.py --file <飞书文档> --output <输出路径>
```

**功能**：
- 解析飞书Markdown格式
- 提取章节结构
- 转换为标准Markdown

---

## AI能力脚本

### recommend_template.py

基于文档内容智能推荐模板。

```bash
python3 scripts/recommend_template.py --file <文档路径>
```

**输出示例**：
```
我分析了你的文档，推荐：

🥇 决策汇报型（匹配度 91%）
   → 命中关键词：决策, 方案, 资源

🥈 项目推进型（匹配度 72%）
```

---

## OnePage生成脚本

### generate_onepage.py

根据模板生成OnePage初稿。

```bash
python3 scripts/generate_onepage.py \
  --template <模板名> \
  --title "<标题>" \
  --refs "<参考文档>" \
  --output "<输出路径>"
```

**模板选项**：
- `decision-report` - 决策汇报型
- `product-solution` - 产品方案型
- `project-progress` - 项目推进型
- `governance-improvement` - 治理专项型
- `holiday-support` - 大促保障型
- `product-tool` - 产品工具型
- `project-management` - 项目管理型
- `team-intro` - 团队说明型

---

### apply_updates.py

应用用户的修改到OnePage文档。

```bash
python3 scripts/apply_updates.py --onepage <文档路径> --updates <更新JSON> --anchors <锚点>
```

**更新JSON格式**：
```json
{
  "章节名": "新的内容",
  "另一个章节": {"mode": "replace", "content": "替换内容"}
}
```

---

## 数据与网页脚本

### export_onepage_json.py

将Markdown格式的OnePage解析为结构化JSON。

```bash
python3 scripts/export_onepage_json.py \
  --onepage <OnePage文件> \
  --template <模板名> \
  --output <输出路径>
```

---

### build_web_onepage.py

构建网页版本的OnePage。

```bash
python3 scripts/build_web_onepage.py \
  --data <JSON数据> \
  --outdir <输出目录> \
  --style <视觉风格> \
  --animation <动效风格>
```

**风格选项**：
- `report` - 商务蓝（决策汇报）
- `tutorial` - 绿色（教程）
- `promotion` - 橙红渐变（宣传）
- `project` - 紫色（项目）
- `default` - 灰色（通用）

**动效选项**：
- `minimal` - 简洁fade-in
- `stagger` - 卡片错位
- `poster` - 缩放动画
- `default` - 默认

---

### validate_onepage.py

**OnePage 自检与自修复系统** - 在生成网页后，自动进行质量检查并自我优化。

```bash
python3 scripts/validate_onepage.py \
  --html <HTML文件> \
  --auto-fix \
  --output <输出路径>
```

**校验标准**：

| 检查项 | 权重 |
|--------|------|
| 结论优先 | 20分 |
| CTA行动号召 | 20分 |
| 风险说明 | 15分 |
| 模块数量 | 15分 |
| 视觉层级 | 15分 |
| 内容长度 | 15分 |

**自动修复能力**：
- 缺少结论区域 → 自动添加结论横幅
- 缺少风险模块 → 自动添加风险说明

---

### screenshot_validator.py

**OnePage 截图校验脚本** - 使用 Playwright 进行视觉质量检查。

```bash
python3 scripts/screenshot_validator.py \
  --html <HTML文件> \
  --screenshot <截图保存路径> \
  --analyze
```

**功能**：
- 使用无头浏览器生成页面截图
- 自动检测关键元素（结论区、CTA、标题层级）
- 分析模块数量和内容可见性
- 输出视觉质量评分

**视觉检查项**：
| 检查项 | 说明 |
|--------|------|
| 结论区域 | 是否存在结论横幅 |
| CTA按钮 | 是否有按钮或链接 |
| 标题层级 | H1≥1, H2≤5 |
| 模块数量 | sections≤8 |
| 内容可见性 | 内容是否正常渲染 |

**前置要求**：
```bash
pip install playwright
playwright install chromium
```

---

## 飞书集成脚本

### read_lark_doc.py

使用lark-cli读取飞书文档。

```bash
python3 scripts/read_lark_doc.py \
  --doc "<飞书文档URL或ID>" \
  --output <输出路径> \
  --format <格式>
```

**前置要求**：
```bash
npm install -g @larksuite/cli
lark-cli config init --new
lark-cli auth login
```

---

### create_lark_doc.py

创建或更新飞书文档。

```bash
# 创建新文档
python3 scripts/create_lark_doc.py create \
  --title "<标题>" \
  --content "<内容或文件路径>"

# 更新文档
python3 scripts/create_lark_doc.py update \
  --doc "<文档ID>" \
  --content "<新内容>"
```

---

## 部署脚本

### deploy_web.py

部署网页版本到指定平台。

```bash
python3 scripts/deploy_web.py \
  --dir <目录> \
  --output <ZIP输出路径> \
  --platform <平台>
```

**平台选项**：`netlify`、`vercel`、`surge`、`local`

---

## 环境要求

- Python 3.7+
- Node.js 16.0+（用于飞书CLI）
- pip install: PyPDF2, python-docx

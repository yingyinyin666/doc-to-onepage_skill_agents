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
- `personal-review` - 个人述职型

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

**风格选项**（`--style`）：

基础风格：
- `dark` - 暗色背景+毛玻璃+彩色光晕，高级感强（默认）
- `light` - 白色背景+淡灰卡片+蓝色强调，清爽易读
- `corporate` - 深蓝顶部+白色内容区+严谨排版，专业权威
- `warm` - 米色背景+暖棕色调+柔和阴影，亲和温暖

创意风格（物理隐喻）：
- `blueprint` - 蓝图网格+超细线条+等宽字体，像建筑图纸
- `retro` - 高饱和色块+粗黑边框+漫画分格，活泼易传播
- `folder` - 蓝色文件夹+金属夹子+白色纸张，专业有序
- `receipt` - 热敏纸质感+波浪边+虚线分隔，简洁高效
- `scrapbook` - 牛皮纸背景+便签拼贴+红色图钉，温暖有思考感
- `dossier` - 软木板纹理+金属夹+URGENT标签，像作战指挥室

**V2 可视化组件**（自动识别，无需额外参数）：
- Metric 大数卡片：检测到加粗数字时自动渲染
- Flow 流程图：有序列表自动转为时间轴
- Journey 旅程线：旅程类列表自动转为阶段卡片
- Priority Badge：表格中 P00/P0/P1 自动渲染为彩色标签
- Risk Level：风险等级表格中的高/中/低自动着色
- CTA 决策框：结论区加粗问句独立高亮展示

---

### validate_onepage.py

**OnePage V2 自检与自修复系统** - 在生成网页后，自动进行质量检查并自我优化。适配 V2 模板结构。

```bash
python3 scripts/validate_onepage.py \
  --html <HTML文件> \
  --auto-fix \
  --output <输出路径>
```

**校验标准**（V2）：

| 检查项 | 匹配方式 | 权重 |
|--------|----------|------|
| 结论优先 | `.conclusion` 区域 | 20分 |
| CTA行动号召 | `.conclusion-cta` 或决策问句 | 20分 |
| 风险说明 | `.sec-risk` 或 `.risk-level` | 15分 |
| 模块数量 | `.card` 数量 ≤ 8 | 15分 |
| 视觉层级 | metric/flow/timeline 等组件 | 15分 |
| 内容长度 | HTML < 80KB | 15分 |

**自动修复能力**：
- 缺少结论区域 → 自动插入 `.conclusion` 区域
- 缺少 CTA → 自动添加 `.conclusion-cta` 决策框
- 缺少风险模块 → 自动添加 `.sec-risk` 章节

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

**视觉检查项**（V2）：
| 检查项 | 说明 |
|--------|------|
| 结论区域 | `.conclusion` 是否存在 |
| CTA决策框 | `.conclusion-cta` 或加粗决策问句 |
| 标题层级 | H1≥1, card h2≤8 |
| 模块数量 | `.card` ≤ 8 |
| 可视化组件 | metric/flow/journey/badge/risk 数量 |
| 风险模块 | `.sec-risk` 是否存在 |
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

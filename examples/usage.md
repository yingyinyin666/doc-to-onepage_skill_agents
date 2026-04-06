# 使用示例

## 示例1：处理飞书文档

```bash
# 1. 读取飞书文档
python3 scripts/read_lark_doc.py \
  --doc "https://feishu.cn/docx/xxxxxx" \
  --output "./output/lark_content.md"

# 2. 推荐模板
python3 scripts/recommend_template.py --file ./output/lark_content.md

# 3. 生成OnePage
python3 scripts/generate_onepage.py \
  --template decision-report \
  --title "项目决策汇报" \
  --refs "./output/lark_content.md" \
  --output "./output/onepage.lark.md"

# 4. 创建飞书文档
python3 scripts/create_lark_doc.py create \
  --title "项目决策汇报" \
  --content "$(cat ./output/onepage.lark.md)"

# 5. 生成网页
python3 scripts/export_onepage_json.py \
  --onepage ./output/onepage.lark.md \
  --template decision-report \
  --output ./output/data.json

python3 scripts/build_web_onepage.py \
  --data ./output/data.json \
  --style report \
  --animation minimal \
  --outdir ./output/web
```

---

## 示例2：处理本地文档

```bash
# 处理PDF
python3 scripts/process_document.py \
  --file "./documents/report.pdf" \
  --output "./output/content.md"

# 推荐模板
python3 scripts/recommend_template.py --file ./output/content.md

# 生成OnePage
python3 scripts/generate_onepage.py \
  --template project-progress \
  --title "项目进展周报" \
  --refs "./output/content.md" \
  --output "./output/weekly_report.lark.md"
```

---

## 示例3：处理聊天记录

```bash
# 处理微信聊天记录
python3 scripts/process_chat.py \
  --file "./chat_history.txt" \
  --type wechat \
  --output "./output/chat_analysis.json"

# 基于聊天分析结果生成OnePage
python3 scripts/generate_onepage.py \
  --template team-intro \
  --title "会议纪要" \
  --refs "./output/chat_analysis.md" \
  --output "./output/meeting_notes.lark.md"
```

---

## 示例4：交互式修改

```bash
# 创建更新JSON
cat > ./updates.json << 'EOF'
{
  "背景": "补充市场分析数据",
  "方案对比": {"mode": "replace", "content": "新方案内容..."}
}
EOF

# 应用更新
python3 scripts/apply_updates.py \
  --onepage ./output/onepage.lark.md \
  --updates ./updates.json \
  --anchors "背景,方案对比"
```

---

## 示例5：使用不同风格和动效

```bash
# 决策汇报风格（极简动效）
python3 scripts/build_web_onepage.py \
  --data ./output/data.json \
  --style report \
  --animation minimal \
  --outdir ./output/web_report

# 项目推进风格（有节奏动效）
python3 scripts/build_web_onepage.py \
  --data ./output/data.json \
  --style project \
  --animation stagger \
  --outdir ./output/web_project

# 宣传海报风格（强化动效）
python3 scripts/build_web_onepage.py \
  --data ./output/data.json \
  --style promotion \
  --animation poster \
  --theme poster \
  --outdir ./output/web_poster
```

---

## 完整工作流示例

```
用户：帮我把这个飞书文档整理成 onepage
链接：https://feishu.cn/docx/xxxxxx

Agent执行：
1. read_lark_doc.py --doc "https://feishu.cn/docx/xxxxxx"
2. recommend_template.py --file ./output/lark_content.md
   → 推荐：决策汇报型（91%匹配）
3. generate_onepage.py --template decision-report --title "项目汇报"
4. create_lark_doc.py create --title "项目汇报"
5. 用户确认/修改
6. export_onepage_json.py + build_web_onepage.py
7. 交付：飞书链接 + 网页链接
```

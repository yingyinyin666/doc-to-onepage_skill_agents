# Toolchain — doc-to-onepage

## Runtime Dependencies

```bash
# Python
pip install anthropic PyPDF2 python-docx

# Node.js（飞书集成）
npm install -g @larksuite/cli@1.0.4

# 可选：截图校验
pip install playwright && playwright install chromium
```

## Environment Variables

```bash
export ANTHROPIC_API_KEY=sk-ant-xxx   # 图片风格分析（analyze_style_from_image.py）
```

## Script Inventory

### 文档处理层
| 脚本 | 调用者 | 功能 |
|------|--------|------|
| `read_lark_doc.py` | Document Analyst | 飞书文档 → Markdown |
| `process_document.py` | Document Analyst | PDF/Word/TXT → Markdown |
| `process_chat.py` | Document Analyst | 聊天记录 → Markdown |
| `process_lark.py` | Document Analyst | 飞书格式转换 |
| `recommend_template.py` | Document Analyst | 内容分析 → 模板推荐 |

### 内容生成层
| 脚本 | 调用者 | 功能 |
|------|--------|------|
| `generate_onepage.py` | Content Architect | 生成 Markdown 骨架 |
| `export_onepage_json.py` | Content Architect | Markdown → JSON |
| `apply_updates.py` | Content Architect | 应用修改 |

### 视觉渲染层
| 脚本 | 调用者 | 功能 |
|------|--------|------|
| `analyze_style_from_image.py` | Visual Designer | 截图 → custom_style.json |
| `build_web_onepage.py` | Visual Designer | JSON + style → HTML |

### 质量保障层
| 脚本 | 调用者 | 功能 |
|------|--------|------|
| `validate_onepage.py` | QA Validator | HTML 结构校验+自动修复 |
| `screenshot_validator.py` | QA Validator | Playwright 视觉校验 |

### 分发层
| 脚本 | 调用者 | 功能 |
|------|--------|------|
| `create_lark_doc.py` | Publisher | 创建/更新飞书文档 |
| `deploy_web.py` | Publisher | 打包/部署网页 |

## Key Commands

```bash
# 完整流程（Orchestrator 协调，各脚本由对应 Agent 调用）

# Document Analyst
lark-cli docs +fetch --doc <URL> --format pretty > tmp_content.md
python3 scripts/recommend_template.py --file tmp_content.md

# Content Architect
python3 scripts/generate_onepage.py --template decision-report --title "xxx" --refs tmp_content.md --output contracts/onepage_draft.md
python3 scripts/export_onepage_json.py --onepage contracts/onepage_draft.md --output contracts/onepage_data.json

# Visual Designer
python3 scripts/analyze_style_from_image.py --image screenshot.png --output contracts/custom_style.json
python3 scripts/build_web_onepage.py --data contracts/onepage_data.json --custom-style contracts/custom_style.json --outdir output/web
# OR
python3 scripts/build_web_onepage.py --data contracts/onepage_data.json --style dark --outdir output/web

# QA Validator
python3 scripts/validate_onepage.py --html output/web/index.html --auto-fix --output output/web/index.html
python3 scripts/validate_onepage.py --html output/web/index.html --lenient --output output/web/index.html  # 保留原文结构模式

# Publisher
python3 scripts/create_lark_doc.py create --title "xxx" --content contracts/onepage_draft.md
```

## Worktree Setup

```bash
cd ~/Projects/managed/doc-to-onepage
git worktree add ../doc-to-onepage-analyst main
git worktree add ../doc-to-onepage-architect main
git worktree add ../doc-to-onepage-designer main
git worktree add ../doc-to-onepage-qa main
git worktree add ../doc-to-onepage-publisher main
git worktree list  # 验证
```

#!/usr/bin/env python3
import argparse
import os
import re
from pathlib import Path

def get_skill_dir():
    return Path(__file__).parent.parent

def load_template(template_name):
    skill_dir = get_skill_dir()
    template_path = skill_dir / "scripts" / "templates" / f"{template_name}.lark.md"
    if not template_path.exists():
        raise FileNotFoundError(f"Template {template_name} not found: {template_path}")

    with open(template_path, 'r', encoding='utf-8') as f:
        return f.read()

def load_extra(extra_path):
    if not extra_path or not os.path.exists(extra_path):
        return ""

    with open(extra_path, 'r', encoding='utf-8') as f:
        return f.read()

def generate_onepage(template, refs, extra, output, title, audience, tone, include_tables):
    template_content = load_template(template)

    template_content = template_content.replace("{{title}}", title)

    ref_content = ""
    if refs:
        ref_files = refs.split(',')
        for ref_file in ref_files:
            ref_file = ref_file.strip()
            if os.path.exists(ref_file):
                with open(ref_file, 'r', encoding='utf-8') as f:
                    ref_content += f"\n\n# 参考文档: {os.path.basename(ref_file)}\n{f.read()}"

    extra_content = load_extra(extra)

    # 生成写作上下文提示，供 Claude 填充内容时参考
    context_hints = []
    if audience:
        context_hints.append(f"目标受众：{audience}")
    if tone:
        context_hints.append(f"写作风格：{tone}")
    if include_tables:
        context_hints.append("要求：关键对比内容使用 Markdown 表格呈现")

    final_content = template_content
    if context_hints:
        hints_block = "\n".join(f"- {h}" for h in context_hints)
        final_content = f"<!-- 写作要求\n{hints_block}\n-->\n\n" + final_content
    if extra_content:
        final_content += f"\n\n# 补充内容\n{extra_content}"
    if ref_content:
        final_content += ref_content

    parent = os.path.dirname(output)
    if parent and output != "./onepage_generated.lark.md":
        os.makedirs(parent, exist_ok=True)

    with open(output, 'w', encoding='utf-8') as f:
        f.write(final_content)

    print(f"Onepage generated successfully: {output}")
    if context_hints:
        print(f"Writing context: {'; '.join(context_hints)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Onepage document")
    parser.add_argument('--template', type=str, required=True, choices=[
        'decision-report',
        'product-solution',
        'project-progress',
        'governance-improvement',
        'holiday-support',
        'product-tool',
        'project-management',
        'team-intro'
    ], help='Template name')
    parser.add_argument('--refs', type=str, default="", help='Comma-separated list of reference documents')
    parser.add_argument('--extra', type=str, default="", help='Path to extra content file')
    parser.add_argument('--output', type=str, default="./onepage_generated.lark.md", help='Output file path')
    parser.add_argument('--title', type=str, required=True, help='Document title')
    parser.add_argument('--audience', type=str, default="", help='Target audience')
    parser.add_argument('--tone', type=str, default="专业精炼", help='Writing tone')
    parser.add_argument('--include_tables', type=bool, default=False, help='Include tables')

    args = parser.parse_args()
    generate_onepage(
        template=args.template,
        refs=args.refs,
        extra=args.extra,
        output=args.output,
        title=args.title,
        audience=args.audience,
        tone=args.tone,
        include_tables=args.include_tables
    )

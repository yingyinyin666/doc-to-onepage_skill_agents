#!/usr/bin/env python3
import argparse
import os
import json
import re

def parse_markdown(markdown_content):
    # 解析标题
    title_match = re.search(r'^#\s+(.*)$', markdown_content, re.MULTILINE)
    title = title_match.group(1) if title_match else ""

    # 按 ## 切分章节（用 split 代替 finditer，避免正则 $ 歧义）
    lines = markdown_content.split('\n')
    sections = {}
    current_section = None
    current_lines = []

    def flush_section(sec_title, sec_lines):
        if not sec_title:
            return
        content = '\n'.join(sec_lines).strip()
        # 尝试解析子章节
        subsections = {}
        cur_sub = None
        cur_sub_lines = []

        def flush_sub(sub_title, sub_lines):
            if sub_title:
                subsections[sub_title] = '\n'.join(sub_lines).strip()

        for line in sec_lines:
            if line.startswith('### '):
                flush_sub(cur_sub, cur_sub_lines)
                cur_sub = line[4:].strip()
                cur_sub_lines = []
            else:
                cur_sub_lines.append(line)
        flush_sub(cur_sub, cur_sub_lines)

        sections[sec_title] = subsections if subsections else content

    for line in lines:
        if line.startswith('## '):
            flush_section(current_section, current_lines)
            current_section = line[3:].strip()
            current_lines = []
        elif line.startswith('# '):
            pass  # 跳过文档标题行
        else:
            if current_section is not None:
                current_lines.append(line)

    flush_section(current_section, current_lines)

    return {
        "title": title,
        "sections": sections
    }

def main(onepage, template, output):
    # 加载onepage文件
    if not os.path.exists(onepage):
        raise FileNotFoundError(f"Onepage file {onepage} not found")
    
    with open(onepage, 'r', encoding='utf-8') as f:
        markdown_content = f.read()
    
    # 解析Markdown
    data = parse_markdown(markdown_content)
    data["template"] = template
    
    # 确保输出目录存在
    os.makedirs(os.path.dirname(output), exist_ok=True)
    
    # 写入JSON文件
    with open(output, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"JSON exported successfully: {output}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export Onepage to JSON")
    parser.add_argument('--onepage', type=str, required=True, help='Path to onepage file')
    parser.add_argument('--template', type=str, required=True, choices=[
        'decision-report',
        'product-solution',
        'project-progress',
        'governance-improvement',
        'holiday-support',
        'product-tool',
        'project-management',
        'team-intro',
        'personal-review'
    ], help='Template name')
    parser.add_argument('--output', type=str, default="./output/data.json", help='Output JSON file path')
    
    args = parser.parse_args()
    main(
        onepage=args.onepage,
        template=args.template,
        output=args.output
    )

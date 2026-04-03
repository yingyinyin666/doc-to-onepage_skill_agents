#!/usr/bin/env python3
import argparse
import os
import json
import re

def parse_markdown(markdown_content):
    # 解析标题
    title_match = re.search(r'^#\s+(.*)$', markdown_content, re.MULTILINE)
    title = title_match.group(1) if title_match else ""
    
    # 解析章节
    sections = {}
    section_pattern = re.compile(r'^##\s+(.*?)$\n(.*?)(?=^##\s+|$)', re.DOTALL | re.MULTILINE)
    
    for match in section_pattern.finditer(markdown_content):
        section_title = match.group(1).strip()
        section_content = match.group(2).strip()
        
        # 解析子章节
        subsections = {}
        subsection_pattern = re.compile(r'^###\s+(.*?)$\n(.*?)(?=^###\s+|^##\s+|$)', re.DOTALL | re.MULTILINE)
        
        for sub_match in subsection_pattern.finditer(section_content):
            sub_title = sub_match.group(1).strip()
            sub_content = sub_match.group(2).strip()
            subsections[sub_title] = sub_content
        
        # 如果没有子章节，直接使用内容
        if not subsections:
            sections[section_title] = section_content
        else:
            sections[section_title] = subsections
    
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
    parser.add_argument('--template', type=str, required=True, choices=['decision-report', 'product-solution', 'project-progress'], help='Template name')
    parser.add_argument('--output', type=str, default="./output/data.json", help='Output JSON file path')
    
    args = parser.parse_args()
    main(
        onepage=args.onepage,
        template=args.template,
        output=args.output
    )
